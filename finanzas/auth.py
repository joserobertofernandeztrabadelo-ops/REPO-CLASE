"""
Ejecuta este script UNA VEZ para autenticarte con Google Sheets.
Abrirá el navegador para que inicies sesión con tu cuenta de Google.
El token se guardará en token.json y la app lo usará automáticamente.

Uso:
    python auth.py
"""
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
CREDENTIALS_FILE = Path(__file__).parent / "credentials.json"
TOKEN_FILE = Path(__file__).parent / "token.json"


def main():
    if not CREDENTIALS_FILE.exists():
        print("❌ No se encontró credentials.json")
        print()
        print("Pasos:")
        print("1. Ve a https://console.cloud.google.com/")
        print("2. Crea un proyecto (o usa uno existente)")
        print("3. Activa la API de Google Sheets")
        print("4. Ve a Credenciales → Crear credencial → ID de cliente OAuth 2.0")
        print("5. Tipo de aplicación: Aplicación de escritorio")
        print("6. Descarga el JSON y guárdalo como credentials.json en esta carpeta")
        return

    flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
    creds = flow.run_local_server(port=0)

    TOKEN_FILE.write_text(creds.to_json())
    print(f"✅ Autenticación completada. Token guardado en {TOKEN_FILE}")


if __name__ == "__main__":
    main()
