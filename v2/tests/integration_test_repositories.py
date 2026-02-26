import pytest

from v2.src.domain.entities.user import User
from v2.src.domain.entities.post import Post


@pytest.mark.asyncio
class TestUserRepository:
    async def test_create_user(self, user_repo, password_hasher):
        """Test creating a user."""
        user = User(
            id=None,
            username="testuser",
            email="test@example.com",
            hashed_password=password_hasher.hash("password123")
        )
        created_user = await user_repo.create(user)

        assert created_user.id is not None
        assert created_user.username == "testuser"
        assert created_user.email == "test@example.com"

    async def test_get_user_by_id(self, user_repo, password_hasher):
        """Test retrieving a user by ID."""
        user = User(
            id=None,
            username="testuser",
            email="test@example.com",
            hashed_password=password_hasher.hash("password123")
        )
        created_user = await user_repo.create(user)
        retrieved_user = await user_repo.get_by_id(created_user.id)

        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id

    async def test_get_user_by_email(self, user_repo, password_hasher):
        """Test retrieving a user by email."""
        user = User(
            id=None,
            username="testuser",
            email="test@example.com",
            hashed_password=password_hasher.hash("password123")
        )
        await user_repo.create(user)
        retrieved_user = await user_repo.get_by_email("test@example.com")

        assert retrieved_user is not None
        assert retrieved_user.email == "test@example.com"

    async def test_get_user_by_email_not_found(self, user_repo):
        """Test retrieving non-existent user by email."""
        retrieved_user = await user_repo.get_by_email("nonexistent@example.com")

        assert retrieved_user is None

    async def test_update_user(self, user_repo, password_hasher):
        """Test updating a user."""
        user = User(
            id=None,
            username="testuser",
            email="test@example.com",
            hashed_password=password_hasher.hash("password123")
        )
        created_user = await user_repo.create(user)
        
        # Update username
        created_user.username = "updateduser"
        updated_user = await user_repo.update(created_user)

        assert updated_user.username == "updateduser"

    async def test_delete_user(self, user_repo, password_hasher):
        """Test deleting a user."""
        user = User(
            id=None,
            username="testuser",
            email="test@example.com",
            hashed_password=password_hasher.hash("password123")
        )
        created_user = await user_repo.create(user)
        deleted = await user_repo.delete(created_user.id)

        assert deleted is True
        retrieved_user = await user_repo.get_by_id(created_user.id)
        assert retrieved_user is None


@pytest.mark.asyncio
class TestPostRepository:
    async def test_create_post(self, post_repo, user_repo, password_hasher):
        """Test creating a post."""
        # Create a user first
        user = User(
            id=None,
            username="testuser",
            email="test@example.com",
            hashed_password=password_hasher.hash("password123")
        )
        created_user = await user_repo.create(user)

        # Create a post
        post = Post(
            id=None,
            title="Test Post",
            content="This is a test post with sufficient content",
            author_id=created_user.id
        )
        created_post = await post_repo.create(post)

        assert created_post.id is not None
        assert created_post.title == "Test Post"
        assert created_post.author_id == created_user.id

    async def test_get_post_by_id(self, post_repo, user_repo, password_hasher):
        """Test retrieving a post by ID."""
        # Create a user and post
        user = User(
            id=None,
            username="testuser",
            email="test@example.com",
            hashed_password=password_hasher.hash("password123")
        )
        created_user = await user_repo.create(user)

        post = Post(
            id=None,
            title="Test Post",
            content="This is a test post with sufficient content",
            author_id=created_user.id
        )
        created_post = await post_repo.create(post)

        retrieved_post = await post_repo.get_by_id(created_post.id)
        assert retrieved_post is not None
        assert retrieved_post.id == created_post.id

    async def test_get_posts_by_author_id(self, post_repo, user_repo, password_hasher):
        """Test retrieving all posts by author."""
        # Create a user
        user = User(
            id=None,
            username="testuser",
            email="test@example.com",
            hashed_password=password_hasher.hash("password123")
        )
        created_user = await user_repo.create(user)

        # Create posts
        post1 = Post(
            id=None,
            title="Post 1",
            content="Content 1 with sufficient length",
            author_id=created_user.id
        )
        post2 = Post(
            id=None,
            title="Post 2",
            content="Content 2 with sufficient length",
            author_id=created_user.id
        )
        await post_repo.create(post1)
        await post_repo.create(post2)

        posts = await post_repo.get_by_author_id(created_user.id)
        assert len(posts) == 2

    async def test_update_post(self, post_repo, user_repo, password_hasher):
        """Test updating a post."""
        # Create a user and post
        user = User(
            id=None,
            username="testuser",
            email="test@example.com",
            hashed_password=password_hasher.hash("password123")
        )
        created_user = await user_repo.create(user)

        post = Post(
            id=None,
            title="Test Post",
            content="This is a test post with sufficient content",
            author_id=created_user.id
        )
        created_post = await post_repo.create(post)

        # Update title
        created_post.title = "Updated Title"
        updated_post = await post_repo.update(created_post)

        assert updated_post.title == "Updated Title"

    async def test_delete_post(self, post_repo, user_repo, password_hasher):
        """Test deleting a post."""
        # Create a user and post
        user = User(
            id=None,
            username="testuser",
            email="test@example.com",
            hashed_password=password_hasher.hash("password123")
        )
        created_user = await user_repo.create(user)

        post = Post(
            id=None,
            title="Test Post",
            content="This is a test post with sufficient content",
            author_id=created_user.id
        )
        created_post = await post_repo.create(post)

        deleted = await post_repo.delete(created_post.id)
        assert deleted is True

        retrieved_post = await post_repo.get_by_id(created_post.id)
        assert retrieved_post is None
