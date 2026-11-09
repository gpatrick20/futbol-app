# Migraciones de la base de datos

La migración inicial crea las nueve tablas del MVP. No ejecutarla más de una vez sobre la misma base ni usar create_all para sustituir el historial de migraciones. Guardar este archivo en GitHub no ejecuta SQL en Supabase. La aplicación de la migración se realiza como un paso separado y se registra con Supabase apply_migration.

## Acceso

La autenticación actual pertenece a FastAPI, no a Supabase Auth. RLS está habilitado sin políticas para clientes y se revocan permisos de anon y authenticated sobre estas tablas. El frontend debe usar FastAPI; nunca debe recibir la contraseña PostgreSQL. La conexión privilegiada del backend requiere autorización por endpoint y no queda protegida automáticamente por RLS.

## Decisiones iniciales

Las fechas del partido pueden ser NULL durante la votación; el modelo SQLAlchemy debe ajustarse para reflejarlo. Las cuotas usan numeric(10,2); los modelos deben usar Decimal en lugar de float. Las restricciones CHECK y UNIQUE deben reflejarse en los modelos antes de generar futuras migraciones con Alembic. Esta migración no configura Alembic. Los roles, estados y formatos válidos están definidos mediante CHECK.

No guarda credenciales ni crea usuarios de prueba.
