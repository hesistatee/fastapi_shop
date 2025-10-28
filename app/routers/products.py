from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.db_depends import get_db
from app.models import Product as ProductModel
from app.models.categories import Category
from app.schemas import Product, ProductCreate

router = APIRouter(
    prefix="/products",
    tags=["products"],
)


@router.get("/", response_model=list[Product])
async def get_all_products(session: Session = Depends(get_db)):
    """
    Возвращает список всех товаров.
    """
    products = (
        session.execute(select(ProductModel).where(ProductModel.is_active == True))
        .scalars()
        .all()
    )
    return products


@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_product(
    create_product: ProductCreate, session: Session = Depends(get_db)
):
    """
    Создаёт новый товар.
    """
    category_id = create_product.category_id
    category = session.scalars(
        select(Category).where(Category.id == category_id)
    ).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    product = ProductModel(**create_product.model_dump())
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


@router.get("/category/{category_id}", response_model=list[Product])
async def get_products_by_category(
    category_id: int, session: Session = Depends(get_db)
):
    """
    Возвращает список товаров в указанной категории по её ID.
    """
    category = session.scalars(
        select(Category).where(Category.id == category_id)
    ).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    products = session.scalars(
        select(ProductModel).where(
            ProductModel.category_id == category_id, ProductModel.is_active == True
        )
    ).all()
    return products


@router.get("/{product_id}", response_model=Product)
async def get_product(product_id: int, session: Session = Depends(get_db)):
    """
    Возвращает детальную информацию о товаре по его ID.
    """
    product = session.scalars(
        select(ProductModel).where(
            ProductModel.id == product_id, ProductModel.is_active == True
        )
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/{product_id}", response_model=Product)
async def update_product(
    product_id: int, product_update: ProductCreate, session: Session = Depends(get_db)
):
    """
    Обновляет товар по его ID.
    """
    product = session.scalars(
        select(ProductModel).where(
            ProductModel.id == product_id, ProductModel.is_active == True
        )
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    category = session.scalars(
        select(Category).where(
            Category.id == product_update.category_id, Category.is_active == True
        )
    ).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    product.name = product_update.name
    product.description = product_update.description
    product.price = product_update.price
    product.category_id = category.id
    session.commit()
    session.refresh(product)
    return product


@router.delete("/{product_id}")
async def delete_product(product_id: int, session: Session = Depends(get_db)):
    """
    Удаляет товар по его ID.
    """
    product = session.scalars(
        select(ProductModel).where(
            ProductModel.id == product_id, ProductModel.is_active == True
        )
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.is_active = False
    session.commit()
    session.refresh(product)
    return {"message": f"Товар {product_id} удалён"}
