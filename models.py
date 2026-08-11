from sqlalchemy import Column, Integer, String, Text

from database import Base


class Recipe(Base):
    """Модель рецепта кулинарной книги."""

    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    cooking_time = Column(Integer, nullable=False)
    views_count = Column(Integer, default=0, nullable=False)
    ingredients = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
