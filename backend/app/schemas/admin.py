"""Schemas para el panel de administración del SaaS.

Los schemas de Create/Update son deliberadamente simples: usan
Pydantic para validar los datos antes de insertarlos.
"""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Vertical
# ---------------------------------------------------------------------------

class VerticalAdminCreate(BaseModel):
    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=255)
    is_active: bool = True


class VerticalAdminUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, min_length=1, max_length=255)
    is_active: bool | None = None


# ---------------------------------------------------------------------------
# Feature
# ---------------------------------------------------------------------------

class FeatureAdminCreate(BaseModel):
    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=255)
    applies_to: str = Field(..., pattern="^(mpr|marketplace|both)$")
    is_active: bool = True


class FeatureAdminUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, min_length=1, max_length=255)
    applies_to: str | None = Field(None, pattern="^(mpr|marketplace|both)$")
    is_active: bool | None = None


# ---------------------------------------------------------------------------
# Plan
# ---------------------------------------------------------------------------

class PlanAdminCreate(BaseModel):
    code: str = Field(..., min_length=1, max_length=30)
    name: str = Field(..., min_length=1, max_length=50)
    price: Decimal = Field(..., ge=0)
    currency_id: UUID
    interval: str = Field(..., pattern="^(monthly|quarterly|yearly)$")
    trial_days: int = Field(0, ge=0, le=90)
    is_active: bool = True
    feature_codes: list[str] = Field(default_factory=list)
    limits: dict[str, int | None] = Field(default_factory=dict)


class PlanAdminUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=50)
    price: Decimal | None = Field(None, ge=0)
    currency_id: UUID | None = None
    interval: str | None = Field(None, pattern="^(monthly|quarterly|yearly)$")
    trial_days: int | None = Field(None, ge=0, le=90)
    is_active: bool | None = None
    feature_codes: list[str] | None = None
    limits: dict[str, int | None] | None = None


# ---------------------------------------------------------------------------
# Attribute
# ---------------------------------------------------------------------------

class AttributeAdminCreate(BaseModel):
    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)
    type_code: str = Field(..., min_length=1, max_length=30)
    is_active: bool = True


class AttributeAdminUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    type_code: str | None = Field(None, min_length=1, max_length=30)
    is_active: bool | None = None


# ---------------------------------------------------------------------------
# Tax
# ---------------------------------------------------------------------------

class TaxAdminCreate(BaseModel):
    country_code: str = Field(..., min_length=2, max_length=2)
    code: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=1, max_length=50)
    rate: Decimal = Field(..., ge=0, le=100)
    applies_to: str = Field(..., min_length=1, max_length=50)
    is_active: bool = True


class TaxAdminUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=50)
    rate: Decimal | None = Field(None, ge=0, le=100)
    applies_to: str | None = Field(None, min_length=1, max_length=50)
    is_active: bool | None = None


# ---------------------------------------------------------------------------
# ServiceTemplate
# ---------------------------------------------------------------------------

class ServiceTemplateAdminCreate(BaseModel):
    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=255)
    category_id: UUID | None = None
    is_active: bool = True


class ServiceTemplateAdminUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, min_length=1, max_length=255)
    category_id: UUID | None = None
    is_active: bool | None = None


# ---------------------------------------------------------------------------
# Currency
# ---------------------------------------------------------------------------

class CurrencyAdminCreate(BaseModel):
    code: str = Field(..., min_length=1, max_length=10)
    name: str = Field(..., min_length=1, max_length=100)
    symbol: str = Field(..., min_length=1, max_length=10)
    decimals: int = Field(2, ge=0, le=8)
    is_base: bool = False
    is_active: bool = True


class CurrencyAdminUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    symbol: str | None = Field(None, min_length=1, max_length=10)
    decimals: int | None = Field(None, ge=0, le=8)
    is_active: bool | None = None


# ---------------------------------------------------------------------------
# Unit
# ---------------------------------------------------------------------------

class UnitAdminCreate(BaseModel):
    code: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=1, max_length=50)
    symbol: str = Field(..., min_length=1, max_length=10)
    category_id: UUID
    is_base: bool = False
    is_active: bool = True


class UnitAdminUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=50)
    symbol: str | None = Field(None, min_length=1, max_length=10)
    is_base: bool | None = None
    is_active: bool | None = None


# ---------------------------------------------------------------------------
# Category
# ---------------------------------------------------------------------------

class CategoryAdminCreate(BaseModel):
    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)
    is_active: bool = True


class CategoryAdminUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    is_active: bool | None = None


# ---------------------------------------------------------------------------
# Country
# ---------------------------------------------------------------------------

class CountryAdminCreate(BaseModel):
    code: str = Field(..., min_length=2, max_length=2)
    name: str = Field(..., min_length=1, max_length=100)
    timezone_id: UUID
    currency_id: UUID
    phone_prefix: str = Field(..., min_length=1, max_length=5)
    is_active: bool = True


class CountryAdminUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    phone_prefix: str | None = Field(None, min_length=1, max_length=5)
    is_active: bool | None = None


# ---------------------------------------------------------------------------
# DocumentType
# ---------------------------------------------------------------------------

class DocumentTypeAdminCreate(BaseModel):
    code: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=1, max_length=50)
    country_id: UUID | None = None
    format: str | None = None
    regex: str | None = None
    is_active: bool = True


class DocumentTypeAdminUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=50)
    format: str | None = None
    regex: str | None = None
    is_active: bool | None = None