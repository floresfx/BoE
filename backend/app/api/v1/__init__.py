from fastapi import APIRouter


from app.api.v1 import (
    access_logs,
    admin,
    auth,
    availability,
    bundles,
    catalogs,
    costing,
    production,
    movements,
    permissions,
    plans,
    profiles,
    purchase_requests,
    register,
    resources,
    resource_attributes,
    resource_taxes,
    roles,
    secure_devices,
    stock,
    subscription,
    suppliers,
    tenants,
    users,
    verticals,
    warehouses,
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
api_router.include_router(register.router)
api_router.include_router(subscription.router)
api_router.include_router(admin.router)
api_router.include_router(warehouses.router)
api_router.include_router(movements.router)
api_router.include_router(stock.router)
api_router.include_router(suppliers.router)
api_router.include_router(bundles.router)
api_router.include_router(purchase_requests.router)
api_router.include_router(availability.router)
api_router.include_router(costing.router)
api_router.include_router(production.router)