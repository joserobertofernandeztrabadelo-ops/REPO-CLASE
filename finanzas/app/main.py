import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .database import engine
from . import models
from .categories import ALL_CATEGORIES, CATEGORY_META, EXTRA_PAY_MONTHS
from .routers import accounts, budget, export, movements, sheets

models.Base.metadata.create_all(bind=engine)

STATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "static")

app = FastAPI(title="Presupuesto Familiar", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(movements.router, prefix="/api/movements", tags=["movements"])
app.include_router(accounts.router, prefix="/api/accounts", tags=["accounts"])
app.include_router(budget.router, prefix="/api/budget", tags=["budget"])
app.include_router(sheets.router, prefix="/api/import", tags=["import"])
app.include_router(export.router, prefix="/api/export", tags=["export"])


@app.get("/api/categories")
def get_categories():
    return {
        "categories": ALL_CATEGORIES,
        "meta": CATEGORY_META,
        "extra_pay_months": list(EXTRA_PAY_MONTHS),
    }


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def root():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))
