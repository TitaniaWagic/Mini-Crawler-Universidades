# Mini-Crawler-Universidades
Prototipo de agente crawler desarrollado para la empresa ficticia DataExplorer. Este agente rastrea sitios web de universidades paraguayas y muestra en tiempo real el tráfico HTTP, generando métricas de rendimiento y respetando las políticas de crawling.

Actualmente, el crawler está configurado para rastrear `www.unae.edu.py`.


## Características

*   **Rastreo Adaptable:** Configurado para `www.une.edu.py`. Fácilmente configurable para otros dominios cambiando `DOMAIN_TARGET` en `main_crawler.py`.
*   **Respeto a `robots.txt`:** Descarga y parsea el archivo `robots.txt` del sitio web objetivo, respetando las directivas `Disallow` y `Allow`.
*   **Control de Frecuencia:** Limita las solicitudes a un máximo de 1 por segundo para evitar sobrecargar el servidor del sitio web.
*   **Logging Detallado:**
    *   Imprime en consola: URL solicitada, código HTTP, tiempo de respuesta y número de enlaces detectados.
    *   Genera un archivo `crawler_log.csv` con un registro de todas las páginas rastreadas, su estado y métricas.
*   **Extracción de Enlaces:** Identifica y sigue enlaces internos dentro del dominio objetivo.
*   **Límite de Páginas:** El número máximo de páginas a rastrear es configurable (`MAX_PAGES`).

## Instalación

1.  Clona este repositorio (o descarga los archivos).
2.  Navega a la carpeta raíz del proyecto.
3.  Crea un entorno virtual (opcional pero recomendado):
    ```bash
    python -m venv venv
    source venv/bin/activate  # En Linux/macOS
    .\venv\Scripts\activate   # En Windows
    ```
4.  Instala las dependencias necesarias:
    ```bash
    pip install -r requirements.txt
    ```

## Uso

Para ejecutar el crawler, navega a la carpeta `/src` y ejecuta el script principal:

```bash
cd src
python main_crawler.py
