from google_auth_oauthlib.flow import InstalledAppFlow

# Configuración
CLIENT_ID = "844910494582-hc6hgprnsl4p3dp6nepevr4fg5ent2jr.apps.googleusercontent.com"
CLIENT_SECRET = "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"
SCOPES = ['https://www.googleapis.com/auth/adwords']

flow = InstalledAppFlow.from_client_config(
    {
        "installed": {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://accounts.google.com/o/oauth2/token",
            "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob"]
        }
    },
    scopes=SCOPES
)

credentials = flow.run_local_server(port=0)  # Abrirá tu navegador para autenticarte
print("Refresh token:", credentials.refresh_token)  # ¡Copia este valor!