# Presupuesto Familiar

App web local para gestionar el presupuesto del hogar. Lee movimientos de Google Sheets (CaixaBank y Santander), permite entrada manual de Revolut y guarda todo en SQLite.

---

## Requisitos

- Python 3.11+
- Acceso a las Google Sheets de CaixaBank y Santander

---

## Instalación y arranque

```bash
cd finanzas
chmod +x start.sh
./start.sh
```

El script crea el entorno virtual, instala dependencias y arranca el servidor en `http://localhost:8000`.

---

## Configurar Google Sheets (primer uso)

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un proyecto → Activa la **API de Google Sheets**
3. Credenciales → Crear credencial → **ID de cliente OAuth 2.0** → Tipo: **Aplicación de escritorio**
4. Descarga el JSON y guárdalo como `finanzas/credentials.json`
5. Ejecuta:
   ```bash
   source .venv/bin/activate
   python auth.py
   ```
   Se abrirá el navegador para autorizar. El token se guarda en `token.json`.
6. Reinicia el servidor (`./start.sh`)
7. En la app, ve a **Importar** → **Importar desde Google Sheets**

A partir de aquí el token se renueva solo. Solo necesitas repetir el paso 5 si el token caduca o revoces el acceso.

---

## Estructura

```
app/            Backend FastAPI
static/         Frontend (HTML + Alpine.js + Chart.js)
data/           SQLite database (gitignored)
auth.py         Setup OAuth Google (ejecutar 1 vez)
start.sh        Script de arranque
```

---

## Datos sensibles (gitignored)

- `credentials.json` — client secret de Google OAuth
- `token.json` — token de acceso/refresh
- `data/` — base de datos SQLite con todos los movimientos
