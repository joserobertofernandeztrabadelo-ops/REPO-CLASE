# App Presupuesto Familiar — v1.0 inicial

**Fecha:** 2026-06-28 17:00  
**Tipo:** Feature

## Qué se hizo

Construcción completa de la aplicación web local de gestión de presupuesto familiar, basada en el briefing `BRIEFING_CLAUDE_CODE.md` del Google Drive del usuario.

**Backend (FastAPI + SQLite):**
- Modelos: `Account`, `Movement`, `Budget`
- Import desde Google Sheets (CaixaBank y Santander) con deduplicación por hash MD5
- CRUD de movimientos manuales (Revolut)
- Resumen mensual y anual con desglose por categoría
- Vista especial Tenis Lucía
- Presupuesto definible por categoría y mes
- Exportación CSV con BOM (compatible con Excel)

**Frontend (SPA sin build step):**
- Alpine.js para reactividad
- Tailwind CSS (CDN) para estilos
- Chart.js para gráficas (donut categorías + barras presupuesto vs real)
- 6 vistas: Resumen, Movimientos, Cuentas, Presupuesto, Tenis Lucía, Importar
- Badge visual para meses de paga extra (junio y diciembre)
- Selector de mes/año en sidebar

**Integración Google Sheets:**
- OAuth 2.0 con `gspread` + `google-auth-oauthlib`
- Script `auth.py` para autenticación inicial (ejecutar 1 vez)
- Parsers para estructura CaixaBank y Santander con sus columnas específicas
- Mapeo automático de CONCEPTO → categoría

## Qué se modificó

- `finanzas/` — directorio nuevo con toda la aplicación
- `docs/prd.md` — rellenado con contexto del proyecto
- `docs/architecture.md` — stack técnico, endpoints API, decisiones
- `docs/data-model.md` — esquema de las 3 tablas SQLite

## Por qué

Primera versión completa partiendo del briefing del usuario. El usuario tenía Google Drive y GitHub conectados en Claude Code; la app corre localmente en su Mac y no necesita servidor externo ni base de datos en la nube.
