# Arquitectura técnica

## Stack

| Capa | Tecnología |
|------|------------|
| Backend | Python 3.11+ · FastAPI |
| Base de datos | SQLite (SQLAlchemy ORM) |
| Frontend | HTML + Tailwind CSS (CDN) + Alpine.js (CDN) + Chart.js (CDN) |
| Google Sheets | gspread + google-auth-oauthlib (OAuth 2.0) |
| Servidor | uvicorn |
| Gestor de paquetes | pip + venv |

No hay build step. El frontend son archivos estáticos servidos por FastAPI.

---

## Estructura de carpetas

```
finanzas/
├── app/
│   ├── main.py              # FastAPI app, CORS, routes, static files
│   ├── database.py          # SQLAlchemy engine + session + Base
│   ├── models.py            # Account, Movement, Budget
│   ├── categories.py        # Mapeo CONCEPTO → categoría, metadatos
│   ├── routers/
│   │   ├── movements.py     # CRUD, summary, tennis endpoints
│   │   ├── accounts.py      # Account list + movements por cuenta
│   │   ├── budget.py        # Budget CRUD por mes/categoría
│   │   ├── sheets.py        # Import desde Google Sheets
│   │   └── export.py        # CSV download
│   └── services/
│       └── google_sheets.py # gspread client, parsers CaixaBank/Santander
├── static/
│   ├── index.html           # SPA con Alpine.js
│   └── app.js               # Estado, llamadas API, charts
├── data/                    # SQLite DB (gitignored)
│   └── finanzas.db
├── auth.py                  # Setup OAuth Google (ejecutar 1 vez)
├── credentials.json         # OAuth client secret (gitignored)
├── token.json               # OAuth token (gitignored)
├── requirements.txt
└── start.sh                 # Arranque con venv
```

---

## API endpoints

### Movimientos
- `GET /api/movements/` — lista filtrable (year, month, account, category)
- `POST /api/movements/` — crear movimiento manual (Revolut)
- `PATCH /api/movements/{id}/category` — cambiar categoría
- `DELETE /api/movements/{id}` — borrar movimiento manual
- `GET /api/movements/summary/{year}/{month}` — totales y desglose por categoría
- `GET /api/movements/tennis/{year}/{month}` — desglose Tenis Lucía

### Cuentas
- `GET /api/accounts/` — lista con saldos
- `GET /api/accounts/{code}/movements` — movimientos de una cuenta

### Presupuesto
- `GET /api/budget/{year}/{month}` — presupuesto del mes
- `POST /api/budget/` — crear/actualizar entrada de presupuesto
- `DELETE /api/budget/{year}/{month}/{category}` — eliminar entrada

### Importación
- `POST /api/import/sheets` — importa CaixaBank + Santander desde Google Sheets
- `GET /api/import/status` — estado de autenticación Google

### Exportación
- `GET /api/export/csv?year=&month=` — descarga CSV del mes

### Misc
- `GET /api/categories` — lista de categorías con metadatos (color, icon)

---

## Modelo de datos

Ver `docs/data-model.md`

---

## Decisiones técnicas relevantes

**Deduplicación de movimientos**: hash MD5 de `account|date|amount|description[:80]`. Permite reimportar los mismos sheets sin duplicar.

**OAuth Google**: token almacenado en `token.json` local. El usuario ejecuta `python auth.py` una vez; después el servidor refresca el token automáticamente.

**Sin build step**: el frontend usa CDN (Tailwind, Alpine.js, Chart.js). Simplicidad máxima para una app personal local.

**Ejecución local**: la app corre en `localhost:8000`. No tiene ningún mecanismo de autenticación de usuario.
