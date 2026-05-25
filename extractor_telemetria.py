import fastf1
import fastf1.plotting
import matplotlib.pyplot as plt
import pandas as pd
import os

# 1. Configuración inicial y Caché (CRÍTICO)
# El caché evita que descargues los mismos 50-100MB cada vez que corres el script.
cache_dir = './f1_cache'
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)
fastf1.Cache.enable_cache(cache_dir)

# Activar la paleta de colores oficial de FastF1 (incluye los colores de McLaren)
fastf1.plotting.setup_mpl(misc_mpl_mods=False)

def extraer_telemetria_qualy(año, gran_premio):
    print(f"Cargando sesión: {año} {gran_premio} - Clasificación...")
    
    # 2. Cargar la sesión de Clasificación ('Q')
    session = fastf1.get_session(año, gran_premio, 'Q')
    session.load() # Aquí ocurre la descarga fuerte de la API

    # 3. Aislar las vueltas más rápidas de Norris (NOR) y Piastri (PIA)
    laps_nor = session.laps.pick_driver('NOR').pick_fastest()
    laps_pia = session.laps.pick_driver('PIA').pick_fastest()

    # Extraer el tiempo final para contexto
    delta_tiempo = laps_nor['LapTime'] - laps_pia['LapTime']
    print(f"Vuelta NOR: {laps_nor['LapTime']} | Vuelta PIA: {laps_pia['LapTime']}")
    print(f"Delta: {delta_tiempo.total_seconds():.3f} segundos")

    # 4. Extraer telemetría y añadir la columna de Distancia
    tel_nor = laps_nor.get_telemetry().add_distance()
    tel_pia = laps_pia.get_telemetry().add_distance()

    # 5. Visualización (Generación del H2H)
    crear_grafico_telemetria(tel_nor, tel_pia, año, gran_premio)
    
    return tel_nor, tel_pia

def crear_grafico_telemetria(tel_nor, tel_pia, año, gran_premio):
    # Crear una figura con 3 subgráficos (Velocidad, Acelerador, Freno)
    fig, ax = plt.subplots(3, 1, figsize=(15, 10), gridspec_kw={'height_ratios': [3, 1, 1]})
    fig.suptitle(f"Telemetría H2H: Norris vs Piastri - {gran_premio} {año} (Q)", fontsize=16)

    # Colores base (podemos ajustarlos para que contrasten, aunque ambos sean McLaren)
    color_nor = '#FF8700' # Papaya clásico
    color_pia = '#000000' # Negro carbono para contrastar

    # Subplot 1: Velocidad (Speed)
    ax[0].plot(tel_nor['Distance'], tel_nor['Speed'], label='NOR', color=color_nor, linewidth=2)
    ax[0].plot(tel_pia['Distance'], tel_pia['Speed'], label='PIA', color=color_pia, linewidth=1.5, linestyle='--')
    ax[0].set_ylabel('Velocidad (km/h)')
    ax[0].legend()

    # Subplot 2: Acelerador (Throttle)
    ax[1].plot(tel_nor['Distance'], tel_nor['Throttle'], color=color_nor)
    ax[1].plot(tel_pia['Distance'], tel_pia['Throttle'], color=color_pia, linestyle='--')
    ax[1].set_ylabel('Acelerador (%)')

    # Subplot 3: Freno (Brake)
    # Brake en FastF1 es un booleano (True/False) o un porcentaje dependiendo del año/sensor
    ax[2].plot(tel_nor['Distance'], tel_nor['Brake'], color=color_nor)
    ax[2].plot(tel_pia['Distance'], tel_pia['Brake'], color=color_pia, linestyle='--')
    ax[2].set_ylabel('Freno')
    ax[2].set_xlabel('Distancia (metros)')

    # Ajustes finales y exportación
    plt.tight_layout()
    ruta_exportacion = f"H2H_Qualy_{año}_{gran_premio}.png"
    plt.savefig(ruta_exportacion, dpi=300)
    print(f"Gráfico exportado exitosamente a: {ruta_exportacion}")
    plt.show()

# Ejecución de prueba
if __name__ == '__main__':
    tel_n, tel_p = extraer_telemetria_qualy(2024, 'Monza')