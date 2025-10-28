from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.categories import Category as CategoryModel
from app.schemas import Category as CategorySchema, CategoryCreate
from app.db_depends import get_db


router = APIRouter(
    prefix="/categories",
    tags=["categories"],
)


@router.get("/", response_model=list[CategorySchema], status_code=status.HTTP_200_OK)
async def get_all_categories(db: Session = Depends(get_db)):
    """
    Возвращает список всех категорий товаров.
    """
    stmt = select(CategoryModel).where(CategoryModel.is_active == True)
    categories = db.execute(stmt).scalars().all()
    return categories


@router.post("/", response_model=CategorySchema, status_code=status.HTTP_201_CREATED)
async def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """
    Создаёт новую категорию.
    """
    if category.parent_id:
        stmt = select(CategoryModel).where(
            CategoryModel.id == category.parent_id, CategoryModel.is_active == True
        )
        parent = db.execute(stmt).scalars().first()

        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent category not found",
            )

    db_category = CategoryModel(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@router.put("/{category_id}", response_model=CategorySchema)
async def update_category(
    category_id: int, category: CategoryCreate, db: Session = Depends(get_db)
):
    """
    Обновляет категорию по её ID.
    """
    db_category = (
        db.execute(
            select(CategoryModel).where(
                CategoryModel.id == category_id, CategoryModel.is_active == True
            )
        )
        .scalars()
        .first()
    )
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    if category.parent_id:
        parent = (
            db.execute(
                select(CategoryModel).where(
                    CategoryModel.parent_id == category.parent_id,
                    CategoryModel.is_active == True,
                )
            )
            .scalars()
            .first()
        )
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent category not found",
            )

    db.execute(
        update(CategoryModel)
        .where(CategoryModel.id == category_id)
        .values(**category.model_dump())
    )
    db.commit()
    db.refresh(db_category)
    return db_category


@router.delete("/{category_id}", status_code=status.HTTP_200_OK)
async def delete_category(category_id: int, db: Session = Depends(get_db)):
    """
    Удаляет категорию по её ID.
    """
    stmt = select(CategoryModel).where(
        CategoryModel.id == category_id, CategoryModel.is_active == True
    )
    category = db.execute(stmt).scalars().first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    db.execute(
        update(CategoryModel)
        .where(CategoryModel.id == category_id)
        .values(is_active=False)
    )
    db.commit()
    return {"message": f"Категория с ID {category_id} удалена"}
