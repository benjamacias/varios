import argparse
from PIL import Image

# Tamaños estándar en milímetros
tamanos_hoja = {
    "A4": (210, 297),
    "Carta": (216, 279),
    "Oficio": (216, 356)
}

# Conversión de milímetros a píxeles
def mm_to_px(mm, dpi):
    return int((mm / 25.4) * dpi)

# Cargar imagen
def cargar_imagen(ruta_imagen):
    try:
        return Image.open(ruta_imagen)
    except Exception as e:
        raise IOError(f"No se pudo abrir la imagen: {e}")

# Calcular dimensiones y posiciones con separación
def calcular_posicion_optima(ruta_imagen, tipo_hoja="A4", cantidad_imagenes=1, separacion_mm=0, dpi=300, guardar=False):
    if tipo_hoja not in tamanos_hoja:
        raise ValueError(f"Tipo de hoja '{tipo_hoja}' no soportado. Usa: {', '.join(tamanos_hoja.keys())}")

    ancho_mm, alto_mm = tamanos_hoja[tipo_hoja]
    ancho_px = mm_to_px(ancho_mm, dpi)
    alto_px = mm_to_px(alto_mm, dpi)
    separacion_px = mm_to_px(separacion_mm, dpi)

    with cargar_imagen(ruta_imagen) as img:
        img_width, img_height = img.size

        print(f"Dimensiones imagen: {img_width}px ancho x {img_height}px alto")
        print(f"Dimensiones hoja {tipo_hoja}: {ancho_px}px ancho x {alto_px}px alto")

        columnas = int(cantidad_imagenes ** 0.5)
        filas = -(-cantidad_imagenes // columnas)

        espacio_ancho = (ancho_px - (columnas + 1) * separacion_px) // columnas
        espacio_alto = (alto_px - (filas + 1) * separacion_px) // filas

        escala = min(espacio_ancho / img_width, espacio_alto / img_height)
        nuevo_ancho = int(img_width * escala)
        nuevo_alto = int(img_height * escala)
        print(f"Imagen redimensionada a {nuevo_ancho}px x {nuevo_alto}px para {cantidad_imagenes} imágenes con separación de {separacion_mm}mm.")

        posicion_x = (espacio_ancho - nuevo_ancho) // 2
        posicion_y = (espacio_alto - nuevo_alto) // 2

        if guardar:
            hoja = Image.new('RGB', (ancho_px, alto_px), 'white')
            for fila in range(filas):
                for col in range(columnas):
                    if fila * columnas + col >= cantidad_imagenes:
                        break
                    x_offset = separacion_px + col * (espacio_ancho + separacion_px) + posicion_x
                    y_offset = separacion_px + fila * (espacio_alto + separacion_px) + posicion_y
                    hoja.paste(img.resize((nuevo_ancho, nuevo_alto), Image.LANCZOS), (x_offset, y_offset))
            hoja.save('imagen_ajustada.png')
            print("Hoja con múltiples imágenes y separación guardada como 'imagen_ajustada.png'")

    return {
        "posicion_x": posicion_x,
        "posicion_y": posicion_y,
        "nuevo_ancho": nuevo_ancho,
        "nuevo_alto": nuevo_alto,
        "columnas": columnas,
        "filas": filas,
        "cantidad_total": cantidad_imagenes
    }

# Interfaz CLI
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Distribuye imágenes en una hoja seleccionada con separación personalizada.')
    parser.add_argument('ruta_imagen', type=str, help='Ruta a la imagen a procesar.')
    parser.add_argument('--tipo_hoja', type=str, default='A4', choices=tamanos_hoja.keys(), help='Tipo de hoja para ajustar la imagen.')
    parser.add_argument('--cantidad', type=int, default=1, help='Cantidad de imágenes a colocar en la hoja.')
    parser.add_argument('--separacion', type=float, default=0, help='Separación entre imágenes en milímetros.')
    parser.add_argument('--dpi', type=int, default=300, help='Resolución de impresión en DPI.')
    parser.add_argument('--guardar', action='store_true', help='Guardar hoja con imágenes distribuidas.')

    args = parser.parse_args()

    posicion = calcular_posicion_optima(args.ruta_imagen, args.tipo_hoja, args.cantidad, args.separacion, args.dpi, args.guardar)

    print(f"Distribución óptima en hoja {args.tipo_hoja}: {posicion}")
