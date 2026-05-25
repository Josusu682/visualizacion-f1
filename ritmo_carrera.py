import fastf1
import fastf1.plotting
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import time

# 1. Configuración de Caché y Estilos Oscuros
cache_dir = './f1_cache'
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)
fastf1.Cache.enable_cache(cache_dir)
fastf1.plotting.setup_mpl() # Corregido: se eliminó misc_mpl_mods=False

def analizar_ritmo_carrera(año, gran_premio):
    print(f"-> Analizando telemetría de carrera: {año} {gran_premio}...")
    
    # Cargar sesión de Carrera ('R')
    session = fastf1.get_session(año, gran_premio, 'R')
    session.load()

    # 2. Extraer todas las vueltas (Corregido: pick_drivers en plural)
    laps_nor = session.laps.pick_drivers('NOR')
    laps_pia = session.laps.pick_drivers('PIA')

    # 3. FILTRO CRÍTICO DE INGENIERÍA:
    # Añadimos .copy() para evitar advertencias de memoria en Pandas
    valid_nor = laps_nor.pick_track_status('1').pick_quicklaps().copy()
    valid_pia = laps_pia.pick_track_status('1').pick_quicklaps().copy()

    # Identificar a los pilotos
    valid_nor['Driver'] = 'NOR'
    valid_pia['Driver'] = 'PIA'
    
    # Unir datos
    df_laps = pd.concat([valid_nor, valid_pia])
    
    # Convertir el tiempo de vuelta (Timedelta) a segundos flotantes para graficar
    df_laps['LapTime_Sec'] = df_laps['LapTime'].dt.total_seconds()

    # 4. Configurar Visualización
    fig, ax = plt.subplots(figsize=(12, 7))
    fig.suptitle(f"Evolución del Ritmo de Carrera y Degradación\n{gran_premio} {año}", fontsize=16, fontweight='bold')

    # Colores base de pilotos
    colores_piloto = {'NOR': '#FF8700', 'PIA': '#AAAAAA'}
    
    # Colores oficiales de Pirelli para los compuestos
    colores_pirelli = {'SOFT': '#FF3333', 'MEDIUM': '#EAEA00', 'HARD': '#FFFFFF'}

    # 5. Trazar Puntos y Líneas de Tendencia
    for driver in ['NOR', 'PIA']:
        driver_data = df_laps[df_laps['Driver'] == driver]
        
        # Graficar los tiempos de vuelta reales marcando el compuesto usado
        sns.scatterplot(
            data=driver_data, 
            x='LapNumber', 
            y='LapTime_Sec', 
            hue='Compound', 
            palette=colores_pirelli,
            edgecolor=colores_piloto[driver],
            linewidth=1.5,
            s=60,
            ax=ax,
            alpha=0.8,
            legend=False
        )

        # Graficar la línea de regresión (Degradación media)
        sns.regplot(
            data=driver_data, 
            x='LapNumber', 
            y='LapTime_Sec', 
            scatter=False, 
            color=colores_piloto[driver], 
            label=f"{driver} (Tendencia)",
            line_kws={"linewidth": 2.5, "linestyle": "-" if driver == 'NOR' else "--"}
        )

    # Configuración de ejes
    ax.set_xlabel("Número de Vuelta", fontsize=12)
    ax.set_ylabel("Tiempo por Vuelta (Segundos)", fontsize=12)
    ax.grid(color='grey', linestyle='-', linewidth=0.2, alpha=0.5)
    
    # Leyenda limpia
    ax.legend(loc='upper right', frameon=True, facecolor="#E9DBB4")
    
    # Exportar
    ruta_exportacion = f"RacePace_{año}_{gran_premio}.png"
    plt.tight_layout()
    plt.savefig(ruta_exportacion, dpi=300)
    plt.close()

def ejecutar_lote_carreras():
    # 1. Definición de la muestra estratificada
    carreras_objetivo = [
        # Temporada 2023
        (2023, 'Bahrain'),       
        (2023, 'Qatar'),         
        (2023, 'Las Vegas'),     
        (2023, 'Belgium'),       
        
        # Temporada 2024
        (2024, 'Italy'),         
        (2024, 'Austria'),       
        (2024, 'Hungary'),       
        (2024, 'Saudi Arabia'),  
        
        # Temporada 2025
        (2025, 'China'),         
        (2025, 'Monaco'),        
        (2025, 'Las Vegas'),     
        (2025, 'Azerbaijan')     
    ]

    print("==================================================")
    print("Iniciando procesamiento por lotes - RITMO DE CARRERA")
    print(f"Total de eventos a procesar: {len(carreras_objetivo)}")
    print("==================================================\n")

    conteo_exitos = 0
    conteo_errores = 0

    # 2. El Bucle Maestro con manejo de excepciones
    for año, gran_premio in carreras_objetivo:
        try:
            analizar_ritmo_carrera(año, gran_premio)
            print(f"[OK] Éxito: Gráfico de RacePace para {gran_premio} {año} exportado.\n")
            conteo_exitos += 1
            
            # Pausa de 2 segundos para dar respiro a la conexión
            time.sleep(2) 
            
        except Exception as e:
            print(f"[ERROR] Fallo crítico procesando {gran_premio} {año}.")
            print(f"Detalle del error: {e}\n")
            conteo_errores += 1
            continue 

    # 3. Resumen de ejecución
    print("==================================================")
    print("PROCESAMIENTO DE CARRERAS FINALIZADO")
    print(f"Archivos PNG generados: {conteo_exitos}")
    print(f"Errores encontrados: {conteo_errores}")
    print("==================================================")

if __name__ == '__main__':
    ejecutar_lote_carreras()