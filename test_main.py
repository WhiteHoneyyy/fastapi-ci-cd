import pytest
from httpx import ASGITransport, AsyncClient

from main import app


@pytest.mark.asyncio
async def test_recipes_crud_flow() -> None:
    """Тестирует создание рецепта, получение списка и детальный просмотр."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        payload = {
            "title": "Тестовая Паста",
            "cooking_time": 20,
            "ingredients": "Спагетти, пармезан",
            "description": "Отварить пасту.",
        }
        create_resp = await ac.post("/recipes", json=payload)
        assert create_resp.status_code == 201
        data = create_resp.json()
        assert data["title"] == payload["title"]
        recipe_id = data["id"]

        list_resp = await ac.get("/recipes")
        assert list_resp.status_code == 200

        detail_resp = await ac.get(f"/recipes/{recipe_id}")
        assert detail_resp.status_code == 200
        assert detail_resp.json()["views_count"] == 1


@pytest.mark.asyncio
async def test_get_nonexistent_recipe() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/recipes/99999")
        assert response.status_code == 404
