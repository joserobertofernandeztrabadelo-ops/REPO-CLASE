from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Date, DateTime, Boolean,
    ForeignKey, UniqueConstraint,
)
from sqlalchemy.orm import relationship
from .database import Base


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)   # caixabank | santander | revolut
    name = Column(String)
    balance = Column(Float, default=0.0)
    last_updated = Column(DateTime, default=datetime.utcnow)

    movements = relationship("Movement", back_populates="account", cascade="all, delete-orphan")


class Movement(Base):
    __tablename__ = "movements"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"))
    date = Column(Date, index=True)
    value_date = Column(Date, nullable=True)
    description = Column(String)
    concepto = Column(String, nullable=True)   # etiqueta manual de la hoja
    category = Column(String, index=True)
    amount = Column(Float)
    balance_after = Column(Float, nullable=True)
    notes = Column(String, nullable=True)
    is_manual = Column(Boolean, default=False)
    dedup_hash = Column(String, unique=True, index=True)
    import_batch = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    account = relationship("Account", back_populates="movements")


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, index=True)
    month = Column(Integer, index=True)
    category = Column(String)
    amount = Column(Float)

    __table_args__ = (
        UniqueConstraint("year", "month", "category", name="uq_budget_period_category"),
    )
