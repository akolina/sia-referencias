import os
import requests
from datetime import datetime

# Parámetros de configuración
SEMANTIC_SCHOLAR_QUERY = "inteligencia artificial en salud"
REDMINE_URL = os.getenv("REDMINE_URL")
REDMINE_API_KEY = os.getenv("REDMINE_API_KEY")
PROJECT_IDENTIFIER = "sia"
WIKI_PAGE_TITLE = "referencias"
LOG_FILE = "log.txt"

def log(mensaje):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {mensaje}\n")
    print(mensaje)

def buscar_papers(query):
    log(f"🔍 Buscando papers para: '{query}'")
    url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={query}&limit=5&fields=title,authors,url,year"
    response = requests.get(url)
    if response.status_code != 200:
        log(f"❌ Error al buscar papers: {response.status_code}")
        return []
    data = response.json()
    log(f"✅ {len(data.get('data', []))} papers encontrados.")
    return data.get("data", [])

def formatear_papers_markdown(papers):
    markdown = "# Referencias científicas\n\n"
    for paper in papers:
        autores = ", ".join([a["name"] for a in paper.get("authors", [])])
        markdown += f"- **{paper['title']}** ({paper['year']}) — {autores}\n  [Ver artículo]({paper['url']})\n\n"
    return markdown

def actualizar_wiki_redmine(contenido_md):
    log("📤 Actualizando página wiki en Redmine...")
    url = f"{REDMINE_URL}/projects/{PROJECT_IDENTIFIER}/wiki/{WIKI_PAGE_TITLE}.json"
    headers = {
        "X-Redmine-API-Key": REDMINE_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "wiki_page": {
            "text": contenido_md
        }
    }
    response = requests.put(url, json=payload, headers=headers)
    if response.status_code == 200:
        log("✅ Wiki actualizada correctamente.")
    else:
        log(f"❌ Error al actualizar wiki: {response.status_code} - {response.text}")

if __name__ == "__main__":
    log("🚀 Inicio de ejecución del script")
    papers_data = buscar_papers(SEMANTIC_SCHOLAR_QUERY)
    if papers_data:
        contenido_md = formatear_papers_markdown(papers_data)
        actualizar_wiki_redmine(contenido_md)
    else:
        log("⚠️ No se encontraron papers.")
    log("🏁 Fin de ejecución\n")
