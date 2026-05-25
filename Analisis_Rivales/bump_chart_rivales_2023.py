import requests
import pandas as pd
import matplotlib.pyplot as plt
import time

plt.style.use('dark_background')

def extraer_datos_reales_api(año, total_rondas):
    print(f"Conectando a la API de F1 para descargar posiciones de {año}...")
    datos_clasificacion = []

    # Iterar por cada carrera de la temporada
    for ronda in range(1, total_rondas + 1):
        # Endpoint de la API que nos da cómo quedó el campeonato después de esa ronda exacta
        url = f"https://api.jolpi.ca/ergast/f1/{año}/{ronda}/constructorStandings.json"
        
        try:
            respuesta = requests.get(url)
            datos_json = respuesta.json()
            
            # Navegar por el JSON hasta la lista de constructores
            standings = datos_json['MRData']['StandingsTable']['StandingsLists'][0]['ConstructorStandings']
            
            # Crear una fila para nuestro DataFrame
            fila = {'Ronda': f"R{ronda}"}
            
            for equipo in standings:
                nombre = equipo['Constructor']['name']
                posicion = int(equipo['position'])
                fila[nombre] = posicion
                
            datos_clasificacion.append(fila)
            
            # Pequeña pausa para no saturar el servidor público
            time.sleep(0.5)
            
        except Exception as e:
            print(f"[ERROR] No se pudo obtener la ronda {ronda}: {e}")
            
    print("[OK] Datos reales descargados y estructurados con éxito.\n")
    return pd.DataFrame(datos_clasificacion)


def generar_bump_chart_real(año_objetivo, total_rondas):
    print(f"-> Generando Bump Chart de Constructores para la temporada {año_objetivo}...")

    # 1. OBTENER DATOS REALES DE LA API
    df = extraer_datos_reales_api(año_objetivo, total_rondas)

    # 2. Diccionario de colores oficiales (Asegúrate de que los nombres coincidan con la API)
    # La API devuelve nombres limpios como "McLaren", "Red Bull", "Mercedes", "Ferrari", "Aston Martin"
    colores_equipos = {
        'McLaren': '#FF8700',       
        'Red Bull': '#0600EF',      
        'Mercedes': '#00D2BE',      
        'Ferrari': '#DC0000',       
        'Aston Martin': '#006F62',  
        'Alpine F1 Team': '#0090FF' # A veces la API lo llama Alpine F1 Team
    }

    # 3. Configuración de la Figura
    fig, ax = plt.subplots(figsize=(14, 7))
    fig.suptitle(f"Evolución Jerárquica de Rivales Directos - {año_objetivo} (Datos Oficiales)", fontsize=18, fontweight='bold')

    # 4. Trazar las líneas
    equipos = [col for col in df.columns if col != 'Ronda']
    
    for equipo in equipos:
        grosor = 4 if equipo == 'McLaren' else 2
        opacidad = 1.0 if equipo == 'McLaren' else 0.4 # Opacamos a los rivales para destacar a McLaren
        
        ax.plot(
            df['Ronda'], 
            df[equipo], 
            marker='o', 
            markersize=8 if equipo == 'McLaren' else 5,
            linewidth=grosor, 
            color=colores_equipos.get(equipo, '#888888'), # Gris si el equipo no está en el diccionario
            label=equipo,
            alpha=opacidad
        )

    # 5. Invertir Eje Y (El 1er lugar arriba)
    ax.invert_yaxis()
    ax.set_yticks(range(1, 11))
    ax.set_yticklabels([f"P{i}" for i in range(1, 11)], fontsize=11)

    # 6. Formato
    ax.set_xlabel("Ronda del Campeonato", fontsize=12)
    ax.set_ylabel("Posición en Constructores", fontsize=12)
    ax.grid(axis='y', color='#333333', linestyle='--', linewidth=0.5)
    
    # Leyenda
    ax.legend(title="Escudería", bbox_to_anchor=(1.02, 1), loc='upper left', frameon=False)

    # 7. Exportación
    ruta_exportacion = f"BumpChart_Rivales_REAL_{año_objetivo}.png"
    plt.tight_layout()
    plt.savefig(ruta_exportacion, dpi=300, bbox_inches='tight')
    print(f"[OK] Gráfico exportado a: {ruta_exportacion}")
    plt.close()

# Ejecución (Ejemplo con 2023, que tuvo 22 rondas)
if __name__ == '__main__':
    # Modifica el año y el número total de Grandes Premios de esa temporada
    generar_bump_chart_real(año_objetivo=2023, total_rondas=22)