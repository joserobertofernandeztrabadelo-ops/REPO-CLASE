#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Create venv if needed
if [ ! -d ".venv" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv .venv
fi

source .venv/bin/activate

# Install dependencies
pip install -q -r requirements.txt

# Check Google auth
if [ ! -f "token.json" ]; then
    echo ""
    echo "⚠️  No hay autenticación de Google configurada."
    echo "   Ejecuta: python auth.py"
    echo "   (Puedes hacerlo después; la app funciona sin importación de Sheets)"
    echo ""
fi

echo "🚀 Iniciando Presupuesto Familiar en http://localhost:8000"
echo "   Pulsa Ctrl+C para detener"
echo ""

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
