import fastf1
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Configuración
plt.style.use('dark_background')
cache_dir = './f1_cache'
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)
fastf1.Cache.enable_cache(cache_dir)

def generar_grafico_lluvia(año, gran_premio, piloto='NOR'):
    print(f"[API] Analizando evento atípico (Lluvia): {año} {gran_premio} para {piloto}...")
    
    # 1. Cargar la sesión de carrera
    session = fastf1.get_session(año, gran_premio, 'R')
    session.load()
    
    # 2. Extraer vueltas del piloto
    laps = session.laps.pick_drivers(piloto)
    
    # Filtro suave: Eliminamos vueltas de entrada/salida de pits, pero mantenemos todo lo demás
    # porque en lluvia incluso las vueltas bajo Safety Car cuentan la historia del caos.
    laps = laps[laps['PitOutTime'].isnull() & laps['PitInTime'].isnull()].copy()
    
    # Convertir tiempo a segundos para graficar
    laps['LapTime_Sec'] = laps['LapTime'].dt.total_seconds()
    
    # 3. Colores oficiales para condiciones climáticas mixtas
    colores_clima = {
        'SOFT': '#FF3333',         # Rojo (Seco)
        'MEDIUM': '#EAEA00',       # Amarillo (Seco)
        'HARD': '#FFFFFF',         # Blanco (Seco)
        'INTERMEDIATE': '#43B02A', # Verde (Lluvia Ligera)
        'WET': '#0066FF'           # Azul (Lluvia Extrema)
    }

    # 4. Configurar Visualización
    fig, ax = plt.subplots(figsize=(13, 7))
    fig.suptitle(f"Análisis de Evento Atípico (Wet Race) - Adaptabilidad Estratégica\n{piloto} en {gran_premio} {año}", fontsize=16, fontweight='bold', y=0.98)
    
    # 5. Trazar la evolución del ritmo
    # Usamos una línea continua gris de fondo para mostrar la tendencia
    ax.plot(laps['LapNumber'], laps['LapTime_Sec'], color='gray', alpha=0.4, linewidth=1.5, zorder=1)
    
    # Superponemos los puntos de color según el neumático que llevaba puesto
    sns.scatterplot(
        data=laps, 
        x='LapNumber', 
        y='LapTime_Sec', 
        hue='Compound', 
        palette=colores_clima, 
        s=80, 
        edgecolor='white',
        linewidth=0.5,
        zorder=2,
        ax=ax
    )

    # 6. Formato del gráfico
    # Invertimos el eje Y para que los tiempos MÁS RÁPIDOS (números menores) estén ARRIBA
    ax.invert_yaxis()
    
    ax.set_xlabel("Número de Vuelta", fontsize=12)
    ax.set_ylabel("Tiempo por Vuelta (Segundos) -> Hacia arriba es más rápido", fontsize=12)
    ax.grid(color='#333333', linestyle=':', linewidth=1)
    
    # Leyenda
    ax.legend(title="Compuesto Usado", bbox_to_anchor=(1.02, 1), loc='upper left', frameon=True, facecolor='#111111')
    
    # Exportación
    ruta = f"Outlier_Lluvia_{año}_{gran_premio}_{piloto}.png"
    plt.tight_layout()
    plt.savefig(ruta, dpi=300)
    print(f"[OK] Gráfico de Outlier exportado a: {ruta}\n")
    plt.close()

if __name__ == '__main__':
    generar_grafico_lluvia(2023, 'Netherlands', piloto='NOR')