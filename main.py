# main.py
import requests
import json
from datetime import datetime

# === CONFIGURACIÓN ===
REDMINE_URL = "https://gesproy.pagina.cu"
PROJECT_IDENTIFIER = "ps211lh010_001"
WIKI_PAGE_TITLE = "Referencias_academicas"
REDMINE_API_KEY = "TU_API_KEY_AQUI"  # Será reemplazada por GitHub Secrets

# === BÚSQUEDA CIENTÍFICA ===
SEMANTIC_SCHOLAR_QUERY = (
    "digital transformation environmental information system open data "
    "geospatial platform climate change sustainability public sector"
)

HEADERS = {
    "User-Agent": "SIA-Cuba-Digital/1.0 (Contact: sia-digital@midireccion.cu)"
}

# ================================
#       FUNCIONES
# ================================

def buscar_papers(query, limit=6):
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": query,
        "limit": limit,
        "fields": "title,authors,year,abstract,url,citationCount,journal",
        "year": "2018-2025"
    }
    try:
        print("📡 Buscando en Semantic Scholar...")
        response = requests.get(url, params=params, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {len(data['data'])} artículos encontrados.")
            return data
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error de conexión: {str(e)}")
        return None

def formatear_papers_markdown(papers_data):
    hoy = datetime.now().strftime("%d/%m/%Y %H:%M")
    md = f"""# Referencias Académicas - Transformación Digital del SIA

> Actualizado automáticamente el {hoy} (via GitHub Actions)

Artículos científicos relevantes para el **Sistema de Información Ambiental de Cuba**.

---

"""
    papers = papers_data.get("data", [])
    if not papers:
        md += "❌ No se encontraron artículos científicos recientes.\n"
        return md

    for i, paper in enumerate(papers, 1):
        title = paper.get("title", "Sin título")
        url = paper.get("url", "#")
        year = paper.get("year", "N/A")
        citations = paper.get("citationCount", 0)
        journal = paper.get("journal", {}) or {}
        journal_name = journal.get("name", "Sin revista")
        abstract = (paper.get("abstract") or "No disponible")[:350] + "..."

        authors = ", ".join([a["name"] for a in paper.get("authors", [])[:4]])
        if len(paper.get("authors", [])) > 4:
            authors += " et al."

        md += f"""
### {i}. {title}

- **Autores:** {authors}
- **Año:** {year} | **Revista:** {journal_name}
- **Citas:** {citations}
- **Resumen:** {abstract}
- [🔗 Ver artículo en Semantic Scholar]({url})

---

"""
    return md

def actualizar_wiki_redmine(contenido):
    url = f"{REDMINE_URL}/projects/{PROJECT_IDENTIFIER}/wiki/{WIKI_PAGE_TITLE}.json"
    headers = {
        "Content-Type": "application/json",
        "X-Redmine-API-Key": REDMINE_API_KEY
    }
    data = {
        "wiki_page": {
            "text": contenido,
            "comments": f"Actualización automática - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        }
    }
    try:
        response = requests.put(url, json=data, headers=headers, timeout=15)
        if response.status_code in [200, 201]:
            print("✅ Éxito: Página del wiki actualizada.")
            return True
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error al conectar con Redmine: {str(e)}")
        return False

# === EJECUCIÓN ===
def main():
    print("🚀 Iniciando actualización de referencias científicas...\n")
    resultados = buscar_papers(SEMANTIC_SCHOLAR_QUERY)
    
    if not resultados:
        print("❌ No se pudieron obtener datos. Verifica la conexión o la API.")
        return
    
    contenido = formatear_papers_markdown(resultados)
    
    print("📝 Enviando a Redmine...")
    if actualizar_wiki_redmine(contenido):
        print("🎉 ¡Proceso completado con éxito!")
    else:
        print("⚠️ Falló la actualización en Redmine.")

if __name__ == "__main__":
    main()
