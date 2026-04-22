-- Cooperativa de Ahorro y Crédito "Bailarines" — PostgreSQL
-- Generado: 2026-04-11 09:44
-- Uso: psql -U postgres -d bailarines < bailarines_postgresql.sql
SET client_encoding = 'UTF8'; SET standard_conforming_strings = on;

CREATE TABLE IF NOT EXISTS "auth_group" (
    "id" SERIAL PRIMARY KEY,
    "name" VARCHAR(150) NOT NULL
);

CREATE TABLE IF NOT EXISTS "auth_group_permissions" (
    "id" SERIAL PRIMARY KEY,
    "group_id" INTEGER NOT NULL,
    "permission_id" INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS "auth_permission" (
    "id" SERIAL PRIMARY KEY,
    "content_type_id" INTEGER NOT NULL,
    "codename" VARCHAR(100) NOT NULL,
    "name" VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS "auth_user" (
    "id" SERIAL PRIMARY KEY,
    "password" VARCHAR(128) NOT NULL,
    "last_login" TIMESTAMP WITH TIME ZONE,
    "is_superuser" BOOLEAN NOT NULL,
    "username" VARCHAR(150) NOT NULL,
    "last_name" VARCHAR(150) NOT NULL,
    "email" VARCHAR(254) NOT NULL,
    "is_staff" BOOLEAN NOT NULL,
    "is_active" BOOLEAN NOT NULL,
    "date_joined" TIMESTAMP WITH TIME ZONE NOT NULL,
    "first_name" VARCHAR(150) NOT NULL
);

CREATE TABLE IF NOT EXISTS "auth_user_groups" (
    "id" SERIAL PRIMARY KEY,
    "user_id" INTEGER NOT NULL,
    "group_id" INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS "auth_user_user_permissions" (
    "id" SERIAL PRIMARY KEY,
    "user_id" INTEGER NOT NULL,
    "permission_id" INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS "core_movimiento" (
    "id" SERIAL PRIMARY KEY,
    "tipo" VARCHAR(10) NOT NULL,
    "categoria" VARCHAR(30) NOT NULL,
    "descripcion" VARCHAR(300) NOT NULL,
    "monto" NUMERIC NOT NULL,
    "fecha" DATE NOT NULL,
    "origen" VARCHAR(15) NOT NULL,
    "comprobante" VARCHAR(200) NOT NULL,
    "socio_ref" VARCHAR(200) NOT NULL,
    "libreta_ref" VARCHAR(50) NOT NULL,
    "credito_ref" VARCHAR(50) NOT NULL,
    "fecha_registro" TIMESTAMP WITH TIME ZONE NOT NULL,
    "observaciones" TEXT NOT NULL,
    "registrado_por_id" INTEGER
);

CREATE TABLE IF NOT EXISTS "core_perfilusuario" (
    "id" SERIAL PRIMARY KEY,
    "rol" VARCHAR(20) NOT NULL,
    "telefono" VARCHAR(15) NOT NULL,
    "usuario_id" INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS "creditos_credito" (
    "id" SERIAL PRIMARY KEY,
    "numero" VARCHAR(20) NOT NULL,
    "tipo" VARCHAR(20) NOT NULL,
    "monto_solicitado" NUMERIC NOT NULL,
    "plazo_meses" INTEGER NOT NULL,
    "banco" VARCHAR(30) NOT NULL,
    "numero_cuenta_bancaria" VARCHAR(50) NOT NULL,
    "titular_cuenta" VARCHAR(200) NOT NULL,
    "cedula_titular" VARCHAR(13) NOT NULL,
    "tasa_mensual" NUMERIC NOT NULL,
    "interes_total" NUMERIC NOT NULL,
    "comision_bancaria" NUMERIC NOT NULL,
    "beneficio_transferencia" NUMERIC NOT NULL,
    "monto_transferir" NUMERIC NOT NULL,
    "cuota_mensual" NUMERIC NOT NULL,
    "monto_pago_final" NUMERIC NOT NULL,
    "saldo_pendiente" NUMERIC NOT NULL,
    "estado" VARCHAR(20) NOT NULL,
    "fecha_solicitud" TIMESTAMP WITH TIME ZONE NOT NULL,
    "fecha_aprobacion" DATE,
    "fecha_desembolso" DATE,
    "fecha_pago_limite" DATE,
    "observaciones" TEXT NOT NULL,
    "motivo_rechazo" VARCHAR(300) NOT NULL,
    "aprobado_por_id" INTEGER,
    "libreta_id" INTEGER NOT NULL,
    "periodo_id" INTEGER NOT NULL,
    "socio_id" INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS "creditos_multacredito" (
    "id" SERIAL PRIMARY KEY,
    "numero_cuota" INTEGER NOT NULL,
    "tipo" VARCHAR(20) NOT NULL,
    "monto" NUMERIC NOT NULL,
    "pagada" BOOLEAN NOT NULL,
    "fecha_generacion" DATE NOT NULL,
    "fecha_pago" DATE,
    "observaciones" VARCHAR(200) NOT NULL,
    "credito_id" INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS "creditos_pagocredito" (
    "id" SERIAL PRIMARY KEY,
    "numero_pago" INTEGER NOT NULL,
    "monto_pagado" NUMERIC NOT NULL,
    "saldo_anterior" NUMERIC NOT NULL,
    "saldo_posterior" NUMERIC NOT NULL,
    "fecha_reporte" TIMESTAMP WITH TIME ZONE NOT NULL,
    "fecha_verificacion" TIMESTAMP WITH TIME ZONE,
    "comprobante_referencia" VARCHAR(200) NOT NULL,
    "estado" VARCHAR(20) NOT NULL,
    "es_abono" BOOLEAN NOT NULL,
    "observaciones" VARCHAR(300) NOT NULL,
    "credito_id" INTEGER NOT NULL,
    "verificado_por_id" INTEGER
);

CREATE TABLE IF NOT EXISTS "cuentas_rifamensual" (
    "id" SERIAL PRIMARY KEY,
    "mes" INTEGER NOT NULL,
    "anio" INTEGER NOT NULL,
    "numeros_loteria" VARCHAR(50) NOT NULL,
    "monto_premio" NUMERIC NOT NULL,
    "estado" VARCHAR(20) NOT NULL,
    "socio_al_dia" BOOLEAN NOT NULL,
    "observaciones" TEXT NOT NULL,
    "fecha_registro" TIMESTAMP WITH TIME ZONE NOT NULL,
    "libreta_ganadora_id" INTEGER,
    "periodo_id" INTEGER NOT NULL,
    "registrado_por_id" INTEGER
);

CREATE TABLE IF NOT EXISTS "django_admin_log" (
    "id" SERIAL PRIMARY KEY,
    "object_id" TEXT,
    "object_repr" VARCHAR(200) NOT NULL,
    "action_flag" INTEGER NOT NULL,
    "change_message" TEXT NOT NULL,
    "content_type_id" INTEGER,
    "user_id" INTEGER NOT NULL,
    "action_time" TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE IF NOT EXISTS "django_content_type" (
    "id" SERIAL PRIMARY KEY,
    "app_label" VARCHAR(100) NOT NULL,
    "model" VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS "django_migrations" (
    "id" SERIAL PRIMARY KEY,
    "app" VARCHAR(255) NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "applied" TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE IF NOT EXISTS "django_session" (
    "session_key" VARCHAR(40),
    "session_data" TEXT NOT NULL,
    "expire_date" TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE IF NOT EXISTS "multas_asistenciareunion" (
    "id" SERIAL PRIMARY KEY,
    "estado" VARCHAR(25) NOT NULL,
    "hora_llegada" TEXT,
    "justificacion" VARCHAR(300) NOT NULL,
    "multas_generadas" BOOLEAN NOT NULL,
    "socio_id" INTEGER NOT NULL,
    "reunion_id" INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS "multas_comportamientoreunion" (
    "id" SERIAL PRIMARY KEY,
    "descripcion" VARCHAR(200) NOT NULL,
    "multa_generada" BOOLEAN NOT NULL,
    "socio_id" INTEGER NOT NULL,
    "reunion_id" INTEGER NOT NULL,
    "tipo_multa_id" INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS "multas_multa" (
    "id" SERIAL PRIMARY KEY,
    "origen" VARCHAR(40) NOT NULL,
    "descripcion" VARCHAR(300) NOT NULL,
    "monto" NUMERIC NOT NULL,
    "estado" VARCHAR(20) NOT NULL,
    "fecha_generacion" DATE NOT NULL,
    "fecha_pago" DATE,
    "comprobante_pago" VARCHAR(200) NOT NULL,
    "observaciones" VARCHAR(300) NOT NULL,
    "aplicada_por_id" INTEGER,
    "libreta_id" INTEGER,
    "periodo_id" INTEGER NOT NULL,
    "socio_id" INTEGER NOT NULL,
    "reunion_id" INTEGER
);

CREATE TABLE IF NOT EXISTS "multas_reunion" (
    "id" SERIAL PRIMARY KEY,
    "fecha" DATE NOT NULL,
    "mes" INTEGER NOT NULL,
    "anio" INTEGER NOT NULL,
    "descripcion" VARCHAR(200) NOT NULL,
    "estado" VARCHAR(20) NOT NULL,
    "notas" TEXT NOT NULL,
    "periodo_id" INTEGER NOT NULL,
    "registrada_por_id" INTEGER
);

CREATE TABLE IF NOT EXISTS "multas_tipomulta" (
    "id" SERIAL PRIMARY KEY,
    "nombre" VARCHAR(100) NOT NULL,
    "descripcion" TEXT NOT NULL,
    "monto" NUMERIC NOT NULL,
    "aplica_a" VARCHAR(10) NOT NULL,
    "activo" BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS "socios_accesosocio" (
    "id" SERIAL PRIMARY KEY,
    "pin" VARCHAR(128) NOT NULL,
    "activo" BOOLEAN NOT NULL,
    "fecha_creacion" TIMESTAMP WITH TIME ZONE NOT NULL,
    "ultimo_acceso" TIMESTAMP WITH TIME ZONE,
    "socio_id" INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS "socios_aportemensual" (
    "id" SERIAL PRIMARY KEY,
    "mes" INTEGER NOT NULL,
    "anio" INTEGER NOT NULL,
    "monto_ahorro" NUMERIC NOT NULL,
    "monto_loteria" NUMERIC NOT NULL,
    "monto_cumpleanos" NUMERIC NOT NULL,
    "monto_total" NUMERIC NOT NULL,
    "estado" VARCHAR(20) NOT NULL,
    "fecha_reporte" TIMESTAMP WITH TIME ZONE,
    "fecha_verificacion" TIMESTAMP WITH TIME ZONE,
    "comprobante_referencia" VARCHAR(200) NOT NULL,
    "observacion" VARCHAR(300) NOT NULL,
    "libreta_id" INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS "socios_libreta" (
    "id" SERIAL PRIMARY KEY,
    "numero" INTEGER NOT NULL,
    "estado" VARCHAR(20) NOT NULL,
    "fecha_inscripcion" DATE NOT NULL,
    "inscripcion_pagada" BOOLEAN NOT NULL,
    "fecha_inscripcion_pago" DATE,
    "saldo_ahorro" NUMERIC NOT NULL,
    "observaciones" TEXT NOT NULL,
    "periodo_id" INTEGER NOT NULL,
    "socio_id" INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS "socios_periodo" (
    "id" SERIAL PRIMARY KEY,
    "anio" INTEGER NOT NULL,
    "fecha_inicio" DATE NOT NULL,
    "fecha_cierre" DATE NOT NULL,
    "activo" BOOLEAN NOT NULL,
    "descripcion" VARCHAR(200) NOT NULL
);

CREATE TABLE IF NOT EXISTS "socios_socio" (
    "id" SERIAL PRIMARY KEY,
    "cedula" VARCHAR(13) NOT NULL,
    "nombres" VARCHAR(100) NOT NULL,
    "apellidos" VARCHAR(100) NOT NULL,
    "fecha_nacimiento" DATE NOT NULL,
    "genero" VARCHAR(1) NOT NULL,
    "direccion" TEXT NOT NULL,
    "ciudad" VARCHAR(50) NOT NULL,
    "telefono" VARCHAR(15) NOT NULL,
    "whatsapp" VARCHAR(15) NOT NULL,
    "email" VARCHAR(254) NOT NULL,
    "es_menor" BOOLEAN NOT NULL,
    "representante_nombre" VARCHAR(200) NOT NULL,
    "representante_cedula" VARCHAR(13) NOT NULL,
    "estado" VARCHAR(20) NOT NULL,
    "fecha_registro" DATE NOT NULL,
    "observaciones" TEXT NOT NULL,
    "recomendado_por_id" INTEGER
);

-- DATOS

-- auth_permission
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (1, 1, 'add_logentry', 'Can add log entry');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (2, 1, 'change_logentry', 'Can change log entry');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (3, 1, 'delete_logentry', 'Can delete log entry');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (4, 1, 'view_logentry', 'Can view log entry');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (5, 3, 'add_permission', 'Can add permission');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (6, 3, 'change_permission', 'Can change permission');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (7, 3, 'delete_permission', 'Can delete permission');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (8, 3, 'view_permission', 'Can view permission');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (9, 2, 'add_group', 'Can add group');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (10, 2, 'change_group', 'Can change group');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (11, 2, 'delete_group', 'Can delete group');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (12, 2, 'view_group', 'Can view group');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (13, 4, 'add_user', 'Can add user');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (14, 4, 'change_user', 'Can change user');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (15, 4, 'delete_user', 'Can delete user');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (16, 4, 'view_user', 'Can view user');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (17, 5, 'add_contenttype', 'Can add content type');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (18, 5, 'change_contenttype', 'Can change content type');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (19, 5, 'delete_contenttype', 'Can delete content type');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (20, 5, 'view_contenttype', 'Can view content type');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (21, 6, 'add_session', 'Can add session');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (22, 6, 'change_session', 'Can change session');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (23, 6, 'delete_session', 'Can delete session');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (24, 6, 'view_session', 'Can view session');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (25, 7, 'add_perfilusuario', 'Can add perfil usuario');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (26, 7, 'change_perfilusuario', 'Can change perfil usuario');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (27, 7, 'delete_perfilusuario', 'Can delete perfil usuario');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (28, 7, 'view_perfilusuario', 'Can view perfil usuario');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (29, 11, 'add_periodo', 'Can add periodo');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (30, 11, 'change_periodo', 'Can change periodo');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (31, 11, 'delete_periodo', 'Can delete periodo');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (32, 11, 'view_periodo', 'Can view periodo');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (33, 12, 'add_socio', 'Can add socio');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (34, 12, 'change_socio', 'Can change socio');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (35, 12, 'delete_socio', 'Can delete socio');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (36, 12, 'view_socio', 'Can view socio');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (37, 10, 'add_libreta', 'Can add libreta');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (38, 10, 'change_libreta', 'Can change libreta');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (39, 10, 'delete_libreta', 'Can delete libreta');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (40, 10, 'view_libreta', 'Can view libreta');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (41, 8, 'add_accesosocio', 'Can add acceso socio');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (42, 8, 'change_accesosocio', 'Can change acceso socio');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (43, 8, 'delete_accesosocio', 'Can delete acceso socio');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (44, 8, 'view_accesosocio', 'Can view acceso socio');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (45, 9, 'add_aportemensual', 'Can add aporte mensual');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (46, 9, 'change_aportemensual', 'Can change aporte mensual');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (47, 9, 'delete_aportemensual', 'Can delete aporte mensual');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (48, 9, 'view_aportemensual', 'Can view aporte mensual');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (49, 13, 'add_rifamensual', 'Can add rifa mensual');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (50, 13, 'change_rifamensual', 'Can change rifa mensual');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (51, 13, 'delete_rifamensual', 'Can delete rifa mensual');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (52, 13, 'view_rifamensual', 'Can view rifa mensual');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (53, 14, 'add_credito', 'Can add credito');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (54, 14, 'change_credito', 'Can change credito');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (55, 14, 'delete_credito', 'Can delete credito');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (56, 14, 'view_credito', 'Can view credito');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (57, 15, 'add_multacredito', 'Can add multa credito');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (58, 15, 'change_multacredito', 'Can change multa credito');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (59, 15, 'delete_multacredito', 'Can delete multa credito');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (60, 15, 'view_multacredito', 'Can view multa credito');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (61, 16, 'add_pagocredito', 'Can add pago credito');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (62, 16, 'change_pagocredito', 'Can change pago credito');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (63, 16, 'delete_pagocredito', 'Can delete pago credito');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (64, 16, 'view_pagocredito', 'Can view pago credito');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (65, 21, 'add_tipomulta', 'Can add Tipo de Multa');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (66, 21, 'change_tipomulta', 'Can change Tipo de Multa');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (67, 21, 'delete_tipomulta', 'Can delete Tipo de Multa');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (68, 21, 'view_tipomulta', 'Can view Tipo de Multa');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (69, 20, 'add_reunion', 'Can add reunion');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (70, 20, 'change_reunion', 'Can change reunion');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (71, 20, 'delete_reunion', 'Can delete reunion');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (72, 20, 'view_reunion', 'Can view reunion');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (73, 19, 'add_multa', 'Can add multa');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (74, 19, 'change_multa', 'Can change multa');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (75, 19, 'delete_multa', 'Can delete multa');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (76, 19, 'view_multa', 'Can view multa');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (77, 18, 'add_comportamientoreunion', 'Can add comportamiento reunion');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (78, 18, 'change_comportamientoreunion', 'Can change comportamiento reunion');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (79, 18, 'delete_comportamientoreunion', 'Can delete comportamiento reunion');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (80, 18, 'view_comportamientoreunion', 'Can view comportamiento reunion');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (81, 17, 'add_asistenciareunion', 'Can add asistencia reunion');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (82, 17, 'change_asistenciareunion', 'Can change asistencia reunion');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (83, 17, 'delete_asistenciareunion', 'Can delete asistencia reunion');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (84, 17, 'view_asistenciareunion', 'Can view asistencia reunion');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (85, 22, 'add_movimiento', 'Can add Movimiento');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (86, 22, 'change_movimiento', 'Can change Movimiento');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (87, 22, 'delete_movimiento', 'Can delete Movimiento');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (88, 22, 'view_movimiento', 'Can view Movimiento');

-- auth_user
INSERT INTO "auth_user" ("id", "password", "last_login", "is_superuser", "username", "last_name", "email", "is_staff", "is_active", "date_joined", "first_name") VALUES (1, 'pbkdf2_sha256$1200000$32tY4MEtfDjWL0HQAha5Mj$UgNmVWAUhMFKxmYrfb8sfUn8HDiYxBZGEkLUak8TDyc=', NULL, TRUE, 'admin', 'Admin', 'admin@bailarines.coop', TRUE, TRUE, '2026-04-09 02:01:37.122604', 'Carlos');
INSERT INTO "auth_user" ("id", "password", "last_login", "is_superuser", "username", "last_name", "email", "is_staff", "is_active", "date_joined", "first_name") VALUES (2, 'pbkdf2_sha256$1200000$Xcwo4LXTyx5mjzM6lzGMkS$P+qcXqiv6W+kLn95gUAb5Y0Dl/vq0nzpswPClwoUPNo=', NULL, FALSE, 'cajero1', 'López', '', FALSE, TRUE, '2026-04-09 02:01:38.036385', 'María');

-- core_movimiento
INSERT INTO "core_movimiento" ("id", "tipo", "categoria", "descripcion", "monto", "fecha", "origen", "comprobante", "socio_ref", "libreta_ref", "credito_ref", "fecha_registro", "observaciones", "registrado_por_id") VALUES (1, 'ingreso', 'aporte_mensual', 'Aporte Enero 2026 — Libreta #1 — Mabel Adelaida Bailón Rivas', 22, '2026-01-20', 'automatico', '', 'Mabel Adelaida Bailón Rivas', '#1', '', '2026-04-11 14:43:59.697266', '', 1);
INSERT INTO "core_movimiento" ("id", "tipo", "categoria", "descripcion", "monto", "fecha", "origen", "comprobante", "socio_ref", "libreta_ref", "credito_ref", "fecha_registro", "observaciones", "registrado_por_id") VALUES (2, 'ingreso', 'aporte_mensual', 'Aporte Febrero 2026 — Libreta #1 — Mabel Adelaida Bailón Rivas', 22, '2026-02-20', 'automatico', '', 'Mabel Adelaida Bailón Rivas', '#1', '', '2026-04-11 14:43:59.726938', '', 1);
INSERT INTO "core_movimiento" ("id", "tipo", "categoria", "descripcion", "monto", "fecha", "origen", "comprobante", "socio_ref", "libreta_ref", "credito_ref", "fecha_registro", "observaciones", "registrado_por_id") VALUES (3, 'ingreso', 'aporte_mensual', 'Aporte Marzo 2026 — Libreta #1 — Mabel Adelaida Bailón Rivas', 22, '2026-03-20', 'automatico', '', 'Mabel Adelaida Bailón Rivas', '#1', '', '2026-04-11 14:43:59.738213', '', 1);
INSERT INTO "core_movimiento" ("id", "tipo", "categoria", "descripcion", "monto", "fecha", "origen", "comprobante", "socio_ref", "libreta_ref", "credito_ref", "fecha_registro", "observaciones", "registrado_por_id") VALUES (4, 'ingreso', 'aporte_mensual', 'Aporte Enero 2026 — Libreta #2 — Mabel Adelaida Bailón Rivas', 22, '2026-01-20', 'automatico', '', 'Mabel Adelaida Bailón Rivas', '#2', '', '2026-04-11 14:43:59.751133', '', 1);
INSERT INTO "core_movimiento" ("id", "tipo", "categoria", "descripcion", "monto", "fecha", "origen", "comprobante", "socio_ref", "libreta_ref", "credito_ref", "fecha_registro", "observaciones", "registrado_por_id") VALUES (5, 'ingreso', 'aporte_mensual', 'Aporte Febrero 2026 — Libreta #2 — Mabel Adelaida Bailón Rivas', 22, '2026-02-20', 'automatico', '', 'Mabel Adelaida Bailón Rivas', '#2', '', '2026-04-11 14:43:59.762978', '', 1);
INSERT INTO "core_movimiento" ("id", "tipo", "categoria", "descripcion", "monto", "fecha", "origen", "comprobante", "socio_ref", "libreta_ref", "credito_ref", "fecha_registro", "observaciones", "registrado_por_id") VALUES (6, 'ingreso', 'aporte_mensual', 'Aporte Marzo 2026 — Libreta #2 — Mabel Adelaida Bailón Rivas', 22, '2026-03-20', 'automatico', '', 'Mabel Adelaida Bailón Rivas', '#2', '', '2026-04-11 14:43:59.777215', '', 1);
INSERT INTO "core_movimiento" ("id", "tipo", "categoria", "descripcion", "monto", "fecha", "origen", "comprobante", "socio_ref", "libreta_ref", "credito_ref", "fecha_registro", "observaciones", "registrado_por_id") VALUES (7, 'ingreso', 'aporte_mensual', 'Aporte Enero 2026 — Libreta #3 — Mabel Adelaida Bailón Rivas', 22, '2026-01-20', 'automatico', '', 'Mabel Adelaida Bailón Rivas', '#3', '', '2026-04-11 14:43:59.812746', '', 1);
INSERT INTO "core_movimiento" ("id", "tipo", "categoria", "descripcion", "monto", "fecha", "origen", "comprobante", "socio_ref", "libreta_ref", "credito_ref", "fecha_registro", "observaciones", "registrado_por_id") VALUES (8, 'ingreso', 'aporte_mensual', 'Aporte Febrero 2026 — Libreta #3 — Mabel Adelaida Bailón Rivas', 22, '2026-02-20', 'automatico', '', 'Mabel Adelaida Bailón Rivas', '#3', '', '2026-04-11 14:43:59.824414', '', 1);
INSERT INTO "core_movimiento" ("id", "tipo", "categoria", "descripcion", "monto", "fecha", "origen", "comprobante", "socio_ref", "libreta_ref", "credito_ref", "fecha_registro", "observaciones", "registrado_por_id") VALUES (9, 'ingreso', 'aporte_mensual', 'Aporte Marzo 2026 — Libreta #3 — Mabel Adelaida Bailón Rivas', 22, '2026-03-20', 'automatico', '', 'Mabel Adelaida Bailón Rivas', '#3', '', '2026-04-11 14:43:59.835794', '', 1);
INSERT INTO "core_movimiento" ("id", "tipo", "categoria", "descripcion", "monto", "fecha", "origen", "comprobante", "socio_ref", "libreta_ref", "credito_ref", "fecha_registro", "observaciones", "registrado_por_id") VALUES (10, 'ingreso', 'aporte_mensual', 'Aporte Enero 2026 — Libreta #4 — Mabel Adelaida Bailón Rivas', 22, '2026-01-20', 'automatico', '', 'Mabel Adelaida Bailón Rivas', '#4', '', '2026-04-11 14:43:59.850482', '', 1);
INSERT INTO "core_movimiento" ("id", "tipo", "categoria", "descripcion", "monto", "fecha", "origen", "comprobante", "socio_ref", "libreta_ref", "credito_ref", "fecha_registro", "observaciones", "registrado_por_id") VALUES (11, 'ingreso', 'aporte_mensual', 'Aporte Febrero 2026 — Libreta #4 — Mabel Adelaida Bailón Rivas', 22, '2026-02-20', 'automatico', '', 'Mabel Adelaida Bailón Rivas', '#4', '', '2026-04-11 14:43:59.861044', '', 1);
INSERT INTO "core_movimiento" ("id", "tipo", "categoria", "descripcion", "monto", "fecha", "origen", "comprobante", "socio_ref", "libreta_ref", "credito_ref", "fecha_registro", "observaciones", "registrado_por_id") VALUES (12, 'ingreso', 'aporte_mensual', 'Aporte Marzo 2026 — Libreta #4 — Mabel Adelaida Bailón Rivas', 22, '2026-03-20', 'automatico', '', 'Mabel Adelaida Bailón Rivas', '#4', '', '2026-04-11 14:43:59.875218', '', 1);
INSERT INTO "core_movimiento" ("id", "tipo", "categoria", "descripcion", "monto", "fecha", "origen", "comprobante", "socio_ref", "libreta_ref", "credito_ref", "fecha_registro", "observaciones", "registrado_por_id") VALUES (13, 'ingreso', 'aporte_mensual', 'Aporte Enero 2026 — Libreta #5 — Betty Mariela Molina Cercado', 22, '2026-01-20', 'automatico', '', 'Betty Mariela Molina Cercado', '#5', '', '2026-04-11 14:43:59.888459', '', 1);
INSERT INTO "core_movimiento" ("id", "tipo", "categoria", "descripcion", "monto", "fecha", "origen", "comprobante", "socio_ref", "libreta_ref", "credito_ref", "fecha_registro", "observaciones", "registrado_por_id") VALUES (14, 'ingreso', 'aporte_mensual', 'Aporte Febrero 2026 — Libreta #5 — Betty Mariela Molina Cercado', 22, '2026-02-20', 'automatico', '', 'Betty Mariela Molina Cercado', '#5', '', '2026-04-11 14:43:59.914214', '', 1);
INSERT INTO "core_movimiento" ("id", "tipo", "categoria", "descripcion", "monto", "fecha", "origen", "comprobante", "socio_ref", "libreta_ref", "credito_ref", "fecha_registro", "observaciones", "registrado_por_id") VALUES (15, 'ingreso', 'aporte_mensual', 'Aporte Marzo 2026 — Libreta #5 — Betty Mariela Molina Cercado', 22, '2026-03-20', 'automatico', '', 'Betty Mariela Molina Cercado', '#5', '', '2026-04-11 14:43:59.927353', '', 1);
INSERT INTO "core_movimiento" ("id", "tipo", "categoria", "descripcion", "monto", "fecha", "origen", "comprobante", "socio_ref", "libreta_ref", "credito_ref", "fecha_registro", "observaciones", "registrado_por_id") VALUES (16, 'ingreso', 'aporte_mensual', 'Aporte Enero 2026 — Libreta #6 — Betty Mariela Molina Cercado', 22, '2026-01-20', 'automatico', '', 'Betty Mariela Molina Cercado', '#6', '', '2026-04-11 14:43:59.940101', '', 1);
INSERT INTO "core_movimiento" ("id", "tipo", "categoria", "descripcion", "monto", "fecha", "origen", "comprobante", "socio_ref", "libreta_ref", "credito_ref", "fecha_registro", "observaciones", "registrado_por_id") VALUES (17, 'ingreso', 'aporte_mensual', 'Aporte Febrero 2026 — Libreta #6 — Betty Mariela Molina Cercado', 22, '2026-02-20', 'automatico', '', 'Betty Mariela Molina Cercado', '#6', '', '2026-04-11 14:43:59.957616', '', 1);
INSERT INTO "core_movimiento" ("id", "tipo", "categoria", "descripcion", "monto", "fecha", "origen", "comprobante", "socio_ref", "libreta_ref", "credito_ref", "fecha_registro", "observaciones", "registrado_por_id") VALUES (18, 'ingreso', 'aporte_mensual', 'Aporte Marzo 2026 — Libreta #6 — Betty Mariela Molina Cercado', 22, '2026-03-20', 'automatico', '', 'Betty Mariela Molina Cercado', '#6', '', '2026-04-11 14:43:59.967117', '', 1);
INSERT INTO "core_movimiento" ("id", "tipo", "categoria", "descripcion", "monto", "fecha", "origen", "comprobante", "socio_ref", "libreta_ref", "credito_ref", "fecha_registro", "observaciones", "registrado_por_id") VALUES (19, 'ingreso', 'aporte_mensual', 'Aporte Enero 2026 — Libreta #7 — Carlos Junior Zambrano Meza', 22, '2026-01-20', 'automatico', '', 'Carlos Junior Zambrano Meza', '#7', '', '2026-04-11 14:43:59.979462', '', 1);
INSERT INTO "core_movimiento" ("id", "tipo", "categoria", "descripcion", "monto", "fecha", "origen", "comprobante", "socio_ref", "libreta_ref", "credito_ref", "fecha_registro", "observaciones", "registrado_por_id") VALUES (20, 'ingreso', 'aporte_mensual', 'Aporte Febrero 2026 — Libreta #7 — Carlos Junior Zambrano Meza', 22, '2026-02-20', 'automatico', '', 'Carlos Junior Zambrano Meza', '#7', '', '2026-04-11 14:43:59.991788', '', 1);
INSERT INTO "core_movimiento" ("id", "tipo", "categoria", "descripcion", "monto", "fecha", "origen", "comprobante", "socio_ref", "libreta_ref", "credito_ref", "fecha_registro", "observaciones", "registrado_por_id") VALUES (21, 'ingreso', 'aporte_mensual', 'Aporte Marzo 2026 — Libreta #7 — Carlos Junior Zambrano Meza', 22, '2026-03-20', 'automatico', '', 'Carlos Junior Zambrano Meza', '#7', '', '2026-04-11 14:44:00.002792', '', 1);
INSERT INTO "core_movimiento" ("id", "tipo", "categoria", "descripcion", "monto", "fecha", "origen", "comprobante", "socio_ref", "libreta_ref", "credito_ref", "fecha_registro", "observaciones", "registrado_por_id") VALUES (22, 'ingreso', 'aporte_mensual', 'Aporte Enero 2026 — Libreta #8 — Zayda Arelis Moreno Bailon', 22, '2026-01-20', 'automatico', '', 'Zayda Arelis Moreno Bailon', '#8', '', '2026-04-11 14:44:00.015383', '', 1);
INSERT INTO "core_movimiento" ("id", "tipo", "categoria", "descripcion", "monto", "fecha", "origen", "comprobante", "socio_ref", "libreta_ref", "credito_ref", "fecha_registro", "observaciones", "registrado_por_id") VALUES (23, 'ingreso', 'aporte_mensual', 'Aporte Febrero 2026 — Libreta #8 — Zayda Arelis Moreno Bailon', 22, '2026-02-20', 'automatico', '', 'Zayda Arelis Moreno Bailon', '#8', '', '2026-04-11 14:44:00.025717', '', 1);
INSERT INTO "core_movimiento" ("id", "tipo", "categoria", "descripcion", "monto", "fecha", "origen", "comprobante", "socio_ref", "libreta_ref", "credito_ref", "fecha_registro", "observaciones", "registrado_por_id") VALUES (24, 'ingreso', 'aporte_mensual', 'Aporte Marzo 2026 — Libreta #8 — Zayda Arelis Moreno Bailon', 22, '2026-03-20', 'automatico', '', 'Zayda Arelis Moreno Bailon', '#8', '', '2026-04-11 14:44:00.036983', '', 1);
INSERT INTO "core_movimiento" ("id", "tipo", "categoria", "descripcion", "monto", "fecha", "origen", "comprobante", "socio_ref", "libreta_ref", "credito_ref", "fecha_registro", "observaciones", "registrado_por_id") VALUES (25, 'ingreso', 'aporte_mensual', 'Aporte Enero 2026 — Libreta #9 — Zayda Arelis Moreno Bailon', 22, '2026-01-20', 'automatico', '', 'Zayda Arelis Moreno Bailon', '#9', '', '2026-04-11 14:44:00.048822', '', 1);
INSERT INTO "core_movimiento" ("id", "tipo", "categoria", "descripcion", "monto", "fecha", "origen", "comprobante", "socio_ref", "libreta_ref", "credito_ref", "fecha_registro", "observaciones", "registrado_por_id") VALUES (26, 'ingreso', 'aporte_mensual', 'Aporte Febrero 2026 — Libreta #9 — Zayda Arelis Moreno Bailon', 22, '2026-02-20', 'automatico', '', 'Zayda Arelis Moreno Bailon', '#9', '', '2026-04-11 14:44:00.059833', '', 1);
INSERT INTO "core_movimiento" ("id", "tipo", "categoria", "descripcion", "monto", "fecha", "origen", "comprobante", "socio_ref", "libreta_ref", "credito_ref", "fecha_registro", "observaciones", "registrado_por_id") VALUES (27, 'ingreso', 'aporte_mensual', 'Aporte Marzo 2026 — Libreta #9 — Zayda Arelis Moreno Bailon', 22, '2026-03-20', 'automatico', '', 'Zayda Arelis Moreno Bailon', '#9', '', '2026-04-11 14:44:00.069829', '', 1);
INSERT INTO "core_movimiento" ("id", "tipo", "categoria", "descripcion", "monto", "fecha", "origen", "comprobante", "socio_ref", "libreta_ref", "credito_ref", "fecha_registro", "observaciones", "registrado_por_id") VALUES (28, 'ingreso', 'aporte_mensual', 'Aporte Enero 2026 — Libreta #10 — Steven Vidal Piza Alvarez', 22, '2026-01-20', 'automatico', '', 'Steven Vidal Piza Alvarez', '#10', '', '2026-04-11 14:44:00.085601', '', 1);
INSERT INTO "core_movimiento" ("id", "tipo", "categoria", "descripcion", "monto", "fecha", "origen", "comprobante", "socio_ref", "libreta_ref", "credito_ref", "fecha_registro", "observaciones", "registrado_por_id") VALUES (29, 'ingreso', 'aporte_mensual', 'Aporte Febrero 2026 — Libreta #10 — Steven Vidal Piza Alvarez', 22, '2026-02-20', 'automatico', '', 'Steven Vidal Piza Alvarez', '#10', '', '2026-04-11 14:44:00.097149', '', 1);
INSERT INTO "core_movimiento" ("id", "tipo", "categoria", "descripcion", "monto", "fecha", "origen", "comprobante", "socio_ref", "libreta_ref", "credito_ref", "fecha_registro", "observaciones", "registrado_por_id") VALUES (30, 'ingreso', 'aporte_mensual', 'Aporte Marzo 2026 — Libreta #10 — Steven Vidal Piza Alvarez', 22, '2026-03-20', 'automatico', '', 'Steven Vidal Piza Alvarez', '#10', '', '2026-04-11 14:44:00.107048', '', 1);
INSERT INTO "core_movimiento" ("id", "tipo", "categoria", "descripcion", "monto", "fecha", "origen", "comprobante", "socio_ref", "libreta_ref", "credito_ref", "fecha_registro", "observaciones", "registrado_por_id") VALUES (31, 'egreso', 'desembolso_credito', 'Desembolso crédito CRD-2026-02 — Betty Mariela Molina Cercado', 424, '2026-01-17', 'automatico', '', 'Betty Mariela Molina Cercado', '#5', 'CRD-2026-02', '2026-04-11 14:44:00.123502', '', 1);
INSERT INTO "core_movimiento" ("id", "tipo", "categoria", "descripcion", "monto", "fecha", "origen", "comprobante", "socio_ref", "libreta_ref", "credito_ref", "fecha_registro", "observaciones", "registrado_por_id") VALUES (32, 'egreso', 'desembolso_credito', 'Desembolso crédito CRD-2026-01 — Mabel Adelaida Bailón Rivas', 499.5, '2026-01-16', 'automatico', '', 'Mabel Adelaida Bailón Rivas', '#1', 'CRD-2026-01', '2026-04-11 14:44:00.135541', '', 1);
INSERT INTO "core_movimiento" ("id", "tipo", "categoria", "descripcion", "monto", "fecha", "origen", "comprobante", "socio_ref", "libreta_ref", "credito_ref", "fecha_registro", "observaciones", "registrado_por_id") VALUES (33, 'ingreso', 'interes_credito', 'Pago cuota #1 — CRD-2026-01 — Mabel Adelaida Bailón Rivas', 191.67, '2026-04-09', 'automatico', '', 'Mabel Adelaida Bailón Rivas', '', 'CRD-2026-01', '2026-04-11 14:44:00.149500', '', 1);
INSERT INTO "core_movimiento" ("id", "tipo", "categoria", "descripcion", "monto", "fecha", "origen", "comprobante", "socio_ref", "libreta_ref", "credito_ref", "fecha_registro", "observaciones", "registrado_por_id") VALUES (34, 'ingreso', 'inscripcion', 'Inscripción Libreta #1 — Mabel Adelaida Bailón Rivas — Periodo 2026', 20, '2026-01-10', 'automatico', '', 'Mabel Adelaida Bailón Rivas', '#1', '', '2026-04-11 14:44:00.161080', '', 1);
INSERT INTO "core_movimiento" ("id", "tipo", "categoria", "descripcion", "monto", "fecha", "origen", "comprobante", "socio_ref", "libreta_ref", "credito_ref", "fecha_registro", "observaciones", "registrado_por_id") VALUES (35, 'ingreso', 'inscripcion', 'Inscripción Libreta #2 — Mabel Adelaida Bailón Rivas — Periodo 2026', 20, '2026-01-10', 'automatico', '', 'Mabel Adelaida Bailón Rivas', '#2', '', '2026-04-11 14:44:00.172375', '', 1);
INSERT INTO "core_movimiento" ("id", "tipo", "categoria", "descripcion", "monto", "fecha", "origen", "comprobante", "socio_ref", "libreta_ref", "credito_ref", "fecha_registro", "observaciones", "registrado_por_id") VALUES (36, 'ingreso', 'inscripcion', 'Inscripción Libreta #3 — Mabel Adelaida Bailón Rivas — Periodo 2026', 20, '2026-01-10', 'automatico', '', 'Mabel Adelaida Bailón Rivas', '#3', '', '2026-04-11 14:44:00.182902', '', 1);
INSERT INTO "core_movimiento" ("id", "tipo", "categoria", "descripcion", "monto", "fecha", "origen", "comprobante", "socio_ref", "libreta_ref", "credito_ref", "fecha_registro", "observaciones", "registrado_por_id") VALUES (37, 'ingreso', 'inscripcion', 'Inscripción Libreta #4 — Mabel Adelaida Bailón Rivas — Periodo 2026', 20, '2026-01-10', 'automatico', '', 'Mabel Adelaida Bailón Rivas', '#4', '', '2026-04-11 14:44:00.192733', '', 1);
INSERT INTO "core_movimiento" ("id", "tipo", "categoria", "descripcion", "monto", "fecha", "origen", "comprobante", "socio_ref", "libreta_ref", "credito_ref", "fecha_registro", "observaciones", "registrado_por_id") VALUES (38, 'ingreso', 'inscripcion', 'Inscripción Libreta #5 — Betty Mariela Molina Cercado — Periodo 2026', 20, '2026-01-10', 'automatico', '', 'Betty Mariela Molina Cercado', '#5', '', '2026-04-11 14:44:00.204378', '', 1);
INSERT INTO "core_movimiento" ("id", "tipo", "categoria", "descripcion", "monto", "fecha", "origen", "comprobante", "socio_ref", "libreta_ref", "credito_ref", "fecha_registro", "observaciones", "registrado_por_id") VALUES (39, 'ingreso', 'inscripcion', 'Inscripción Libreta #6 — Betty Mariela Molina Cercado — Periodo 2026', 20, '2026-01-10', 'automatico', '', 'Betty Mariela Molina Cercado', '#6', '', '2026-04-11 14:44:00.218859', '', 1);
INSERT INTO "core_movimiento" ("id", "tipo", "categoria", "descripcion", "monto", "fecha", "origen", "comprobante", "socio_ref", "libreta_ref", "credito_ref", "fecha_registro", "observaciones", "registrado_por_id") VALUES (40, 'ingreso', 'inscripcion', 'Inscripción Libreta #7 — Carlos Junior Zambrano Meza — Periodo 2026', 20, '2026-01-10', 'automatico', '', 'Carlos Junior Zambrano Meza', '#7', '', '2026-04-11 14:44:00.230369', '', 1);
INSERT INTO "core_movimiento" ("id", "tipo", "categoria", "descripcion", "monto", "fecha", "origen", "comprobante", "socio_ref", "libreta_ref", "credito_ref", "fecha_registro", "observaciones", "registrado_por_id") VALUES (41, 'ingreso', 'inscripcion', 'Inscripción Libreta #8 — Zayda Arelis Moreno Bailon — Periodo 2026', 20, '2026-01-10', 'automatico', '', 'Zayda Arelis Moreno Bailon', '#8', '', '2026-04-11 14:44:00.241324', '', 1);
INSERT INTO "core_movimiento" ("id", "tipo", "categoria", "descripcion", "monto", "fecha", "origen", "comprobante", "socio_ref", "libreta_ref", "credito_ref", "fecha_registro", "observaciones", "registrado_por_id") VALUES (42, 'ingreso', 'inscripcion', 'Inscripción Libreta #9 — Zayda Arelis Moreno Bailon — Periodo 2026', 20, '2026-01-10', 'automatico', '', 'Zayda Arelis Moreno Bailon', '#9', '', '2026-04-11 14:44:00.252283', '', 1);
INSERT INTO "core_movimiento" ("id", "tipo", "categoria", "descripcion", "monto", "fecha", "origen", "comprobante", "socio_ref", "libreta_ref", "credito_ref", "fecha_registro", "observaciones", "registrado_por_id") VALUES (43, 'ingreso', 'inscripcion', 'Inscripción Libreta #10 — Steven Vidal Piza Alvarez — Periodo 2026', 20, '2026-01-10', 'automatico', '', 'Steven Vidal Piza Alvarez', '#10', '', '2026-04-11 14:44:00.263751', '', 1);

-- core_perfilusuario
INSERT INTO "core_perfilusuario" ("id", "rol", "telefono", "usuario_id") VALUES (1, 'admin', '0991234567', 1);
INSERT INTO "core_perfilusuario" ("id", "rol", "telefono", "usuario_id") VALUES (2, 'cajero', '', 2);

-- creditos_credito
INSERT INTO "creditos_credito" ("id", "numero", "tipo", "monto_solicitado", "plazo_meses", "banco", "numero_cuenta_bancaria", "titular_cuenta", "cedula_titular", "tasa_mensual", "interes_total", "comision_bancaria", "beneficio_transferencia", "monto_transferir", "cuota_mensual", "monto_pago_final", "saldo_pendiente", "estado", "fecha_solicitud", "fecha_aprobacion", "fecha_desembolso", "fecha_pago_limite", "observaciones", "motivo_rechazo", "aprobado_por_id", "libreta_id", "periodo_id", "socio_id") VALUES (1, 'CRD-2026-01', 'mensualizado', 500, 3, 'pichincha', '2214912652', 'Bailón Rivas Mabel Adelaida', '1316078169', 0.05, 75, 0.5, 0.5, 499.5, 191.67, 0, 500, 'desembolsado', '2026-04-09 02:01:40.029320', '2026-01-16', '2026-01-16', '2026-04-16', '', '', 1, 1, 1, 1);
INSERT INTO "creditos_credito" ("id", "numero", "tipo", "monto_solicitado", "plazo_meses", "banco", "numero_cuenta_bancaria", "titular_cuenta", "cedula_titular", "tasa_mensual", "interes_total", "comision_bancaria", "beneficio_transferencia", "monto_transferir", "cuota_mensual", "monto_pago_final", "saldo_pendiente", "estado", "fecha_solicitud", "fecha_aprobacion", "fecha_desembolso", "fecha_pago_limite", "observaciones", "motivo_rechazo", "aprobado_por_id", "libreta_id", "periodo_id", "socio_id") VALUES (2, 'CRD-2026-02', 'no_mensualizado', 500, 3, 'guayaquil', '0031955225', 'Betty Mariela Molina Cercado', '0910117829', 0.05, 75, 1, 0.59, 424, 0, 500, 500, 'desembolsado', '2026-04-09 02:01:40.045310', '2026-01-17', '2026-01-17', '2026-04-17', '', '', 1, 5, 1, 2);
INSERT INTO "creditos_credito" ("id", "numero", "tipo", "monto_solicitado", "plazo_meses", "banco", "numero_cuenta_bancaria", "titular_cuenta", "cedula_titular", "tasa_mensual", "interes_total", "comision_bancaria", "beneficio_transferencia", "monto_transferir", "cuota_mensual", "monto_pago_final", "saldo_pendiente", "estado", "fecha_solicitud", "fecha_aprobacion", "fecha_desembolso", "fecha_pago_limite", "observaciones", "motivo_rechazo", "aprobado_por_id", "libreta_id", "periodo_id", "socio_id") VALUES (3, 'CRD-2026-03', 'mensualizado', 300, 2, 'pichincha', '2210293543', 'Carlos Junior Zambrano Meza', '1317867909', 0.05, 30, 0.5, 0.5, 299.5, 165, 0, 300, 'pendiente', '2026-04-09 02:01:40.053966', NULL, NULL, NULL, '', '', NULL, 7, 1, 3);

-- creditos_pagocredito
INSERT INTO "creditos_pagocredito" ("id", "numero_pago", "monto_pagado", "saldo_anterior", "saldo_posterior", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "estado", "es_abono", "observaciones", "credito_id", "verificado_por_id") VALUES (1, 1, 191.67, 500, 500, '2026-04-09 02:01:40.037062', NULL, 'TXN001234', 'verificado', FALSE, '', 1, 2);

-- django_content_type
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (1, 'admin', 'logentry');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (2, 'auth', 'group');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (3, 'auth', 'permission');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (4, 'auth', 'user');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (5, 'contenttypes', 'contenttype');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (6, 'sessions', 'session');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (7, 'core', 'perfilusuario');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (8, 'socios', 'accesosocio');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (9, 'socios', 'aportemensual');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (10, 'socios', 'libreta');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (11, 'socios', 'periodo');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (12, 'socios', 'socio');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (13, 'cuentas', 'rifamensual');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (14, 'creditos', 'credito');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (15, 'creditos', 'multacredito');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (16, 'creditos', 'pagocredito');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (17, 'multas', 'asistenciareunion');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (18, 'multas', 'comportamientoreunion');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (19, 'multas', 'multa');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (20, 'multas', 'reunion');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (21, 'multas', 'tipomulta');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (22, 'core', 'movimiento');

-- django_migrations
INSERT INTO "django_migrations" ("id", "app", "name", "applied") VALUES (1, 'contenttypes', '0001_initial', '2026-04-08 20:35:36.846472');
INSERT INTO "django_migrations" ("id", "app", "name", "applied") VALUES (2, 'auth', '0001_initial', '2026-04-08 20:35:36.875411');
INSERT INTO "django_migrations" ("id", "app", "name", "applied") VALUES (3, 'admin', '0001_initial', '2026-04-08 20:35:36.896760');
INSERT INTO "django_migrations" ("id", "app", "name", "applied") VALUES (4, 'admin', '0002_logentry_remove_auto_add', '2026-04-08 20:35:36.916490');
INSERT INTO "django_migrations" ("id", "app", "name", "applied") VALUES (5, 'admin', '0003_logentry_add_action_flag_choices', '2026-04-08 20:35:36.930428');
INSERT INTO "django_migrations" ("id", "app", "name", "applied") VALUES (6, 'contenttypes', '0002_remove_content_type_name', '2026-04-08 20:35:36.952702');
INSERT INTO "django_migrations" ("id", "app", "name", "applied") VALUES (7, 'auth', '0002_alter_permission_name_max_length', '2026-04-08 20:35:36.968500');
INSERT INTO "django_migrations" ("id", "app", "name", "applied") VALUES (8, 'auth', '0003_alter_user_email_max_length', '2026-04-08 20:35:36.984796');
INSERT INTO "django_migrations" ("id", "app", "name", "applied") VALUES (9, 'auth', '0004_alter_user_username_opts', '2026-04-08 20:35:36.997396');
INSERT INTO "django_migrations" ("id", "app", "name", "applied") VALUES (10, 'auth', '0005_alter_user_last_login_null', '2026-04-08 20:35:37.014558');
INSERT INTO "django_migrations" ("id", "app", "name", "applied") VALUES (11, 'auth', '0006_require_contenttypes_0002', '2026-04-08 20:35:37.023678');
INSERT INTO "django_migrations" ("id", "app", "name", "applied") VALUES (12, 'auth', '0007_alter_validators_add_error_messages', '2026-04-08 20:35:37.039123');
INSERT INTO "django_migrations" ("id", "app", "name", "applied") VALUES (13, 'auth', '0008_alter_user_username_max_length', '2026-04-08 20:35:37.054726');
INSERT INTO "django_migrations" ("id", "app", "name", "applied") VALUES (14, 'auth', '0009_alter_user_last_name_max_length', '2026-04-08 20:35:37.070860');
INSERT INTO "django_migrations" ("id", "app", "name", "applied") VALUES (15, 'auth', '0010_alter_group_name_max_length', '2026-04-08 20:35:37.086616');
INSERT INTO "django_migrations" ("id", "app", "name", "applied") VALUES (16, 'auth', '0011_update_proxy_permissions', '2026-04-08 20:35:37.101949');
INSERT INTO "django_migrations" ("id", "app", "name", "applied") VALUES (17, 'auth', '0012_alter_user_first_name_max_length', '2026-04-08 20:35:37.117328');
INSERT INTO "django_migrations" ("id", "app", "name", "applied") VALUES (18, 'core', '0001_initial', '2026-04-08 20:35:37.131500');
INSERT INTO "django_migrations" ("id", "app", "name", "applied") VALUES (19, 'socios', '0001_initial', '2026-04-08 20:35:37.166620');
INSERT INTO "django_migrations" ("id", "app", "name", "applied") VALUES (20, 'creditos', '0001_initial', '2026-04-08 20:35:37.228603');
INSERT INTO "django_migrations" ("id", "app", "name", "applied") VALUES (21, 'cuentas', '0001_initial', '2026-04-08 20:35:37.261693');
INSERT INTO "django_migrations" ("id", "app", "name", "applied") VALUES (22, 'multas', '0001_initial', '2026-04-08 20:35:37.347352');
INSERT INTO "django_migrations" ("id", "app", "name", "applied") VALUES (23, 'sessions', '0001_initial', '2026-04-08 20:35:37.371578');
INSERT INTO "django_migrations" ("id", "app", "name", "applied") VALUES (24, 'core', '0002_alter_perfilusuario_rol_movimiento', '2026-04-11 02:52:25.254865');

-- multas_multa
INSERT INTO "multas_multa" ("id", "origen", "descripcion", "monto", "estado", "fecha_generacion", "fecha_pago", "comprobante_pago", "observaciones", "aplicada_por_id", "libreta_id", "periodo_id", "socio_id", "reunion_id") VALUES (1, 'mensualidad_atraso', 'Mensualidad Febrero pagada después del 20', 5, 'pendiente', '2026-04-08', NULL, '', '', 2, 5, 1, 2, NULL);
INSERT INTO "multas_multa" ("id", "origen", "descripcion", "monto", "estado", "fecha_generacion", "fecha_pago", "comprobante_pago", "observaciones", "aplicada_por_id", "libreta_id", "periodo_id", "socio_id", "reunion_id") VALUES (2, 'reunion_comportamiento', 'Reunión Enero: cámara apagada', 1, 'pendiente', '2026-04-08', NULL, '', '', 2, NULL, 1, 4, NULL);

-- multas_tipomulta
INSERT INTO "multas_tipomulta" ("id", "nombre", "descripcion", "monto", "aplica_a", "activo") VALUES (1, 'Atraso 11-20 min en reunión', '', 1, 'socio', TRUE);
INSERT INTO "multas_tipomulta" ("id", "nombre", "descripcion", "monto", "aplica_a", "activo") VALUES (2, 'Atraso 21+ min en reunión', '', 3, 'socio', TRUE);
INSERT INTO "multas_tipomulta" ("id", "nombre", "descripcion", "monto", "aplica_a", "activo") VALUES (3, 'Falta justificada (reunión)', '', 1, 'libreta', TRUE);
INSERT INTO "multas_tipomulta" ("id", "nombre", "descripcion", "monto", "aplica_a", "activo") VALUES (4, 'Falta injustificada (reunión)', '', 3, 'libreta', TRUE);
INSERT INTO "multas_tipomulta" ("id", "nombre", "descripcion", "monto", "aplica_a", "activo") VALUES (5, 'Comportamiento inadecuado (cámara, gorra, etc)', '', 1, 'socio', TRUE);
INSERT INTO "multas_tipomulta" ("id", "nombre", "descripcion", "monto", "aplica_a", "activo") VALUES (6, 'Mensualidad tardía (después del 20)', '', 5, 'libreta', TRUE);
INSERT INTO "multas_tipomulta" ("id", "nombre", "descripcion", "monto", "aplica_a", "activo") VALUES (7, 'Incumplimiento total al fin de mes', '', 20, 'libreta', TRUE);

-- socios_accesosocio
INSERT INTO "socios_accesosocio" ("id", "pin", "activo", "fecha_creacion", "ultimo_acceso", "socio_id") VALUES (1, '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', TRUE, '2026-04-09 02:01:38.997045', NULL, 1);
INSERT INTO "socios_accesosocio" ("id", "pin", "activo", "fecha_creacion", "ultimo_acceso", "socio_id") VALUES (2, '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', TRUE, '2026-04-09 02:01:39.009371', NULL, 2);
INSERT INTO "socios_accesosocio" ("id", "pin", "activo", "fecha_creacion", "ultimo_acceso", "socio_id") VALUES (3, '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', TRUE, '2026-04-09 02:01:39.021751', NULL, 3);
INSERT INTO "socios_accesosocio" ("id", "pin", "activo", "fecha_creacion", "ultimo_acceso", "socio_id") VALUES (4, '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', TRUE, '2026-04-09 02:01:39.034032', NULL, 4);
INSERT INTO "socios_accesosocio" ("id", "pin", "activo", "fecha_creacion", "ultimo_acceso", "socio_id") VALUES (5, '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', TRUE, '2026-04-09 02:01:39.047071', NULL, 5);

-- socios_aportemensual
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (1, 1, 2026, 20, 1, 1, 22, 'verificado', NULL, NULL, '', '', 1);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (2, 2, 2026, 20, 1, 1, 22, 'verificado', NULL, NULL, '', '', 1);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (3, 3, 2026, 20, 1, 1, 22, 'verificado', NULL, NULL, '', '', 1);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (4, 4, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 1);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (5, 5, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 1);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (6, 6, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 1);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (7, 7, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 1);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (8, 8, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 1);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (9, 9, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 1);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (10, 10, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 1);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (11, 11, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 1);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (12, 12, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 1);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (13, 1, 2026, 20, 1, 1, 22, 'verificado', NULL, NULL, '', '', 2);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (14, 2, 2026, 20, 1, 1, 22, 'verificado', NULL, NULL, '', '', 2);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (15, 3, 2026, 20, 1, 1, 22, 'verificado', NULL, NULL, '', '', 2);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (16, 4, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 2);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (17, 5, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 2);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (18, 6, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 2);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (19, 7, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 2);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (20, 8, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 2);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (21, 9, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 2);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (22, 10, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 2);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (23, 11, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 2);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (24, 12, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 2);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (25, 1, 2026, 20, 1, 1, 22, 'verificado', NULL, NULL, '', '', 3);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (26, 2, 2026, 20, 1, 1, 22, 'verificado', NULL, NULL, '', '', 3);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (27, 3, 2026, 20, 1, 1, 22, 'verificado', NULL, NULL, '', '', 3);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (28, 4, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 3);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (29, 5, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 3);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (30, 6, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 3);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (31, 7, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 3);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (32, 8, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 3);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (33, 9, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 3);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (34, 10, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 3);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (35, 11, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 3);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (36, 12, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 3);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (37, 1, 2026, 20, 1, 1, 22, 'verificado', NULL, NULL, '', '', 4);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (38, 2, 2026, 20, 1, 1, 22, 'verificado', NULL, NULL, '', '', 4);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (39, 3, 2026, 20, 1, 1, 22, 'verificado', NULL, NULL, '', '', 4);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (40, 4, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 4);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (41, 5, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 4);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (42, 6, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 4);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (43, 7, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 4);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (44, 8, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 4);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (45, 9, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 4);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (46, 10, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 4);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (47, 11, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 4);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (48, 12, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 4);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (49, 1, 2026, 20, 1, 1, 22, 'verificado', NULL, NULL, '', '', 5);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (50, 2, 2026, 20, 1, 1, 22, 'verificado', NULL, NULL, '', '', 5);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (51, 3, 2026, 20, 1, 1, 22, 'verificado', NULL, NULL, '', '', 5);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (52, 4, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 5);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (53, 5, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 5);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (54, 6, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 5);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (55, 7, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 5);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (56, 8, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 5);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (57, 9, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 5);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (58, 10, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 5);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (59, 11, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 5);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (60, 12, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 5);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (61, 1, 2026, 20, 1, 1, 22, 'verificado', NULL, NULL, '', '', 6);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (62, 2, 2026, 20, 1, 1, 22, 'verificado', NULL, NULL, '', '', 6);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (63, 3, 2026, 20, 1, 1, 22, 'verificado', NULL, NULL, '', '', 6);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (64, 4, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 6);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (65, 5, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 6);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (66, 6, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 6);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (67, 7, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 6);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (68, 8, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 6);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (69, 9, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 6);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (70, 10, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 6);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (71, 11, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 6);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (72, 12, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 6);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (73, 1, 2026, 20, 1, 1, 22, 'verificado', NULL, NULL, '', '', 7);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (74, 2, 2026, 20, 1, 1, 22, 'verificado', NULL, NULL, '', '', 7);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (75, 3, 2026, 20, 1, 1, 22, 'verificado', NULL, NULL, '', '', 7);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (76, 4, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 7);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (77, 5, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 7);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (78, 6, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 7);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (79, 7, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 7);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (80, 8, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 7);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (81, 9, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 7);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (82, 10, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 7);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (83, 11, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 7);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (84, 12, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 7);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (85, 1, 2026, 20, 1, 1, 22, 'verificado', NULL, NULL, '', '', 8);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (86, 2, 2026, 20, 1, 1, 22, 'verificado', NULL, NULL, '', '', 8);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (87, 3, 2026, 20, 1, 1, 22, 'verificado', NULL, NULL, '', '', 8);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (88, 4, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 8);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (89, 5, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 8);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (90, 6, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 8);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (91, 7, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 8);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (92, 8, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 8);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (93, 9, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 8);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (94, 10, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 8);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (95, 11, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 8);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (96, 12, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 8);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (97, 1, 2026, 20, 1, 1, 22, 'verificado', NULL, NULL, '', '', 9);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (98, 2, 2026, 20, 1, 1, 22, 'verificado', NULL, NULL, '', '', 9);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (99, 3, 2026, 20, 1, 1, 22, 'verificado', NULL, NULL, '', '', 9);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (100, 4, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 9);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (101, 5, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 9);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (102, 6, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 9);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (103, 7, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 9);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (104, 8, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 9);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (105, 9, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 9);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (106, 10, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 9);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (107, 11, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 9);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (108, 12, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 9);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (109, 1, 2026, 20, 1, 1, 22, 'verificado', NULL, NULL, '', '', 10);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (110, 2, 2026, 20, 1, 1, 22, 'verificado', NULL, NULL, '', '', 10);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (111, 3, 2026, 20, 1, 1, 22, 'verificado', NULL, NULL, '', '', 10);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (112, 4, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 10);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (113, 5, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 10);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (114, 6, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 10);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (115, 7, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 10);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (116, 8, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 10);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (117, 9, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 10);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (118, 10, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 10);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (119, 11, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 10);
INSERT INTO "socios_aportemensual" ("id", "mes", "anio", "monto_ahorro", "monto_loteria", "monto_cumpleanos", "monto_total", "estado", "fecha_reporte", "fecha_verificacion", "comprobante_referencia", "observacion", "libreta_id") VALUES (120, 12, 2026, 20, 1, 1, 22, 'pendiente', NULL, NULL, '', '', 10);

-- socios_libreta
INSERT INTO "socios_libreta" ("id", "numero", "estado", "fecha_inscripcion", "inscripcion_pagada", "fecha_inscripcion_pago", "saldo_ahorro", "observaciones", "periodo_id", "socio_id") VALUES (1, 1, 'activa', '2026-04-08', TRUE, '2026-01-10', 60, '', 1, 1);
INSERT INTO "socios_libreta" ("id", "numero", "estado", "fecha_inscripcion", "inscripcion_pagada", "fecha_inscripcion_pago", "saldo_ahorro", "observaciones", "periodo_id", "socio_id") VALUES (2, 2, 'activa', '2026-04-08', TRUE, '2026-01-10', 60, '', 1, 1);
INSERT INTO "socios_libreta" ("id", "numero", "estado", "fecha_inscripcion", "inscripcion_pagada", "fecha_inscripcion_pago", "saldo_ahorro", "observaciones", "periodo_id", "socio_id") VALUES (3, 3, 'activa', '2026-04-08', TRUE, '2026-01-10', 60, '', 1, 1);
INSERT INTO "socios_libreta" ("id", "numero", "estado", "fecha_inscripcion", "inscripcion_pagada", "fecha_inscripcion_pago", "saldo_ahorro", "observaciones", "periodo_id", "socio_id") VALUES (4, 4, 'activa', '2026-04-08', TRUE, '2026-01-10', 60, '', 1, 1);
INSERT INTO "socios_libreta" ("id", "numero", "estado", "fecha_inscripcion", "inscripcion_pagada", "fecha_inscripcion_pago", "saldo_ahorro", "observaciones", "periodo_id", "socio_id") VALUES (5, 5, 'activa', '2026-04-08', TRUE, '2026-01-10', 60, '', 1, 2);
INSERT INTO "socios_libreta" ("id", "numero", "estado", "fecha_inscripcion", "inscripcion_pagada", "fecha_inscripcion_pago", "saldo_ahorro", "observaciones", "periodo_id", "socio_id") VALUES (6, 6, 'activa', '2026-04-08', TRUE, '2026-01-10', 60, '', 1, 2);
INSERT INTO "socios_libreta" ("id", "numero", "estado", "fecha_inscripcion", "inscripcion_pagada", "fecha_inscripcion_pago", "saldo_ahorro", "observaciones", "periodo_id", "socio_id") VALUES (7, 7, 'activa', '2026-04-08', TRUE, '2026-01-10', 60, '', 1, 3);
INSERT INTO "socios_libreta" ("id", "numero", "estado", "fecha_inscripcion", "inscripcion_pagada", "fecha_inscripcion_pago", "saldo_ahorro", "observaciones", "periodo_id", "socio_id") VALUES (8, 8, 'activa', '2026-04-08', TRUE, '2026-01-10', 60, '', 1, 4);
INSERT INTO "socios_libreta" ("id", "numero", "estado", "fecha_inscripcion", "inscripcion_pagada", "fecha_inscripcion_pago", "saldo_ahorro", "observaciones", "periodo_id", "socio_id") VALUES (9, 9, 'activa', '2026-04-08', TRUE, '2026-01-10', 60, '', 1, 4);
INSERT INTO "socios_libreta" ("id", "numero", "estado", "fecha_inscripcion", "inscripcion_pagada", "fecha_inscripcion_pago", "saldo_ahorro", "observaciones", "periodo_id", "socio_id") VALUES (10, 10, 'activa', '2026-04-08', TRUE, '2026-01-10', 60, '', 1, 5);

-- socios_periodo
INSERT INTO "socios_periodo" ("id", "anio", "fecha_inicio", "fecha_cierre", "activo", "descripcion") VALUES (1, 2026, '2026-01-01', '2026-12-31', TRUE, '');

-- socios_socio
INSERT INTO "socios_socio" ("id", "cedula", "nombres", "apellidos", "fecha_nacimiento", "genero", "direccion", "ciudad", "telefono", "whatsapp", "email", "es_menor", "representante_nombre", "representante_cedula", "estado", "fecha_registro", "observaciones", "recomendado_por_id") VALUES (1, '1316078169', 'Mabel Adelaida', 'Bailón Rivas', '1985-03-15', 'F', 'Dirección registrada', 'Guayaquil', '0983109501', '', 'bailonmabel320@gmail.com', FALSE, '', '', 'activo', '2026-04-08', '', NULL);
INSERT INTO "socios_socio" ("id", "cedula", "nombres", "apellidos", "fecha_nacimiento", "genero", "direccion", "ciudad", "telefono", "whatsapp", "email", "es_menor", "representante_nombre", "representante_cedula", "estado", "fecha_registro", "observaciones", "recomendado_por_id") VALUES (2, '0910117829', 'Betty Mariela', 'Molina Cercado', '1979-07-22', 'F', 'Dirección registrada', 'Guayaquil', '0981886460', '', 'bettymolina049@gmail.com', FALSE, '', '', 'activo', '2026-04-08', '', NULL);
INSERT INTO "socios_socio" ("id", "cedula", "nombres", "apellidos", "fecha_nacimiento", "genero", "direccion", "ciudad", "telefono", "whatsapp", "email", "es_menor", "representante_nombre", "representante_cedula", "estado", "fecha_registro", "observaciones", "recomendado_por_id") VALUES (3, '1317867909', 'Carlos Junior', 'Zambrano Meza', '1990-11-08', 'M', 'Dirección registrada', 'Quito', '0964147894', '', 'juniorzambranomeza4321@gmail.com', FALSE, '', '', 'activo', '2026-04-08', '', NULL);
INSERT INTO "socios_socio" ("id", "cedula", "nombres", "apellidos", "fecha_nacimiento", "genero", "direccion", "ciudad", "telefono", "whatsapp", "email", "es_menor", "representante_nombre", "representante_cedula", "estado", "fecha_registro", "observaciones", "recomendado_por_id") VALUES (4, '0957640501', 'Zayda Arelis', 'Moreno Bailon', '1982-05-30', 'F', 'Dirección registrada', 'Quito', '0994787131', '', 'marelis675@gmail.com', FALSE, '', '', 'activo', '2026-04-08', '', NULL);
INSERT INTO "socios_socio" ("id", "cedula", "nombres", "apellidos", "fecha_nacimiento", "genero", "direccion", "ciudad", "telefono", "whatsapp", "email", "es_menor", "representante_nombre", "representante_cedula", "estado", "fecha_registro", "observaciones", "recomendado_por_id") VALUES (5, '0951750280', 'Steven Vidal', 'Piza Alvarez', '1988-09-14', 'M', 'Dirección registrada', 'Quito', '0989471195', '', 'steven_svpa@hotmail.com', FALSE, '', '', 'activo', '2026-04-08', '', NULL);

-- FOREIGN KEYS
ALTER TABLE "auth_group_permissions" ADD CONSTRAINT "fk_auth_group_permissions_permission_id" FOREIGN KEY ("permission_id") REFERENCES "auth_permission"("id");
ALTER TABLE "auth_group_permissions" ADD CONSTRAINT "fk_auth_group_permissions_group_id" FOREIGN KEY ("group_id") REFERENCES "auth_group"("id");
ALTER TABLE "auth_permission" ADD CONSTRAINT "fk_auth_permission_content_type_id" FOREIGN KEY ("content_type_id") REFERENCES "django_content_type"("id");
ALTER TABLE "auth_user_groups" ADD CONSTRAINT "fk_auth_user_groups_group_id" FOREIGN KEY ("group_id") REFERENCES "auth_group"("id");
ALTER TABLE "auth_user_groups" ADD CONSTRAINT "fk_auth_user_groups_user_id" FOREIGN KEY ("user_id") REFERENCES "auth_user"("id");
ALTER TABLE "auth_user_user_permissions" ADD CONSTRAINT "fk_auth_user_user_permissions_permission_id" FOREIGN KEY ("permission_id") REFERENCES "auth_permission"("id");
ALTER TABLE "auth_user_user_permissions" ADD CONSTRAINT "fk_auth_user_user_permissions_user_id" FOREIGN KEY ("user_id") REFERENCES "auth_user"("id");
ALTER TABLE "core_movimiento" ADD CONSTRAINT "fk_core_movimiento_registrado_por_id" FOREIGN KEY ("registrado_por_id") REFERENCES "auth_user"("id");
ALTER TABLE "core_perfilusuario" ADD CONSTRAINT "fk_core_perfilusuario_usuario_id" FOREIGN KEY ("usuario_id") REFERENCES "auth_user"("id");
ALTER TABLE "creditos_credito" ADD CONSTRAINT "fk_creditos_credito_socio_id" FOREIGN KEY ("socio_id") REFERENCES "socios_socio"("id");
ALTER TABLE "creditos_credito" ADD CONSTRAINT "fk_creditos_credito_periodo_id" FOREIGN KEY ("periodo_id") REFERENCES "socios_periodo"("id");
ALTER TABLE "creditos_credito" ADD CONSTRAINT "fk_creditos_credito_libreta_id" FOREIGN KEY ("libreta_id") REFERENCES "socios_libreta"("id");
ALTER TABLE "creditos_credito" ADD CONSTRAINT "fk_creditos_credito_aprobado_por_id" FOREIGN KEY ("aprobado_por_id") REFERENCES "auth_user"("id");
ALTER TABLE "creditos_multacredito" ADD CONSTRAINT "fk_creditos_multacredito_credito_id" FOREIGN KEY ("credito_id") REFERENCES "creditos_credito"("id");
ALTER TABLE "creditos_pagocredito" ADD CONSTRAINT "fk_creditos_pagocredito_verificado_por_id" FOREIGN KEY ("verificado_por_id") REFERENCES "auth_user"("id");
ALTER TABLE "creditos_pagocredito" ADD CONSTRAINT "fk_creditos_pagocredito_credito_id" FOREIGN KEY ("credito_id") REFERENCES "creditos_credito"("id");
ALTER TABLE "cuentas_rifamensual" ADD CONSTRAINT "fk_cuentas_rifamensual_registrado_por_id" FOREIGN KEY ("registrado_por_id") REFERENCES "auth_user"("id");
ALTER TABLE "cuentas_rifamensual" ADD CONSTRAINT "fk_cuentas_rifamensual_periodo_id" FOREIGN KEY ("periodo_id") REFERENCES "socios_periodo"("id");
ALTER TABLE "cuentas_rifamensual" ADD CONSTRAINT "fk_cuentas_rifamensual_libreta_ganadora_id" FOREIGN KEY ("libreta_ganadora_id") REFERENCES "socios_libreta"("id");
ALTER TABLE "django_admin_log" ADD CONSTRAINT "fk_django_admin_log_user_id" FOREIGN KEY ("user_id") REFERENCES "auth_user"("id");
ALTER TABLE "django_admin_log" ADD CONSTRAINT "fk_django_admin_log_content_type_id" FOREIGN KEY ("content_type_id") REFERENCES "django_content_type"("id");
ALTER TABLE "multas_asistenciareunion" ADD CONSTRAINT "fk_multas_asistenciareunion_reunion_id" FOREIGN KEY ("reunion_id") REFERENCES "multas_reunion"("id");
ALTER TABLE "multas_asistenciareunion" ADD CONSTRAINT "fk_multas_asistenciareunion_socio_id" FOREIGN KEY ("socio_id") REFERENCES "socios_socio"("id");
ALTER TABLE "multas_comportamientoreunion" ADD CONSTRAINT "fk_multas_comportamientoreunion_tipo_multa_id" FOREIGN KEY ("tipo_multa_id") REFERENCES "multas_tipomulta"("id");
ALTER TABLE "multas_comportamientoreunion" ADD CONSTRAINT "fk_multas_comportamientoreunion_reunion_id" FOREIGN KEY ("reunion_id") REFERENCES "multas_reunion"("id");
ALTER TABLE "multas_comportamientoreunion" ADD CONSTRAINT "fk_multas_comportamientoreunion_socio_id" FOREIGN KEY ("socio_id") REFERENCES "socios_socio"("id");
ALTER TABLE "multas_multa" ADD CONSTRAINT "fk_multas_multa_reunion_id" FOREIGN KEY ("reunion_id") REFERENCES "multas_reunion"("id");
ALTER TABLE "multas_multa" ADD CONSTRAINT "fk_multas_multa_socio_id" FOREIGN KEY ("socio_id") REFERENCES "socios_socio"("id");
ALTER TABLE "multas_multa" ADD CONSTRAINT "fk_multas_multa_periodo_id" FOREIGN KEY ("periodo_id") REFERENCES "socios_periodo"("id");
ALTER TABLE "multas_multa" ADD CONSTRAINT "fk_multas_multa_libreta_id" FOREIGN KEY ("libreta_id") REFERENCES "socios_libreta"("id");
ALTER TABLE "multas_multa" ADD CONSTRAINT "fk_multas_multa_aplicada_por_id" FOREIGN KEY ("aplicada_por_id") REFERENCES "auth_user"("id");
ALTER TABLE "multas_reunion" ADD CONSTRAINT "fk_multas_reunion_registrada_por_id" FOREIGN KEY ("registrada_por_id") REFERENCES "auth_user"("id");
ALTER TABLE "multas_reunion" ADD CONSTRAINT "fk_multas_reunion_periodo_id" FOREIGN KEY ("periodo_id") REFERENCES "socios_periodo"("id");
ALTER TABLE "socios_accesosocio" ADD CONSTRAINT "fk_socios_accesosocio_socio_id" FOREIGN KEY ("socio_id") REFERENCES "socios_socio"("id");
ALTER TABLE "socios_aportemensual" ADD CONSTRAINT "fk_socios_aportemensual_libreta_id" FOREIGN KEY ("libreta_id") REFERENCES "socios_libreta"("id");
ALTER TABLE "socios_libreta" ADD CONSTRAINT "fk_socios_libreta_socio_id" FOREIGN KEY ("socio_id") REFERENCES "socios_socio"("id");
ALTER TABLE "socios_libreta" ADD CONSTRAINT "fk_socios_libreta_periodo_id" FOREIGN KEY ("periodo_id") REFERENCES "socios_periodo"("id");
ALTER TABLE "socios_socio" ADD CONSTRAINT "fk_socios_socio_recomendado_por_id" FOREIGN KEY ("recomendado_por_id") REFERENCES "socios_socio"("id");

-- RESET SEQUENCES
SELECT setval(pg_get_serial_sequence('"auth_permission"', 'id'), 88);
SELECT setval(pg_get_serial_sequence('"auth_user"', 'id'), 2);
SELECT setval(pg_get_serial_sequence('"core_movimiento"', 'id'), 43);
SELECT setval(pg_get_serial_sequence('"core_perfilusuario"', 'id'), 2);
SELECT setval(pg_get_serial_sequence('"creditos_credito"', 'id'), 3);
SELECT setval(pg_get_serial_sequence('"creditos_pagocredito"', 'id'), 1);
SELECT setval(pg_get_serial_sequence('"django_content_type"', 'id'), 22);
SELECT setval(pg_get_serial_sequence('"django_migrations"', 'id'), 24);
SELECT setval(pg_get_serial_sequence('"multas_multa"', 'id'), 2);
SELECT setval(pg_get_serial_sequence('"multas_tipomulta"', 'id'), 7);
SELECT setval(pg_get_serial_sequence('"socios_accesosocio"', 'id'), 5);
SELECT setval(pg_get_serial_sequence('"socios_aportemensual"', 'id'), 120);
SELECT setval(pg_get_serial_sequence('"socios_libreta"', 'id'), 10);
SELECT setval(pg_get_serial_sequence('"socios_periodo"', 'id'), 1);
SELECT setval(pg_get_serial_sequence('"socios_socio"', 'id'), 5);
