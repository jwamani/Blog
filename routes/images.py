"""endpoints for file uploads and retrievals"""

"""
UploadFile: An abstraction over file uploads, provides metadata and file-like interface.
file: actual spooled file-like object, has size, content type, filename and size
extension comes from Path
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Header
# from fastapi.responses import JSONResponse

from typing import Annotated
from starlette import status
from pathlib import Path
import logging
import magic
import uuid
import shutil
# for large files
import aiofiles
import hashlib

from .posts import user_dependency
from .posts import db_dependency
from ..models import Image

image_router = APIRouter(prefix="/images", tags=["Images"])
logger = logging.getLogger(__name__)

# helpers
upload_dir = Path("uploads")
upload_dir.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif"}
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/gif"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


## VALIDATORS
def validate_file_extension(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def validate_content_type(content_type: str) -> bool:
    return content_type in ALLOWED_CONTENT_TYPES


async def validate_file_content(file: UploadFile) -> str:
    # first 2048 bytes for magic detection
    header = await file.read(2048)
    await file.seek(0)  # reset file position
    detected_type = magic.from_buffer(header, mime=True)

    if detected_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File content type '{detected_type}' is not allowed."
        )
    return detected_type


@image_router.post("/upload/validated/", status_code=status.HTTP_201_CREATED)
async def upload_validated_image(file: Annotated[UploadFile, File(description="Image file to upload")],
                                 db: db_dependency, user: user_dependency):
    user_id = user.get("id")
    try:
        if not validate_file_extension(file.filename):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file extension.")

        if not validate_content_type(file.content_type):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid content type.")

        detected_type = await validate_file_content(file)

        file_path = upload_dir / f"{uuid.uuid4()}{Path(file.filename).suffix.lower()}"

        with open(file_path, "wb") as buffer:
            total = 0
            while chunk := file.file.read(64 * 1024):
                total += len(chunk)
                if total > MAX_FILE_SIZE:
                    file_path.unlink(missing_ok=True)
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                        detail="File size exceeds the maximum limit.")
                buffer.write(chunk)

        img = Image(filename=file.filename, file_path=str(file_path.resolve()), file_size=file_path.stat().st_size,
                    content_type=detected_type, user_id=user_id)
        logger.info(f"Uploading validated image for user_id: {user_id}, filename: {file.filename}")
        try:
            db.add(img)
            db.commit()
            db.refresh(img)
        except Exception:
            file_path.unlink(missing_ok=True)
            raise

        return {
            "filename": img.filename,
            "content_type": img.content_type,
            "file_size": img.file_size,
            "message": "Image uploaded successfully"
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Failed to upload image: {str(e)}")
    finally:
        await file.close()


## FOR LARGE FILES

"""
upload file chunks for resumable uploads; large file is split and chunks uploaded separately with metadata. when all chunks arrive, the server reassembles them into the final file. 
Needs Headers:
    - X-Chunk-Number: current chunk index (0-based)
    - X-Total-Chunks: total number of chunks
    - X-File-ID: unique identifier for the upload session
"""

CHUNK_DIR = Path("chunks")
CHUNK_DIR.mkdir(exist_ok=True)


@image_router.post("/upload/chunk/", status_code=status.HTTP_202_ACCEPTED)
async def upload_chunk(
        file: Annotated[UploadFile, File(description="Chunk of the file to upload")],
        chunk_number: Annotated[int, Header(alias="X-Chunk-Number")],
        total_chunks: Annotated[int, Header(alias="X-Total-Chunks")],
        file_id: Annotated[str, Header(alias="X-File-ID")]
):
    # create dir for file's chunks
    file_dir = upload_dir / CHUNK_DIR / file_id
    file_dir.mkdir(exist_ok=True)

    chunk_path = file_dir / f"chunk_{chunk_number:05d}"  # save chunk
    async with aiofiles.open(chunk_path, "wb") as f:
        while chunk := await file.read(64 * 1024): # 64kb
            await f.write(chunk)
    logger.info(f"Uploaded chunk {chunk_number + 1}/{total_chunks} for file_id: {file_id}")
    await file.close()

    # check if all chunks are received
    received_chunks = list(file_dir.glob("chunk_*"))

    if len(received_chunks) == total_chunks:
        # reassemble file
        return await reassemble_file(file_id, total_chunks, file.filename)

    return {
        "status": "chunk_received",
        "chunk_number": chunk_number,
        "received": len(received_chunks),
        "total": total_chunks,
        "progress": f"{(len(received_chunks) / total_chunks) * 100:.1f}"
    }


async def reassemble_file(file_id: str, total_chunks: int, filename: str, /) -> dict:
    """
    Reassemble uploaded chunks into final file.
    Process:\n
    1. Sort chunks by number
    2. Open output file
    3. Append each chunk in order
    4. Calculate checksum for verification
    5. Clean up chunk files
    """
    file_dir =  upload_dir / CHUNK_DIR / file_id
    output_path = upload_dir / filename

    # md5 checksum
    hasher = hashlib.md5()

    total_size = 0

    async with aiofiles.open(output_path, "wb") as output_file:
        for i in range(total_chunks):
            chunk_path = file_dir / f"chunk_{i:05d}"

            async with aiofiles.open(chunk_path, "rb") as chunk_file:
                content = await chunk_file.read()
                await output_file.write(content)
                hasher.update(content)
                total_size += len(content)

    # clean up chunks
    shutil.rmtree(file_dir)

    return {
        "status": "complete",
        "filename": filename,
        "size": total_size,
        "md5": hasher.hexdigest(),
        "message": "File reassembled successfully"
    }

@image_router.get("/upload/chunk/status/{file_id}")
async def get_upload_status(file_id: str):
    """Check the status of a chunked upload."""
    file_chunk_dir = CHUNK_DIR / file_id
    if not file_chunk_dir.exists():
        raise HTTPException(status_code=404, detail="Upload session not found")
    received_chunks = sorted(file_chunk_dir.glob("chunk_*"))
    return {
        "file_id": file_id,
        "chunks_received": len(received_chunks),
        "chunks": [int(c.stem.split("_")[1]) for c in received_chunks]
    }
