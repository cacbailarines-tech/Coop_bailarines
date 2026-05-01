from __future__ import annotations

from django.conf import settings


class DatabaseRouter:
    """
    Router para soportar 2 conexiones:
    - default: base principal del sistema
    - external: base opcional (EXTERNAL_DATABASE_URL)

    Regla:
    - Solo se enruta a 'external' cuando el Model define `db_alias = "external"`.
    - Si no, todo queda en 'default' (comportamiento actual).
    """

    external_alias = "external"

    def _external_enabled(self) -> bool:
        return self.external_alias in getattr(settings, "DATABASES", {})

    def _wants_external(self, model) -> bool:
        return getattr(model, "db_alias", None) == self.external_alias

    def db_for_read(self, model, **hints):
        if self._external_enabled() and self._wants_external(model):
            return self.external_alias
        return None

    def db_for_write(self, model, **hints):
        if self._external_enabled() and self._wants_external(model):
            return self.external_alias
        return None

    def allow_relation(self, obj1, obj2, **hints):
        # Permite relaciones dentro del mismo alias; evita mezclas accidentalmente.
        a1 = getattr(getattr(obj1, "_state", None), "db", None)
        a2 = getattr(getattr(obj2, "_state", None), "db", None)
        if a1 and a2:
            return a1 == a2
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # Nunca migra automáticamente en la DB externa, para no destruir/alterar ese esquema.
        if db == self.external_alias:
            return False
        return None

