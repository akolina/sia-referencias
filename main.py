import os
import requests

# Cargar variables de entorno
REDMINE_URL = os.getenv("REDMINE_URL")
REDMINE_API_KEY = os.getenv("REDMINE_API_KEY")

# Validar que las variables estén definidas
if not REDMINE_URL or not REDMINE_API_KEY:
    print("❌ Error: REDMINE_URL o REDMINE_API_KEY no están definidos.")
    exit(1)

# 🔧 Definir ID del proyecto y nombre de la página wiki
project_id = "ps211lh010_001"
wiki_page = "Referencias_academicas"
url_wiki = f"{REDMINE_URL}/projects/{project_id}/wiki/{wiki_page}.json"

# Encabezados para autenticación
headers = {
    "X-Redmine-API-Key": REDMINE_API_KEY,
    "Content-Type": "application/json"
}

# Verificar si la página existe
response = requests.get(url_wiki, headers=headers)

if response.status_code == 200:
    print("✅ Página wiki encontrada. Procediendo a actualizar...")

    # Contenido nuevo en formato Markdown
    nuevo_contenido = """
## Referencias Académicas

- Pérez, J. (2023). *Gestión ambiental en zonas urbanas*. Editorial Ciencia Verde.
- Rodríguez, M. & Torres, L. (2022). *Indicadores de sostenibilidad*. Revista Medioambiente, 15(2), 45–60.
- CITMA (2021). *Informe técnico sobre biodiversidad en Cuba*. Ministerio de Ciencia, Tecnología y Medio Ambiente.
"""

    # Datos para actualizar la página
    payload = {
        "wiki_page": {
            "text": nuevo_contenido,
            "comments": "Actualización automática semanal de referencias académicas"
        }
    }

    # Enviar actualización
    put_response = requests.put(url_wiki, headers=headers, json=payload)

    if put_response.status_code == 200:
        print("✅ Página wiki actualizada correctamente.")
    else:
        print(f"⚠️ Error al actualizar la página wiki. Código: {put_response.status_code}")
        print(put_response.text)

else:
    print(f"⚠️ No se pudo acceder a la página wiki. Código de estado: {response.status_code}")
    print(response.text)

