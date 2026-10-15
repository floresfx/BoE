from app.models.access_log import AccessLog
from app.models.base import Base
from app.models.base_tenant import TenantBase
from app.models.operational import (
    Movement,
    MOVEMENT_TYPES,
    Resource,
    RESOURCE_TYPES,
    ResourceAttribute,
    ResourceTax,
    StockLot,
    Warehouse,
)
from app.models.permission import Permission, RolePermission
from app.models.plan import Plan
from app.models.profile import Profile, UserProfile
from app.models.role import Role
from app.models.secure_device import SecureDevice
from app.models.tenant import Tenant
from app.models.user import User
from app.models.user_role import UserRole
from app.models.vertical import Vertical
from app.models.plan_feature import PlanFeature
from app.models.plan_limit import PlanLimit


# Catalogos simples (Bloque 1)
from app.models.catalogs import (
    AttributeType,
    Currency,
    DateFormat,
    NumberFormat,
    Timezone,
)

# Catalogos Bloque 2
from app.models.catalogs import (
    Attribute,
    Category,
    Subcategory,
    Unit,
    UnitCategory,
    UnitConversion,
    VerticalAttribute,
)

# Catalogos Bloque 3
from app.models.catalogs import (
    Feature,
    FeatureDependency,
)

# Geografia (Bloque 4)
from app.models.geo import (
    City,
    Country,
    DocumentType,
    State,
    Tax,
)

# Servicios (Bloque 5)
from app.models.services import (
    ServiceTemplate,
    VerticalService,
)

__all__ = [
    "AccessLog",
    "Base",
    "Permission",
    "Plan",
    "Profile",
    "RESOURCE_TYPES",
    "Resource",
    "Role",
    "RolePermission",
    "SecureDevice",
    "Tenant",
    "TenantBase",
    "User",
    "UserProfile",
    "UserRole",
    "Vertical",
    # Catalogos Bloque 1
    "AttributeType",
    "Currency",
    "DateFormat",
    "NumberFormat",
    "Timezone",
    # Catalogos Bloque 2
    "Attribute",
    "Category",
    "Subcategory",
    "Unit",
    "UnitCategory",
    "UnitConversion",
    "VerticalAttribute",
    # Catalogos Bloque 3
    "Feature",
    "FeatureDependency",
    # Geografia (Bloque 4)
    "City",
    "Country",
    "DocumentType",
    "State",
    "Tax",
    # Servicios (Bloque 5)
    "ServiceTemplate",
    "VerticalService",
    "PlanFeature",
    "PlanLimit",
    "RESOURCE_TYPES",
    "Resource",
    "ResourceAttribute",
    "ResourceTax",
    "Movement",
    "MOVEMENT_TYPES",
    "StockLot",
    "Warehouse",
]