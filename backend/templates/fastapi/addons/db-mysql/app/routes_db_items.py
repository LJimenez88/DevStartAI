from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .db import Item as ItemModel
from .db import get_db

router = APIRouter(tags=["db-items"])


# ---------------------------------------------------------
# Pydantic models for API
# ---------------------------------------------------------
class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: int

    class Config:
        orm_mode = True


# ---------------------------------------------------------
# Routes under /db/items (mounted in main.py)
# ---------------------------------------------------------
@router.get("/", response_model=List[Item])
def list_items(db: Session = Depends(get_db)):
    return db.query(ItemModel).order_by(ItemModel.id.asc()).all()


@router.post("/", response_model=Item, status_code=201)
def create_item(payload: ItemCreate, db: Session = Depends(get_db)):
    db_item = ItemModel(name=payload.name, description=payload.description)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.get("/{item_id}", response_model=Item)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return
