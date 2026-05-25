import fastf1
import fastf1.plotting
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Configuración
plt.style.use('dark_background')
fastf1.plotting.setup_mpl()
cache_dir = './f1_cache'
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)
fastf1.Cache.enable_cache(cache_dir)

def generar_matriz_eficiencia(año, gran_premio):
    print(f"[API] Calculando Matriz de Eficiencia con telemetría real: {año} {gran_premio} (Q)...")
    
    # 1. Cargar la sesión de clasificación
    session = fastf1.get_session(año, gran_premio, 'Q')
    session.load()
    
    # 2. Seleccionar pilotos representativos
    pilotos = ['NOR', 'VER', 'LEC', 'HAM', 'ALO']
    equipos = {'NOR': 'McLaren', 'VER': 'Red Bull', 'LEC': 'Ferrari', 'HAM': 'Mercedes', 'ALO': 'Aston Martin'}
    colores = {'McLaren': '#FF8700', 'Red Bull': '#0600EF', 'Ferrari': '#DC0000', 'Mercedes': '#00D2BE', 'Aston Martin': '#006F62'}
    
    datos = []
    
    # 3. Extracción matemática de valores físicos reales
    for p in pilotos:
        try:
            lap = session.laps.pick_drivers(p).pick_fastest()
            tel = lap.get_telemetry()
            
            # Velocidad Punta: El pico máximo de velocidad en toda la vuelta
            v_max = tel['Speed'].max()
            
            # Velocidad de Vértice: El punto más lento de la vuelta. 
            # Filtramos velocidades menores a 50 km/h para evitar errores de sensor o salidas de pista
            v_min = tel[tel['Speed'] > 50]['Speed'].min()
            
            datos.append({
                'Piloto': p,
                'Equipo': equipos[p],
                'V_Max': v_max,
                'V_Min': v_min
            })
        except Exception as e:
            print(f"[ERROR] No se pudo procesar telemetría de {p}: {e}")
            
    df = pd.DataFrame(datos)
    
    # 4. Configurar Visualización
    fig, ax = plt.subplots(figsize=(11, 7))
    fig.suptitle(f"Matriz de Eficiencia Técnica: Tracción vs Velocidad Punta\n{gran_premio} {año}", fontsize=16, fontweight='bold')
    ax.set_title("Datos reales de telemetría (km/h) en vuelta rápida", fontsize=11, color='lightgray')
    
    # Trazar puntos
    sns.scatterplot(data=df, x='V_Min', y='V_Max', hue='Equipo', palette=colores, s=300, ax=ax, edgecolor='white', linewidth=1.5)
    
    # Añadir etiquetas de texto a cada punto (ligeramente desplazadas para no tapar el círculo)
    for i, row in df.iterrows():
        ax.text(row['V_Min'] + 0.3, row['V_Max'] - 0.5, row['Piloto'], fontsize=12, color='white', fontweight='bold')
        
    # Formato de Ejes
    ax.set_xlabel("Velocidad Mínima en Vértice de Curva (Tracción / Grip Mecánico) [km/h]", fontsize=12)
    ax.set_ylabel("Velocidad Máxima en Recta (Eficiencia Aerodinámica / Motor) [km/h]", fontsize=12)
    ax.grid(color='#333333', linestyle='--', linewidth=0.5)
    
    # 5. CREACIÓN DE LOS CUADRANTES ESTRATÉGICOS (La clave del análisis)
    # Dibujamos líneas en el promedio exacto de la parrilla
    promedio_vmin = df['V_Min'].mean()
    promedio_vmax = df['V_Max'].mean()
    
    ax.axvline(promedio_vmin, color='grey', linestyle=':', alpha=0.8, linewidth=2)
    ax.axhline(promedio_vmax, color='grey', linestyle=':', alpha=0.8, linewidth=2)
    
    # Textos de los cuadrantes
    ax.text(df['V_Min'].min(), df['V_Max'].max(), "ALTA VELOCIDAD / BAJA TRACCIÓN", color='gray', alpha=0.5, fontsize=10)
    ax.text(df['V_Min'].max() - 2, df['V_Max'].min(), "ALTA TRACCIÓN / ALTO DRAG", color='gray', alpha=0.5, fontsize=10)
    
    # Leyenda
    ax.legend(title="Escudería", bbox_to_anchor=(1.02, 1), loc='upper left', frameon=False)
    
    # Exportación
    ruta = f"Matriz_Eficiencia_REAL_{año}_{gran_premio}.png"
    plt.tight_layout()
    plt.savefig(ruta, dpi=300, bbox_inches='tight')
    print(f"[OK] Gráfico exportado a: {ruta}\n")
    plt.close()

if __name__ == '__main__':
    generar_matriz_eficiencia(2024, 'Japan')