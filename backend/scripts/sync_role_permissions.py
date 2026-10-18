"""Sincroniza los permisos de los roles por defecto (Admin, Editor, Lector).

Idempotente: puedes correrlo múltiples veces.

Matriz de permisos:
- Admin: todos (crear, editar, eliminar, ver)
- Editor: crear, editar, ver (no eliminar)
- Lector: ver (solo lectura)
- SuperAdmin: todos
"""

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models import Permission, Role, RolePermission


# Matriz de permisos por rol
ROLE_PERMISSIONS = {
    "Admin": "all",
    "Editor": ["crear", "editar", "ver"],
    "Lector": ["ver"],
    "SuperAdmin": "all",
}


def sync_role_permissions(db: Session) -> dict[str, int]:
    """Sincroniza permisos de roles. Devuelve {role_name: total_permisos}."""
    all_perms = db.query(Permission).all()
    result: dict[str, int] = {}

    for role_name, actions in ROLE_PERMISSIONS.items():
        role = db.query(Role).filter(Role.name == role_name).first()
        if not role:
            result[role_name] = -1
            continue

        # Permisos actuales del rol
        current_ids = {
            rp.permission_id
            for rp in db.query(RolePermission).filter(
                RolePermission.role_id == role.id
            ).all()
        }

        # Permisos deseados
        if actions == "all":
            desired = {p.id for p in all_perms}
        else:
            desired = {p.id for p in all_perms if p.action in actions}

        # Añadir los que falten
        for perm_id in desired - current_ids:
            db.add(RolePermission(role_id=role.id, permission_id=perm_id))

        # Quitar los que sobren
        for perm_id in current_ids - desired:
            rp = db.query(RolePermission).filter(
                RolePermission.role_id == role.id,
                RolePermission.permission_id == perm_id,
            ).first()
            if rp:
                db.delete(rp)

        result[role_name] = len(desired)

    db.flush()
    return result


if __name__ == "__main__":
    db = SessionLocal()
    try:
        res = sync_role_permissions(db)
        db.commit()
        print("✅ Roles sincronizados:")
        for role, total in res.items():
            if total == -1:
                print(f"  ⚠️  {role}: no existe")
            else:
                print(f"  ✅ {role}: {total} permisos")
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()