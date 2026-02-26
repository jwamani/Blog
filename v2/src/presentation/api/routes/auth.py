from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from v2.src.presentation.api.dependencies import get_create_user_use_case, get_authenticate_user_use_case, get_jwt_handler
from v2.src.presentation.api.schemas.user_schema import UserCreate, UserResponse
from v2.src.application.use_cases.user.create_user import CreateUserUseCase
from v2.src.application.use_cases.user.authenticate_user import AuthenticateUserUseCase
from v2.src.infrastructure.security.jwt_handler import JWTHandler

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse)
async def register_user(
    user_data: UserCreate,
    use_case: CreateUserUseCase = Depends(get_create_user_use_case)
):
    try:
        user = await use_case.execute(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            phone_number=user_data.phone_number
        )
        return UserResponse.from_entity(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    use_case: AuthenticateUserUseCase = Depends(get_authenticate_user_use_case),
    jwt_handler: JWTHandler = Depends(get_jwt_handler)
):
    try:
        user = await use_case.execute(form_data.username, form_data.password)
        token = jwt_handler.create_access_token({"sub": user.username, "user_id": user.id})
        return {"access_token": token, "token_type": "bearer"}
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid credentials")