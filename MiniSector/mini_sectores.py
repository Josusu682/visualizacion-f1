import fastf1
import fastf1.plotting
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import os

# 1. Configuración de Caché y Estilos
cache_dir = './f1_cache'
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)
fastf1.Cache.enable_cache(cache_dir)
fastf1.plotting.setup_mpl()

def analizar_mini_sectores(año, gran_premio, num_sectores=25):
    print(f"Procesando Mini-Sectores: {año} {gran_premio}...")
    
    # Cargar sesión de clasificación
    session = fastf1.get_session(año, gran_premio, 'Q')
    session.load()

    # Extraer vueltas más rápidas

    lap_nor = session.laps.pick_drivers('NOR').pick_fastest()
    lap_pia = session.laps.pick_drivers('PIA').pick_fastest()

    # Extraer telemetría con posición X, Y (para el mapa) y Distancia
    tel_nor = lap_nor.get_telemetry()
    tel_pia = lap_pia.get_telemetry()

    # 2. Ingeniería de Características: Creación de Mini-sectores
    # Calculamos la longitud total de la pista basándonos en la vuelta de Lando
    distancia_total = max(tel_nor['Distance'])
    tamaño_sector = distancia_total / num_sectores

    # Asignar un "ID de mini-sector" a cada punto de telemetría
    tel_nor['MiniSector'] = (tel_nor['Distance'] // tamaño_sector).astype(int) + 1
    tel_pia['MiniSector'] = (tel_pia['Distance'] // tamaño_sector).astype(int) + 1

    # 3. Cálculo Matemático: Velocidad media por mini-sector
    vel_media_nor = tel_nor.groupby('MiniSector')['Speed'].mean().reset_index()
    vel_media_pia = tel_pia.groupby('MiniSector')['Speed'].mean().reset_index()

    # Unir datos para comparar
    comparativa = pd.merge(vel_media_nor, vel_media_pia, on='MiniSector', suffixes=('_NOR', '_PIA'))
    
    # Determinar quién fue más rápido (1 para NOR, 2 para PIA)
    comparativa['Fastest_Driver_Int'] = np.where(
        comparativa['Speed_NOR'] > comparativa['Speed_PIA'], 1, 2
    )

    # 4. Preparar datos para el trazado del mapa
    # Mapeamos el ganador de cada sector de vuelta a la telemetría completa para graficar
    tel_nor = pd.merge(tel_nor, comparativa[['MiniSector', 'Fastest_Driver_Int']], on='MiniSector')

    # Convertir coordenadas X e Y a formato compatible con LineCollection
    x = np.array(tel_nor['X'].values)
    y = np.array(tel_nor['Y'].values)
    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    
    ganador_sector = tel_nor['Fastest_Driver_Int'].values[:-1]

    # 5. Visualización: Mapa de Dominio
    fig, ax = plt.subplots(figsize=(10, 8))
    fig.suptitle(f"Dominio por Mini-Sectores: NOR vs PIA\n{gran_premio} {año}", fontsize=14, fontweight='bold')

    # Definir mapa de colores personalizados: Papaya vs Gris oscuro/Negro
    # 1 (NOR) = Papaya, 2 (PIA) = Gris
    from matplotlib.colors import ListedColormap
    cmap = ListedColormap(['#FF8700', '#555555']) 

    lc = LineCollection(segments, cmap=cmap, norm=plt.Normalize(1, 2))
    lc.set_array(ganador_sector)
    lc.set_linewidth(5)
    
    ax.add_collection(lc)
    ax.axis('equal')
    ax.axis('off') # Ocultar ejes para que parezca un circuito real

    # Añadir leyenda manual
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], color='#FF8700', lw=4, label='Lando Norris'),
        Line2D([0], [0], color='#555555', lw=4, label='Oscar Piastri')
    ]
    ax.legend(handles=legend_elements, loc='upper right')

    # Exportar
    ruta_exportacion = f"Mapa_MiniSectores_{año}_{gran_premio}.png"
    plt.tight_layout()
    plt.savefig(ruta_exportacion, dpi=300, transparent=False)
    print(f"Mapa exportado: {ruta_exportacion}")
    plt.close() # Cerrar para no saturar memoria en bucles grandes

# Prueba unitaria con la mejor carrera de 2024
# ... (Aquí va todo el código anterior de configuración y la función analizar_mini_sectores) ...

import time

def ejecutar_lote_analisis():
    # 1. Definición de la muestra estratificada (La Matriz)
    carreras_objetivo = [
        # Temporada 2023
        (2023, 'Bahrain'),       # Alta Carga / Bajo Desempeño
        (2023, 'Qatar'),         # Alta Carga / Alto Desempeño
        (2023, 'Las Vegas'),     # Baja Carga / Bajo Desempeño
        (2023, 'Belgium'),       # Baja Carga / Alto Desempeño
        
        # Temporada 2024
        (2024, 'Italy'),         # Baja Carga / Alto Desempeño
        (2024, 'Austria'),       # Alta Carga / Bajo Desempeño
        (2024, 'Hungary'),       # Alta Carga / Alto Desempeño
        (2024, 'Saudi Arabia'),  # Baja Carga / Bajo Desempeño
        
        # Temporada 2025
        (2025, 'China'),         # Alta Carga / Alto Desempeño
        (2025, 'Monaco'),        # Alta Carga / Bajo Desempeño
        (2025, 'Las Vegas'),     # Baja Carga / Bajo Desempeño
        (2025, 'Azerbaijan')     # Baja Carga / Alto Desempeño
    ]

    print("==================================================")
    print(f"Iniciando procesamiento por lotes (Batch Processing)")
    print(f"Total de eventos a procesar: {len(carreras_objetivo)}")
    print("==================================================\n")

    conteo_exitos = 0
    conteo_errores = 0

    # 2. El Bucle Maestro con manejo de excepciones
    for año, gran_premio in carreras_objetivo:
        try:
            print(f"-> Extrayendo datos: {gran_premio} {año}...")
            
            # Aquí llamas a la función generadora de mapas
           # ... código anterior ...
            analizar_mini_sectores(año, gran_premio, num_sectores=25)
            
            print(f"[OK] Éxito: Gráficos de {gran_premio} exportados.\n")
            conteo_exitos += 1
            
            time.sleep(2) 

        except Exception as e:
            print(f"[ERROR] Error crítico procesando {gran_premio} {año}.")
            print(f"Detalle del error: {e}\n")
            conteo_errores += 1
            continue

    # 3. Resumen de ejecución
    print("==================================================")
    print("PROCESAMIENTO FINALIZADO")
    print(f"Archivos generados exitosamente: {conteo_exitos}")
    print(f"Errores encontrados: {conteo_errores}")
    print("==================================================")

if __name__ == '__main__':
    ejecutar_lote_analisis()