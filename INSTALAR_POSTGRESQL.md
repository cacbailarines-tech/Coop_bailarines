# Guía de Instalación con PostgreSQL
## Cooperativa de Ahorro y Crédito Bailarines

---

## PASO 1 — Instalar PostgreSQL en Windows

1. Descargar: https://www.postgresql.org/download/windows/
2. Ejecutar el instalador (versión 15 o 16 recomendada)
3. Durante la instalación:
   - Puerto: **5432** (dejar por defecto)
   - Contraseña del superusuario: anota la que pongas
   - Dejar marcado **pgAdmin 4** (herramienta visual)

---

## PASO 2 — Crear la base de datos

Opción A — Con pgAdmin (más fácil):
1. Abrir pgAdmin 4
2. Expandir Servers > PostgreSQL > Databases
3. Click derecho en Databases > Create > Database
4. Name: `bailarines`
5. Guardar

Opción B — Con psql (terminal):
```
psql -U postgres
CREATE DATABASE bailarines ENCODING 'UTF8';
\q
```

---

## PASO 3 — Cargar los datos

Con pgAdmin:
1. Click derecho en la base `bailarines` > Restore
2. Seleccionar el archivo `bailarines_postgresql.sql`
3. En Options > marcar "Only data" desactivado
4. Click Restore

Con psql:
```
psql -U postgres -d bailarines -f bailarines_postgresql.sql
```

---

## PASO 4 — Configurar el sistema

Editar el archivo `cooperativa_bailarines/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME':     'bailarines',
        'USER':     'postgres',
        'PASSWORD': 'TU_CONTRASEÑA_AQUI',  # ← Cambiar esto
        'HOST':     'localhost',
        'PORT':     '5432',
    }
}
```

---

## PASO 5 — Instalar dependencias y ejecutar

```powershell
cd cooperativa_bailarines_v3
pip install -r requirements.txt
python manage.py runserver
```

Abrir: http://localhost:8000

---

## Usuarios del sistema
| Usuario  | Contraseña | Rol          |
|----------|-----------|--------------|
| admin    | admin123  | Administrador|
| cajero1  | cajero123 | Cajero       |

## Portal del socio: http://localhost:8000/portal/
(Cédula + PIN 1234 para los socios de demo)

---

## ¿Problemas?

**Error "could not connect"**: Verificar que PostgreSQL esté corriendo.
En Windows: Buscar "Services" > PostgreSQL > Start

**Error de contraseña**: Revisar el `settings.py` que tenga la contraseña correcta.

**Error de módulo psycopg2**: Ejecutar `pip install psycopg2-binary`
