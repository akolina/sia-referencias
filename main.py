import os
import requests
import time
from datetime import datetime

# Configuración
SEMANTIC_SCHOLAR_QUERY = "inteligencia artificial en medio ambiente"
REDMINE_URL = os.getenv("REDMINE_URL")
REDMINE_API_KEY = os.getenv("REDMINE_API_KEY")
PROJECT_IDENTIFIER = "sia"
WIKI_PAGE_TITLE = "referencias"
LOG_FILE = "log.txt"
LIMIT_ARTICULOS = 3
ARCHIVO_DUPLICADOS = "papers_guardados.txt"

def log(mensaje):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {mensaje}\n")
    print(mensaje)

def buscar_papers(tema, limite):
    url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={tema}&limit={limite}&fields=title,authors,year,url"
    headers = {"User-Agent": "sia-referencias-bot"}
    
    for intento in range(5):
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json().get("data", [])
        
        elif response.status_code == 429:
            espera = 10 * (intento + 1)
            print(f"❌ Error 429: Demasiadas solicitudes. Esperando {espera} segundos...")
            time.sleep(espera)
        
        else:
            print(f"⚠️ Error inesperado ({response.status_code}): {response.text}")
            break
    
    return []


def filtrar_papers_nuevos(papers):
    if not os.path.exists(ARCHIVO_DUPLICADOS):
        with open(ARCHIVO_DUPLICADOS, "w") as f:
            pass

    with open(ARCHIVO_DUPLICADOS, "r") as f:
        titulos_guardados = set(line.strip() for line in f)

    nuevos = []
    for paper in papers:
        if paper["title"] not in titulos_guardados:
            nuevos.append(paper)
            titulos_guardados.add(paper["title"])

    with open(ARCHIVO_DUPLICADOS, "a") as f:
        for paper in nuevos:
            f.write(paper["title"] + "\n")

    log(f"🧹 Filtrados {len(nuevos)} papers nuevos.")
    return nuevos

def formatear_papers_markdown(papers):
    markdown = "# Referencias científicas\n\n"
    for paper in papers:
        autores = ", ".join([a["name"] for a in paper.get("authors", [])])
        markdown += f"- **{paper['title']}** ({paper['year']}) — {autores}\n  [Ver artículo]({paper['url']})\n\n"
    return markdown

def guardar_historico_markdown(contenido_md):
    fecha = datetime.now().strftime("%Y-%m-%d")
    nombre_archivo = f"referencias_{fecha}.md"
    with open(nombre_archivo, "w", encoding="utf-8") as f:
        f.write(contenido_md)
    log(f"🗂️ Archivo histórico guardado: {nombre_archivo}")

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
    try:
        response = requests.put(url, json=payload, headers=headers)
        if response.status_code == 200:
            log("✅ Wiki actualizada correctamente.")
        else:
            log(f"❌ Error al actualizar wiki: {response.status_code} - {response.text}")
    except Exception as e:
        log(f"❌ Excepción al actualizar wiki: {str(e)}")

if __name__ == "__main__":
    log("🚀 Inicio de ejecución del script")
    papers_data = buscar_papers(SEMANTIC_SCHOLAR_QUERY, LIMIT_ARTICULOS)
    if papers_data:
        papers_nuevos = filtrar_papers_nuevos(papers_data)
        if papers_nuevos:
            contenido_md = formatear_papers_markdown(papers_nuevos)
            guardar_historico_markdown(contenido_md)
            actualizar_wiki_redmine(contenido_md)
        else:
            log("⚠️ No hay papers nuevos para agregar.")
    else:
        log("⚠️ No se encontraron papers.")
    log("🏁 Fin de ejecución\n")
