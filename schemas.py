from pydantic import BaseModel, ConfigDict, Field


class RecipeBase(BaseModel):
    title: str = Field(..., description="Название блюда")
    cooking_time: int = Field(..., gt=0, description="Время приготовления")
    ingredients: str = Field(..., description="Список ингредиентов")
    description: str = Field(..., description="Текстовое описание")


class RecipeCreate(RecipeBase):
    pass


class RecipeListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    views_count: int
    cooking_time: int


class RecipeDetailResponse(RecipeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    views_count: int
