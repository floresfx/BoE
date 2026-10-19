from pydantic import BaseModel


class TenantSettingsUpdate(BaseModel):
    inventory_costing_method: str | None = None