import fastf1
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Configuración de estilo y caché
plt.style.use('seaborn-v0_8-whitegrid')
cache_dir = './f1_cache'
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)
fastf1.Cache.enable_cache(cache_dir)

def generar_boxplot_delta(año, gran_premio, piloto_referencia='VER'):
    print(f"[API] Extrayendo telemetría de carrera: {año} {gran_premio}...")
    
    # 1. Cargar la sesión
    session = fastf1.get_session(año, gran_premio, 'R')
    session.load()

    # 2. Seleccionar a los representantes de las escuderías top
    # Norris (McLaren), Verstappen (Red Bull), Leclerc (Ferrari), Hamilton (Mercedes)
    pilotos = ['NOR', 'VER', 'LEC', 'HAM']
    nombres_equipos = {'NOR': 'McLaren', 'VER': 'Red Bull', 'LEC': 'Ferrari', 'HAM': 'Mercedes'}
    colores_equipos = {'McLaren': '#D8902D', 'Red Bull': '#4A6FA5', 'Ferrari': '#C94C4C', 'Mercedes': '#5FA9A9'}

    df_list = []
    
    # 3. Extraer y limpiar las vueltas de cada piloto
    for p in pilotos:
        laps = session.laps.pick_drivers(p)
        # Filtro estricto: Solo bandera verde y eliminando vueltas de entrada/salida de boxes
        valid_laps = laps.pick_track_status('1').pick_quicklaps().copy()
        
        if not valid_laps.empty:
            valid_laps['Driver'] = p
            valid_laps['Team'] = nombres_equipos[p]
            # Convertir el formato de tiempo a segundos flotantes (ej. 1:20.500 -> 80.5)
            valid_laps['LapTime_Sec'] = valid_laps['LapTime'].dt.total_seconds()
            df_list.append(valid_laps[['Driver', 'Team', 'LapTime_Sec']])

    # Unir todos los datos en un solo DataFrame
    df_total = pd.concat(df_list, ignore_index=True)

    # 4. CÁLCULO DEL DELTA (El corazón del gráfico)
    # Calculamos la mediana de tiempo de vuelta del piloto de referencia
    mediana_referencia = df_total[df_total['Driver'] == piloto_referencia]['LapTime_Sec'].median()
    
    # Restamos la referencia a todas las vueltas. 
    # Resultado: Si da +0.5, esa vuelta fue medio segundo más lenta que el ritmo base.
    df_total['Delta'] = df_total['LapTime_Sec'] - mediana_referencia

    # Limpiar anomalías estadísticas (errores puntuales, pasadas de frenada) para no deformar la gráfica
    # Nos quedamos solo con el ritmo competitivo (vueltas a menos de 3 segundos de diferencia)
    df_limpio = df_total[(df_total['Delta'] >= -2.0) & (df_total['Delta'] <= 3.0)]

    # 5. Visualización
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor('white')      # Fondo blanco limpio
    ax.set_facecolor('#f8f9fa')           # Gris muy claro para los datos
    fig.suptitle(f"Brecha de Rendimiento Puro (Race Pace Delta)\n{gran_premio} {año}", fontsize=16, fontweight='bold')
    ax.set_title(f"Línea base (0.0s) = Ritmo mediano de {piloto_referencia} ({nombres_equipos[piloto_referencia]})", fontsize=11, color='lightgray')

    # Trazar el Boxplot
    sns.boxplot(
        data=df_limpio,
        x='Team',
        y='Delta',
        palette=colores_equipos,
        ax=ax,
        showfliers=False, # Ocultar puntos atípicos, nos importa "la caja" central
        width=0.4,
        linewidth=2
    )

    # Añadir línea punteada horizontal en el 0.0 (El estándar de oro)
    ax.axhline(0, color='white', linestyle='--', linewidth=1.5, alpha=0.8)

    # Formato de ejes
    ax.set_ylabel("Delta de Tiempo (Segundos más lento)", fontsize=12)
    ax.set_xlabel("Escudería", fontsize=12)
    ax.grid(axis='y', color='#333333', linestyle=':', linewidth=1)

    # Exportación
    ruta_exportacion = f"Boxplot_Delta_{año}_{gran_premio}.png"
    plt.tight_layout()
    plt.savefig(ruta_exportacion, dpi=300)
    print(f"[OK] Gráfico exportado a: {ruta_exportacion}\n")
    plt.close()

if __name__ == '__main__':
    # Ejecutamos el análisis de la carrera de España 2024
    generar_boxplot_delta(2024, 'Spain', piloto_referencia='VER')