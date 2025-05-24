from utils.auth import *
from flask import Flask, render_template
from flask import Flask, request, redirect, url_for, session
import os

# Rutas absolutas de templates y static
template_dir = os.path.abspath('../frontend/templates')
static_dir = os.path.abspath('../frontend')  # Apuntamos a la carpeta 'resources'

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

@app.route("/")
def inicio():

    return render_template("index.html")

@app.route("/buscar", methods=['POST'])
def buscar():
    #negocio = request.form.get('negocio')
    # keyword = request.form.get('keyword')
    # print(f"Negocio: {negocio}, Keyword: {keyword}")
     # 0. Autenticación
    creds = load_credentials_from_file(CREDENTIALS_FILE)

    if not creds or not creds.valid:
        authorization_url = generate_auth_url_cli()
        print(f"Por favor, visita la siguiente URL en tu navegador y autoriza la aplicación:\n{authorization_url}\n")
        auth_code = input("Introduce el código de autorización que recibiste: ")
        token = exchange_code_for_token_cli(auth_code)
        if token:
            save_credentials_to_file(CREDENTIALS_FILE, token)
            creds = load_credentials_from_file(CREDENTIALS_FILE)
        else:
            print("Error al obtener el token de acceso.")
            return

    if creds and creds.expired and creds.refresh_token:
        creds = refresh_access_token_cli(creds)
        save_credentials_to_file(CREDENTIALS_FILE, json.loads(creds.to_json()))

    client = get_ads_client_cli(creds)
    if not client:
        print("Error al inicializar el cliente de Google Ads.")
        return
    return render_template("loading.html")

if __name__ == "__main__":
    app.run(debug=True)
