from fastapi import APIRouter

from app.api.v1 import (
    access_logs,
    auth,
    catalogs,
    permissions,
    plans,
    profiles,
    resources,
    resource_attributes,
    resource_taxes,
    roles,
    secure_devices,
    tenants,
    users,
    verticals,
)

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(catalogs.router)
api_router.include_router(tenants.router)
api_router.include_router(users.router)
api_router.include_router(roles.router)
api_router.include_router(profiles.router)
api_router.include_router(permissions.router)
api_router.include_router(secure_devices.router)
api_router.include_router(access_logs.router)
api_router.include_router(verticals.router)
api_router.include_router(plans.router)
api_router.include_router(resources.router)
api_router.include_router(resource_attributes.router)
api_router.include_router(resource_taxes.router)
api_router.include_router(catalogs.router)