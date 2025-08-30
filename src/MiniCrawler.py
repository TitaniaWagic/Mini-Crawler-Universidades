import requests
import time
import csv
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
from urllib.parse import urljoin, urlparse
import re # Para expresiones regulares, útil para robots.txt


console = Console()
VISITED = set()     
QUEUE = ["https://unae.edu.py/tv/"]
MAX_PAGES = 50     
DELAY_BETWEEN_REQUESTS = 1 
DOMAIN_TARGET = "unae.edu.py"


ROBOTS_RULES = {}


#Descarga y parsea el archivo robots.txt para un dominio dado. Almacena las reglas en ROBOTS_RULES.
def fetch_robots_txt(domain):
    
    robots_url = f"https://{domain}/robots.txt"
    console.log(f"Intentando descargar robots.txt de: {robots_url}")
    try:
        r = requests.get(robots_url, timeout=5, headers={'User-Agent': 'DataExplore-Crawler/1.0'})
        if r.status_code == 200:
            parse_robots_txt(r.text, domain)
            console.log(f"robots.txt para {domain} descargado y parseado.")
        elif r.status_code == 404:
            console.log(f"robots.txt no encontrado (404) para {domain}. Asumiendo todo permitido.")
            ROBOTS_RULES[domain] = {"allow": [], "disallow": []} # No hay reglas explícitas
        else:
            console.log(f"Error {r.status_code} al obtener robots.txt para {domain}.")
    except requests.exceptions.RequestException as e:
        console.log(f"[bold red]Error al descargar robots.txt para {domain}: {e}[/bold red]")
        ROBOTS_RULES[domain] = {"allow": [], "disallow": []} # En caso de error, asumimos permitido para no bloquear el crawler



#Parsea el contenido de robots.txt y almacena las reglas de 'Disallow' y 'Allow'.
def parse_robots_txt(content, domain):
    
    rules = {"allow": [], "disallow": []}
    current_user_agent = None
    processing_rules = False

    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        if line.lower().startswith("user-agent:"):
            ua = line.split(":", 1)[1].strip()
            if ua == "*" or ua.lower() == "dataexplore-crawler":
                current_user_agent = ua
                processing_rules = True
            else:
                processing_rules = False
        elif processing_rules:
            if line.lower().startswith("disallow:"):
                path = line.split(":", 1)[1].strip()
                if path:
                    rules["disallow"].append(path)
            elif line.lower().startswith("allow:"):
                path = line.split(":", 1)[1][0:].strip() # [0:] para asegurar que no se corta
                if path:
                    rules["allow"].append(path)
    ROBOTS_RULES[domain] = rules
    console.log(f"Reglas de robots.txt para {domain}: {rules}")


#Verifica si una URL está permitida según las reglas de robots.txt para su dominio. 
#Las reglas 'Allow' tienen precedencia sobre 'Disallow' si son más específicas.
def is_allowed_by_robots(url):
   
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    path = parsed_url.path

    if domain not in ROBOTS_RULES:
        fetch_robots_txt(domain) # Intentar obtener robots.txt si no lo tenemos

    rules = ROBOTS_RULES.get(domain, {"allow": [], "disallow": []})

    allow_patterns = [re.compile(re.escape(p).replace("\\*", ".*")) for p in rules.get("allow", [])]
    disallow_patterns = [re.compile(re.escape(p).replace("\\*", ".*")) for p in rules.get("disallow", [])]

    # Prioridad: La regla más específica y permitida gana
    # Primero, buscar si hay una regla de ALLOW que coincida
    for pattern in sorted(allow_patterns, key=lambda p: len(p.pattern), reverse=True): # Más específicas primero
        if pattern.match(path):
            return True

    # Luego, buscar si hay una regla de DISALLOW que coincida
    for pattern in sorted(disallow_patterns, key=lambda p: len(p.pattern), reverse=True): # Más específicas primero
        if pattern.match(path):
            return False

    return True # Si no hay reglas de disallow que afecten, la URL está permitida

#Verifica si la URL pertenece al dominio objetivo (DOMAIN_TARGET).
def is_same_domain(url):
   
    return urlparse(url).netloc.endswith(DOMAIN_TARGET)

#Bucle Principal del Crawler
if __name__ == "__main__":
    console.print(f"[bold cyan]Iniciando DataExplore Crawler para {DOMAIN_TARGET}[/bold cyan]")

    # Asegurarse de pre-cargar el robots.txt para el dominio inicial
    initial_domain = urlparse(QUEUE[0]).netloc
    if initial_domain not in ROBOTS_RULES:
        fetch_robots_txt(initial_domain)

    with open("crawler_log.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["#", "url", "status", "elapsed_s", "n_links_found", "is_allowed_by_robots"])

        table = Table(title=f"Tráfico HTTP - {DOMAIN_TARGET.upper()}", show_lines=True)
        table.add_column("#", style="cyan")
        table.add_column("URL solicitada", style="magenta")
        table.add_column("Código HTTP", style="green")
        table.add_column("Tiempo (s)", style="yellow")
        table.add_column("Enlaces", style="blue")
        table.add_column("Permitido", style="white")

        count = 0
        while QUEUE and count < MAX_PAGES:
            url_to_crawl = QUEUE.pop(0)

            if url_to_crawl in VISITED:
                continue

            # Respetar robots.txt
            if not is_allowed_by_robots(url_to_crawl):
                console.log(f"[bold red]🚫 URL no permitida por robots.txt: {url_to_crawl}[/bold red]")
                VISITED.add(url_to_crawl) #Marcar como visitada para no intentar de nuevo
                writer.writerow([count + 1, url_to_crawl, "BLOCKED", 0, 0, False])
                continue

            # Respetar el límite de 1 solicitud/s
            start_request_time = time.time()
            try:
                #Usar un User-Agent identificable
                r = requests.get(url_to_crawl, timeout=10, headers={'User-Agent': 'DataExplore-Crawler/1.0'})
                end_request_time = time.time()

                status_code = r.status_code
                response_time = round(end_request_time - start_request_time, 2)

                soup = BeautifulSoup(r.text, "html.parser")

                # Extraer enlaces y filtrar por el mismo dominio
                found_links = []
                for a_tag in soup.select("a[href]"):
                    href = a_tag.get("href")
                    if href:
                        full_url = urljoin(url_to_crawl, href)
                        # Solo añadir a la cola si está en el mismo dominio objetivo
                        if is_same_domain(full_url):
                            found_links.append(full_url)

                # Añadir enlaces a la cola si no han sido visitados y no están ya en cola
                # Limitar el número de enlaces para evitar una explosión de la cola
                for link in found_links[:100]: # Limitar a 100 nuevos enlaces por página
                    if link not in VISITED and link not in QUEUE:
                        QUEUE.append(link)

                n_links_detected = len(found_links)

            except requests.exceptions.RequestException as e:
                status_code, response_time, n_links_detected = "ERR", round(time.time() - start_request_time, 2), 0
                console.log(f"[bold red]Error al acceder {url_to_crawl}: {e}[/bold red]")
            except Exception as e:
                status_code, response_time, n_links_detected = "ERR", round(time.time() - start_request_time, 2), 0
                console.log(f"[bold red]Error inesperado con {url_to_crawl}: {e}[/bold red]")

            VISITED.add(url_to_crawl)
            count += 1

            # Imprimir en consola los detalles solicitados
            console.log(f"\n[bold green]URL solicitada:[/bold green] {url_to_crawl}")
            console.log(f"[bold green]Código HTTP:[/bold green] {status_code}")
            console.log(f"[bold green]Tiempo de respuesta:[/bold green] {response_time}s")
            console.log(f"[bold green]Nº enlaces detectados:[/bold green] {n_links_detected}")
            console.log("-" * 60)

            # Actualizar tabla de Rich
            table.add_row(
                str(count),
                url_to_crawl[:70] + "..." if len(url_to_crawl) > 70 else url_to_crawl, # Truncar para la tabla
                str(status_code),
                str(response_time),
                str(n_links_detected),
                "[green]Sí[/green]" if is_allowed_by_robots(url_to_crawl) else "[red]No[/red]" # Aunque ya lo filtramos, es informativo
            )
            console.clear()
            console.print(table)

            # Escribir en el log CSV
            writer.writerow([count, url_to_crawl, status_code, response_time, n_links_detected, True]) # is_allowed_by_robots siempre True aquí, porque ya lo bloqueamos antes si no lo era

            # Control de tiempo para asegurar 1 solicitud/s
            time_elapsed_since_start = time.time() - start_request_time
            sleep_duration = max(0, DELAY_BETWEEN_REQUESTS - time_elapsed_since_start)
            if sleep_duration > 0:
                time.sleep(sleep_duration)

    console.print(f"\n[bold green]Rastreo completado para {DOMAIN_TARGET}. Se visitaron {count} páginas.[/bold green]")
    console.print("Los resultados se han guardado en [bold cyan]crawler_log.csv[/bold cyan]")
