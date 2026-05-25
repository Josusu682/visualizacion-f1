import fastf1
import fastf1.plotting
import matplotlib.pyplot as plt
import pandas as pd
import os

# 1. Configuración de Caché y Estilos
cache_dir = './f1_cache'
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)
fastf1.Cache.enable_cache(cache_dir)
fastf1.plotting.setup_mpl()

def analizar_micro_curva(año, gran_premio, distancia_min, distancia_max, nombre_curva="Curva 1"):
    print(f"-> Analizando Estilo de Conducción: {año} {gran_premio} [{nombre_curva}]...")
    
    # 2. Cargar sesión de Clasificación ('Q' es ideal porque no hay tráfico)
    session = fastf1.get_session(año, gran_premio, 'Q')
    session.load()

    # Extraer las vueltas más rápidas
    lap_nor = session.laps.pick_drivers('NOR').pick_fastest()
    lap_pia = session.laps.pick_drivers('PIA').pick_fastest()

    # Extraer telemetría y añadir distancia
    tel_nor = lap_nor.get_telemetry().add_distance()
    tel_pia = lap_pia.get_telemetry().add_distance()

    # 3. FILTRO MICRO-SECTOR (El Zoom)
    # Aislamos solo los metros correspondientes a la curva solicitada
    tel_nor_curva = tel_nor[(tel_nor['Distance'] >= distancia_min) & (tel_nor['Distance'] <= distancia_max)]
    tel_pia_curva = tel_pia[(tel_pia['Distance'] >= distancia_min) & (tel_pia['Distance'] <= distancia_max)]

    # 4. Configurar Visualización (3 Subgráficos sincronizados)
    fig, ax = plt.subplots(3, 1, figsize=(12, 10), gridspec_kw={'height_ratios': [2, 1, 1]}, sharex=True)
    fig.suptitle(f"Perfil de Conducción: Norris vs Piastri\n{gran_premio} {año} - {nombre_curva}", fontsize=16, fontweight='bold')

    colores = {'NOR': '#FF8700', 'PIA': '#AAAAAA'}

    # Gráfico A: Velocidad (Perfil de la curva)
    ax[0].plot(tel_nor_curva['Distance'], tel_nor_curva['Speed'], label='Norris', color=colores['NOR'], linewidth=2)
    ax[0].plot(tel_pia_curva['Distance'], tel_pia_curva['Speed'], label='Piastri', color=colores['PIA'], linewidth=2, linestyle='--')
    ax[0].set_ylabel("Velocidad (km/h)", fontsize=11)
    ax[0].legend(loc='upper right')
    ax[0].grid(color='grey', linestyle='-', linewidth=0.2, alpha=0.5)

    # Gráfico B: Freno (Braking Trace)
    # Convertimos a numérico por si la API entrega booleanos (True/False)
    ax[1].plot(tel_nor_curva['Distance'], tel_nor_curva['Brake'].astype(float), color=colores['NOR'], linewidth=2)
    ax[1].plot(tel_pia_curva['Distance'], tel_pia_curva['Brake'].astype(float), color=colores['PIA'], linewidth=2, linestyle='--')
    ax[1].set_ylabel("Freno", fontsize=11)
    ax[1].set_yticks([]) # Ocultamos números Y porque solo nos importa cuándo sube/baja la línea
    ax[1].grid(color='grey', linestyle='-', linewidth=0.2, alpha=0.5)

    # Gráfico C: Acelerador (Throttle Trace)
    ax[2].plot(tel_nor_curva['Distance'], tel_nor_curva['Throttle'], color=colores['NOR'], linewidth=2)
    ax[2].plot(tel_pia_curva['Distance'], tel_pia_curva['Throttle'], color=colores['PIA'], linewidth=2, linestyle='--')
    ax[2].set_ylabel("Acelerador (%)", fontsize=11)
    ax[2].set_xlabel("Distancia en Pista (metros)", fontsize=12)
    ax[2].grid(color='grey', linestyle='-', linewidth=0.2, alpha=0.5)

    # Ajustes finales
    plt.tight_layout()
    ruta_exportacion = f"Conduccion_{año}_{gran_premio}_{nombre_curva.replace(' ', '')}.png"
    plt.savefig(ruta_exportacion, dpi=300)
    print(f"[OK] Gráfico exportado: {ruta_exportacion}\n")
    plt.close()

# Prueba Unitaria: Bélgica 2023 (Curva Pouhon - Alta Velocidad)
# Spa es larguísimo (7km). Pouhon se encuentra aprox entre los metros 4500 y 5200.
if __name__ == '__main__':
    try:
        analizar_micro_curva(
            año=2023, 
            gran_premio='Belgium', 
            distancia_min=4400, 
            distancia_max=5300, 
            nombre_curva="Pouhon (Alta Velocidad)"
        )
    except Exception as e:
        print(f"Error en la ejecución: {e}")