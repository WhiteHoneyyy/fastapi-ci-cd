from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import asc, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import Base, engine, get_db
from models import Recipe
from schemas import RecipeCreate, RecipeDetailResponse, RecipeListResponse


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Автоматическое создание таблиц при старте."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="Кулинарная книга API", lifespan=lifespan)


@app.get("/recipes", response_model=list[RecipeListResponse])
async def get_recipes(db: AsyncSession = Depends(get_db)) -> Any:
    stmt = select(Recipe).order_by(
        desc(Recipe.views_count), asc(Recipe.cooking_time)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@app.get("/recipes/{recipe_id}", response_model=RecipeDetailResponse)
async def get_recipe_detail(
    recipe_id: int, db: AsyncSession = Depends(get_db)
) -> Any:
    stmt = select(Recipe).where(Recipe.id == recipe_id)
    result = await db.execute(stmt)
    recipe = result.scalar_one_or_none()

    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Рецепт с id={recipe_id} не найден.",
        )

    recipe.views_count += 1
    await db.commit()
    await db.refresh(recipe)
    return recipe


@app.post(
    "/recipes",
    response_model=RecipeDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_recipe(
    recipe_in: RecipeCreate, db: AsyncSession = Depends(get_db)
) -> Any:
    new_recipe = Recipe(**recipe_in.model_dump())
    db.add(new_recipe)
    await db.commit()
    await db.refresh(new_recipe)
    return new_recipe
