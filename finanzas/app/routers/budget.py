from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..categories import ALL_CATEGORIES
from ..database import get_db
from ..models import Budget

router = APIRouter()


class BudgetSet(BaseModel):
    year: int
    month: int
    category: str
    amount: float


@router.get("/{year}/{month}")
def get_budget(year: int, month: int, db: Session = Depends(get_db)):
    rows = db.query(Budget).filter(Budget.year == year, Budget.month == month).all()
    return {r.category: r.amount for r in rows}


@router.post("/")
def set_budget(body: BudgetSet, db: Session = Depends(get_db)):
    if body.category not in ALL_CATEGORIES:
        raise HTTPException(status_code=400, detail="Categoría inválida")

    existing = (
        db.query(Budget)
        .filter(
            Budget.year == body.year,
            Budget.month == body.month,
            Budget.category == body.category,
        )
        .first()
    )
    if existing:
        existing.amount = body.amount
    else:
        db.add(Budget(year=body.year, month=body.month, category=body.category, amount=body.amount))
    db.commit()
    return {"ok": True}


@router.delete("/{year}/{month}/{category}")
def delete_budget(year: int, month: int, category: str, db: Session = Depends(get_db)):
    row = (
        db.query(Budget)
        .filter(Budget.year == year, Budget.month == month, Budget.category == category)
        .first()
    )
    if row:
        db.delete(row)
        db.commit()
    return {"ok": True}
