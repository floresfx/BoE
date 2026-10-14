from app.schemas.access_log import (
    AccessLogCreate,
    AccessLogResponse,
)
from app.schemas.common import (
    BaseSchema,
    ErrorResponse,
    MessageResponse,
    TimestampSchema,
    UUIDResponse,
)
from app.schemas.permission import (
    PermissionCreate,
    PermissionResponse,
    PermissionUpdate,
)
from app.schemas.plan import (
    PlanCreate,
    PlanResponse,
    PlanUpdate,
)
from app.schemas.profile import (
    ProfileCreate,
    ProfileResponse,
    ProfileUpdate,
)
from app.schemas.role import (
    RoleCreate,
    RoleResponse,
    RoleUpdate,
)
from app.schemas.secure_device import (
    SecureDeviceCreate,
    SecureDeviceResponse,
)
from app.schemas.tenant import (
    TenantCreate,
    TenantListResponse,
    TenantResponse,
    TenantUpdate,
)
from app.schemas.user import (
    UserCreate,
    UserListResponse,
    UserLogin,
    UserLoginResponse,
    UserResponse,
    UserUpdate,
)
from app.schemas.vertical import (
    VerticalCreate,
    VerticalResponse,
    VerticalUpdate,
)
from app.schemas.resource import (
    ResourceAttributeInline,
    ResourceAttributeResponse,
    ResourceCreate,
    ResourceListResponse,
    ResourceResponse,
    ResourceTaxInline,
    ResourceTaxResponse,
    ResourceUpdate,
)
from app.schemas.resource_attribute import (
    ResourceAttributeCreate,
    ResourceAttributeUpdate,
    ResourceAttributeResponse as ResourceAttributeResponseStandalone,
)
from app.schemas.resource_tax import (
    ResourceTaxCreate,
    ResourceTaxResponse as ResourceTaxResponseStandalone,
)



__all__ = [
    "BaseSchema",
    "TimestampSchema",
    "UUIDResponse",
    "MessageResponse",
    "ErrorResponse",
    "TenantCreate",
    "TenantUpdate",
    "TenantResponse",
    "TenantListResponse",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserListResponse",
    "UserLogin",
    "UserLoginResponse",
    "RoleCreate",
    "RoleUpdate",
    "RoleResponse",
    "ProfileCreate",
    "ProfileUpdate",
    "ProfileResponse",
    "PermissionCreate",
    "PermissionUpdate",
    "PermissionResponse",
    "SecureDeviceCreate",
    "SecureDeviceResponse",
    "AccessLogCreate",
    "AccessLogResponse",
    "VerticalCreate",
    "VerticalUpdate",
    "VerticalResponse",
    "PlanCreate",
    "PlanUpdate",
    "PlanResponse",
    # Resource
    "ResourceAttributeInline",
    "ResourceAttributeResponse",
    "ResourceCreate",
    "ResourceListResponse",
    "ResourceResponse",
    "ResourceTaxInline",
    "ResourceTaxResponse",
    "ResourceUpdate",
    # ResourceAttribute (endpoint dedicado)
    "ResourceAttributeCreate",
    "ResourceAttributeUpdate",
    "ResourceAttributeResponseStandalone",
    # ResourceTax (endpoint dedicado)
    "ResourceTaxCreate",
    "ResourceTaxResponseStandalone",
]