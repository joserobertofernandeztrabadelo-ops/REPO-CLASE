import calendar
import csv
import io
from datetime import date

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Account, Movement

router = APIRouter()


@router.get("/csv")
def export_csv(
    year: int = Query(...),
    month: int = Query(...),
    db: Session = Depends(get_db),
):
    last_day = calendar.monthrange(year, month)[1]
    movements = (
        db.query(Movement)
        .join(Account)
        .filter(
            Movement.date >= date(year, month, 1),
            Movement.date <= date(year, month, last_day),
        )
        .order_by(Movement.date)
        .all()
    )

    output = io.StringIO()
    writer = csv.writer(output, delimiter=";")
    writer.writerow(["Fecha", "Cuenta", "Descripción", "Concepto", "Categoría", "Importe", "Saldo"])
    for m in movements:
        writer.writerow(
            [
                m.date.strftime("%d/%m/%Y"),
                m.account.name,
                m.description,
                m.concepto or "",
                m.category,
                f"{m.amount:.2f}".replace(".", ","),
                f"{m.balance_after:.2f}".replace(".", ",") if m.balance_after is not None else "",
            ]
        )

    content = output.getvalue().encode("utf-8-sig")  # BOM for Excel
    return StreamingResponse(
        io.BytesIO(content),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=finanzas_{year}_{month:02d}.csv"},
    )
