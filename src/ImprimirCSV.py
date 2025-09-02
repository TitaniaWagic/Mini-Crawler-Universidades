import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Configuración de estilo
plt.style.use('default')
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.facecolor'] = '#F8F9FA'
plt.rcParams['grid.color'] = '#DEE2E6'
plt.rcParams['grid.alpha'] = 0.7

# Leer datos desde el CSV del crawler
df = pd.read_csv("crawler_log.csv")

# Asegurar que las columnas tengan los nombres esperados
if "#" not in df.columns:
    df.reset_index(inplace=True)
    df.rename(columns={"index": "#"}, inplace=True)

# Procesar métricas
total_tiempo = df['elapsed_s'].sum()
paginas_por_minuto = (len(df) / total_tiempo) * 60
tiempo_acumulado = df['elapsed_s'].cumsum()
paginas_por_minuto_tiempo_real = [(i+1) / (t/60) for i, t in enumerate(tiempo_acumulado)]

# Crear gráficas
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))

# Gráfica 1: Tiempo de respuesta
ax1.plot(df['#'], df['elapsed_s'], 'b-', marker='o', markersize=4)
ax1.set_title('Tiempo de Respuesta por Página', fontsize=14, fontweight='bold')
ax1.set_xlabel('Número de Página')
ax1.set_ylabel('Tiempo (segundos)')
ax1.grid(True, alpha=0.3)
promedio_tiempo = df['elapsed_s'].mean()
ax1.axhline(y=promedio_tiempo, color='r', linestyle='--', alpha=0.7, label=f'Promedio: {promedio_tiempo:.2f}s')
ax1.legend()

# Gráfica 2: Enlaces encontrados
bars = ax2.bar(df['#'], df['n_links_found'], alpha=0.7, color='green')
ax2.set_title('Enlaces Encontrados por Página', fontsize=14, fontweight='bold')
ax2.set_xlabel('Número de Página')
ax2.set_ylabel('Número de Enlaces')
ax2.grid(True, alpha=0.3, axis='y')
max_links_idx = df['n_links_found'].idxmax()
bars[max_links_idx].set_color('red')
promedio_enlaces = df['n_links_found'].mean()
ax2.axhline(y=promedio_enlaces, color='r', linestyle='--', alpha=0.7, label=f'Promedio: {promedio_enlaces:.1f}')
ax2.legend()

# Gráfica 3: Velocidad de crawling
ax3.plot(df['#'], paginas_por_minuto_tiempo_real, 'purple', marker='s', markersize=4)
ax3.set_title('Velocidad de Crawling (Páginas por Minuto)', fontsize=14, fontweight='bold')
ax3.set_xlabel('Número de Página')
ax3.set_ylabel('Páginas por Minuto')
ax3.grid(True, alpha=0.3)
ax3.axhline(y=paginas_por_minuto, color='r', linestyle='--', alpha=0.7, label=f'Promedio: {paginas_por_minuto:.2f}')
ax3.legend()

# Gráfica 4: Distribución de tiempos
bins = np.arange(1.5, 5.5, 0.5)
n, bins, patches = ax4.hist(df['elapsed_s'], bins=bins, alpha=0.7, color='orange', edgecolor='black')
ax4.set_title('Distribución de Tiempos de Respuesta', fontsize=14, fontweight='bold')
ax4.set_xlabel('Tiempo (segundos)')
ax4.set_ylabel('Frecuencia')
ax4.grid(True, alpha=0.3, axis='y')
ax4.axvline(x=promedio_tiempo, color='r', linestyle='--', alpha=0.7, label=f'Promedio: {promedio_tiempo:.2f}s')
ax4.legend()
for i, (value, patch) in enumerate(zip(n, patches)):
    if value > 0:
        ax4.text(patch.get_x() + patch.get_width()/2, value + 0.1, str(int(value)), ha='center', va='bottom', fontweight='bold')

# Añadir texto con métricas
metricas_texto = f"""MÉTRICAS DEL CRAWLER UNAE
• Páginas: {len(df)}
• Tiempo total: {total_tiempo:.2f}s
• Velocidad: {paginas_por_minuto:.2f} pág/min
• Tiempo promedio: {promedio_tiempo:.2f}s
• Enlaces promedio: {promedio_enlaces:.1f}
• Más rápida: {df['elapsed_s'].min():.2f}s (Pág {df['elapsed_s'].idxmin()+1})
• Más lenta: {df['elapsed_s'].max():.2f}s (Pág {df['elapsed_s'].idxmax()+1})
• Más enlaces: {df['n_links_found'].max()} (Pág {df['n_links_found'].idxmax()+1})"""
plt.figtext(0.5, 0.01, metricas_texto, ha="center", fontsize=11, bbox={"facecolor":"lightgray", "alpha":0.7, "pad":5})

plt.tight_layout()
plt.subplots_adjust(bottom=0.15)

# Guardar y mostrar
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
nombre_archivo = f"metricas_crawler_unae_{timestamp}.png"
plt.savefig(nombre_archivo, dpi=300, bbox_inches='tight')
plt.show()

print(f"✅ Gráfica generada: {nombre_archivo}")
print(f"📊 Páginas: {len(df)} | Tiempo: {total_tiempo:.2f}s | Velocidad: {paginas_por_minuto:.2f} pág/min")