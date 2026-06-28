import calendar
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Account, Movement

router = APIRouter()


@router.get("/")
def list_accounts(db: Session = Depends(get_db)):
    accounts = db.query(Account).all()
    return [
        {
            "id": a.id,
            "code": a.code,
            "name": a.name,
            "balance": a.balance,
            "last_updated": a.last_updated.isoformat() if a.last_updated else None,
            "movement_count": db.query(Movement).filter(Movement.account_id == a.id).count(),
        }
        for a in accounts
    ]


@router.get("/{code}/movements")
def account_movements(
    code: str,
    year: Optional[int] = None,
    month: Optional[int] = None,
    db: Session = Depends(get_db),
):
    account = db.query(Account).filter(Account.code == code).first()
    if not account:
        return {"account": None, "movements": []}

    q = db.query(Movement).filter(Movement.account_id == account.id)

    if year and month:
        last_day = calendar.monthrange(year, month)[1]
        q = q.filter(
            Movement.date >= date(year, month, 1),
            Movement.date <= date(year, month, last_day),
        )

    movements = q.order_by(Movement.date.desc()).all()
    return {
        "account": {"code": account.code, "name": account.name, "balance": account.balance},
        "movements": [
            {
                "id": m.id,
                "date": m.date.isoformat(),
                "description": m.description,
                "concepto": m.concepto,
                "category": m.category,
                "amount": m.amount,
                "balance_after": m.balance_after,
            }
            for m in movements
        ],
    }
