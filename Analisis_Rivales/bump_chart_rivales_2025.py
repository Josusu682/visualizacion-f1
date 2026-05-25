import requests
import pandas as pd
import matplotlib.pyplot as plt
import time

plt.style.use('dark_background')

def extraer_datos_reales_api(año, total_rondas):
    print(f"[API] Descargando posiciones oficiales de {año}...")
    datos_clasificacion = []

    for ronda in range(1, total_rondas + 1):
        url = f"https://api.jolpi.ca/ergast/f1/{año}/{ronda}/constructorStandings.json"
        try:
            respuesta = requests.get(url)
            datos_json = respuesta.json()
            
            # Navegar por el JSON hasta la lista de constructores
            standings = datos_json['MRData']['StandingsTable']['StandingsLists'][0]['ConstructorStandings']
            
            fila = {'Ronda': f"R{ronda}"}
            for equipo in standings:
                nombre = equipo['Constructor']['name']
                posicion = int(equipo['position'])
                fila[nombre] = posicion
                
            datos_clasificacion.append(fila)
            
            # Pausa para no saturar el servidor público
            time.sleep(0.5)
            
        except Exception as e:
            # Si una ronda aún no existiera o hubiera un error, lo saltamos limpiamente
            print(f"[ERROR] Ronda {ronda}: No se pudo obtener la información. Detalle: {e}")
            
    return pd.DataFrame(datos_clasificacion)

def generar_bump_chart_2025_real():
    año = 2025
    rondas = 24 # La temporada 2025 tuvo 24 carreras oficiales
    
    df = extraer_datos_reales_api(año, rondas)

    if df.empty:
        print("[ERROR] El DataFrame está vacío. Revisa tu conexión a internet.")
        return

    # Rivales directos en la era actual de F1
    colores_equipos = {
        'McLaren': '#FF8700',       
        'Red Bull': '#0600EF',      
        'Mercedes': '#00D2BE',      
        'Ferrari': '#DC0000',       
        'Aston Martin': '#006F62'
    }

    fig, ax = plt.subplots(figsize=(14, 7))
    fig.suptitle(f"Evolución Jerárquica - {año} (Datos Oficiales Reales)", fontsize=18, fontweight='bold')

    equipos = [col for col in df.columns if col != 'Ronda']
    
    for equipo in equipos:
        grosor = 4 if equipo == 'McLaren' else 2
        
        # Opacar a los equipos de la zona baja para destacar la lucha por el campeonato
        if equipo == 'McLaren':
            opacidad = 1.0
        elif equipo in ['Red Bull', 'Ferrari', 'Mercedes']:
            opacidad = 0.8
        else:
            opacidad = 0.25 

        ax.plot(
            df['Ronda'], 
            df[equipo], 
            marker='o', 
            markersize=8 if equipo == 'McLaren' else 5,
            linewidth=grosor, 
            color=colores_equipos.get(equipo, '#555555'), 
            label=equipo if opacidad > 0.3 else "", # Solo mostrar rivales directos en leyenda
            alpha=opacidad
        )

    # Invertir Eje Y para que el P1 quede en la cima
    ax.invert_yaxis()
    ax.set_yticks(range(1, 11))
    ax.set_yticklabels([f"P{i}" for i in range(1, 11)], fontsize=11)
    
    ax.set_xlabel("Ronda del Campeonato", fontsize=12)
    ax.set_ylabel("Posición en Constructores", fontsize=12)
    ax.grid(axis='y', color='#333333', linestyle='--', linewidth=0.5)
    
    # Leyenda limpia sin duplicados
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), title="Rivales Directos", bbox_to_anchor=(1.02, 1), loc='upper left', frameon=False)

    ruta = f"BumpChart_Rivales_REAL_{año}.png"
    plt.tight_layout()
    plt.savefig(ruta, dpi=300, bbox_inches='tight')
    print(f"[OK] Gráfico exportado a: {ruta}")

if __name__ == '__main__':
    generar_bump_chart_2025_real()