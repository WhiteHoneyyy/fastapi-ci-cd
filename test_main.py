import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from database import Base, get_db
from main import app

# Используем ту же базу данных для тестов
DATABASE_URL = "sqlite+aiosqlite:///./recipes.db"
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncTestingSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def override_get_db() -> AsyncSession:
    async with AsyncTestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True, scope="function")
async def prepare_database():
    """Создает таблицы перед каждым тестом и удаляет после."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.anyio
async def test_recipes_crud_flow():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Тест создания рецепта
        response = await ac.post(
            "/recipes",
            json={
                "title": "Тестовая Паста",
                "cooking_time": 20,
                "ingredients": "Спагетти, пармезан",
                "description": "Отварить пасту."
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Тестовая Паста"
        recipe_id = data["id"]

        # Тест получения списка
        response = await ac.get("/recipes")
        assert response.status_code == 200
        assert len(response.json()) == 1

        # Тест получения конкретного рецепта
        response = await ac.get(f"/recipes/{recipe_id}")
        assert response.status_code == 200
        assert response.json()["title"] == "Тестовая Паста"

@pytest.mark.anyio
async def test_get_nonexistent_recipe():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/recipes/99999")
        assert response.status_code == 404
