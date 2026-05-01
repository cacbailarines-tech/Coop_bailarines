# Cooperativa de Ahorro y Crédito "Bailarines" — Sistema v3

## Instalación
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
Abrir: http://localhost:8000

## Conectar una segunda base (Railway)
El sistema soporta una segunda conexión opcional (por ejemplo, otra base PostgreSQL en Railway).

- Variable requerida: `EXTERNAL_DATABASE_URL`
- Formato típico: `postgresql://USER:PASSWORD@HOST:PORT/DBNAME`

Notas:
- Si `EXTERNAL_DATABASE_URL` **no** está definida, el sistema funciona normal (solo `DATABASE_URL`).
- Las migraciones **no** se ejecutan en la base externa por seguridad.

## Usuarios
| Usuario  | Contraseña | Rol          |
|----------|-----------|--------------|
| admin    | admin123  | Administrador|
| cajero1  | cajero123 | Cajero       |

## Portal Socios
URL: http://localhost:8000/portal/
Cédula + PIN (los socios de demo tienen PIN: 1234)

## Módulos
- **Socios** — Registro con representante para menores, recomendados
- **Periodos** — Gestión anual (enero-diciembre)
- **Libretas** — Número continuo global, $22/mes ($20+$1+$1), inscripción $20
- **Verificar Aportes** — Socio reporta pago → admin verifica/rechaza
- **Créditos** — Mensualizado y No Mensualizado, tasa 5% mensual fija
  - Mensualizado: recibe monto completo - comisión, paga cuotas mensuales redondeadas arriba
  - No Mensualizado: recibe monto - interés adelantado - comisión, paga capital al final
  - Banco Pichincha: $0.50 comisión (todo beneficio cooperativa)
  - Otros bancos: $1.00 comisión ($0.41 cargo externo, $0.59 beneficio cooperativa)
- **Reuniones** — Registro de asistencia, generación automática de multas
  - Atraso 11-20 min: $1 por socio
  - Atraso 21+ min: $3 por socio
  - Falta justificada: $1 × libretas
  - Falta injustificada: $3 × libretas
  - Comportamiento inadecuado: $1 por socio
- **Multas** — Tipos configurables, por socio o por libreta
- **Rifa** — Registro mensual del resultado de lotería, $50 al ganador
- **Portal Socio** — Consulta de libretas, aportes, créditos y multas
- **Reportes** — Cartera, morosidad, ahorros, multas, aportes + exportación Excel
