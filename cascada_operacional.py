import matplotlib.pyplot as plt
import numpy as np
import os

# Configuración de estilo
plt.style.use('dark_background')

def generar_cascada_operacional():
    print("[INFO] Generando Gráfico de Cascada Operacional...")

    # 1. Definir Categorías y Puntos (Basado en la temporada 2025)
    # Valores representativos para el análisis estratégico
    categorias = [
        'Puntos Máximos\nProyectados', 
        'Errores\nEstratégicos', 
        'Inspección Técnica\n(DSQ Las Vegas)', 
        'DNFs\nMecánicos', 
        'Errores\nde Piloto', 
        'Puntos Reales\nObtenidos'
    ]
    
# 921 fue el techo proyectado ideal. Restamos las pérdidas para llegar a los 833 reales y oficiales.
    valores = [921, -20, -43, -25, 0, 833]

    # 2. Cálculos matemáticos para las posiciones de las barras
    bases = [0] # La primera barra empieza desde el suelo (0)
    acumulado = valores[0]
    
    for i in range(1, len(valores) - 1):
        acumulado += valores[i] # Al ser negativo, se resta
        bases.append(acumulado)
        
    bases.append(0) # La última barra (Total) también empieza desde el suelo

    # 3. Asignación de colores
    # Papaya para el total inicial y final. Rojo para las pérdidas de puntos.
    colores = ['#FF8700', '#DC0000', '#DC0000', '#DC0000', '#DC0000', '#FF8700']

    # 4. Configurar la Figura
    fig, ax = plt.subplots(figsize=(12, 7))
    fig.suptitle("Auditoría de Eficiencia Operacional - McLaren 2025", fontsize=16, fontweight='bold')
    ax.set_title("Fuga de Puntos en el Campeonato de Constructores", fontsize=12, color='lightgray')

    # 5. Trazar el Gráfico de Cascada
    for i in range(len(categorias)):
        # La altura de las barras rojas debe ser positiva para que matplotlib las dibuje bien sobre su base
        altura = abs(valores[i]) if i != 0 and i != (len(categorias)-1) else valores[i]
        fondo = bases[i]
        
        ax.bar(categorias[i], altura, bottom=fondo, color=colores[i], edgecolor='white', width=0.6)
        
        # Añadir las etiquetas de texto (Los números)
        texto_valor = f"{valores[i]}" if valores[i] < 0 else f"{valores[i]}"
        
        # Posicionar el texto: en el medio para las pérdidas, arriba para los totales
        if i == 0 or i == len(categorias)-1:
            y_pos = altura + 15
            color_texto = 'white'
        else:
            y_pos = fondo + (altura / 2)
            color_texto = 'white'
            
        ax.text(i, y_pos, texto_valor, ha='center', va='center', color=color_texto, fontweight='bold', fontsize=12)

    # 6. Añadir las líneas conectores (Paso a Paso)
    y_lines = [valores[0]]
    acum = valores[0]
    for val in valores[1:-1]:
        acum += val
        y_lines.append(acum)

    for i in range(len(y_lines)):
        if i < len(categorias) - 1:
            # Dibuja una línea punteada desde la barra actual hasta la siguiente
            ax.plot([i - 0.35, i + 1.35], [y_lines[i], y_lines[i]], color='gray', linestyle='--', linewidth=1.5, alpha=0.7)

    # 7. Formato y diseño de ejes
    ax.set_ylabel("Puntos del Campeonato", fontsize=12)
    ax.grid(axis='y', color='#333333', linestyle=':', linewidth=0.8)
    
    # Ocultar los bordes superior y derecho para mayor limpieza visual
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # 8. Exportar
    ruta_exportacion = "Cascada_Operacional_2025.png"
    plt.tight_layout()
    plt.savefig(ruta_exportacion, dpi=300)
    print(f"[OK] Gráfico de Cascada exportado a: {ruta_exportacion}")
    plt.close()

if __name__ == '__main__':
    generar_cascada_operacional()