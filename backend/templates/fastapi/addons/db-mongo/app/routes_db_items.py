# app/routes_db_items.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from bson import ObjectId

from app.db import get_db

router = APIRouter(tags=["db-items"])

class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = None

class ItemOut(BaseModel):
    id: str
    name: str
    description: Optional[str] = None

def to_item(doc) -> ItemOut:
    return ItemOut(
        id=str(doc["_id"]),
        name=doc["name"],
        description=doc.get("description"),
    )

@router.get("/", response_model=List[ItemOut])
async def list_items(db=Depends(get_db)):
    docs = await db["items"].find().to_list(length=1000)
    return [to_item(d) for d in docs]

@router.post("/", response_model=ItemOut, status_code=201)
async def create_item(payload: ItemCreate, db=Depends(get_db)):
    res = await db["items"].insert_one(payload.model_dump())
    doc = await db["items"].find_one({"_id": res.inserted_id})
    return to_item(doc)

@router.get("/{item_id}", response_model=ItemOut)
async def get_item(item_id: str, db=Depends(get_db)):
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=400, detail="Invalid id")
    doc = await db["items"].find_one({"_id": ObjectId(item_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Item not found")
    return to_item(doc)

@router.delete("/{item_id}", status_code=204)
async def delete_item(item_id: str, db=Depends(get_db)):
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=400, detail="Invalid id")
    res = await db["items"].delete_one({"_id": ObjectId(item_id)})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return
