"""
Imagen personalizada: el reproductor se ADAPTA a la imagen.

Antes la foto quedaba nítida detrás de los textos y se veían rectángulos
planos sobre ella. Ahora:

  - Al elegir una imagen se calcula una paleta con sus colores: el tono
    dominante crea toda la paleta (fondos, paneles, hover, texto) y el color
    más vivo de la imagen pasa a ser el acento. Con eso los botones, las
    barras de volumen y reproducción, el aleatorio activo, etc. toman los
    colores de la imagen.
  - La imagen queda como un fondo suave de ambiente (siempre algo difuminada
    y mezclada con la paleta), sin rectángulos duros detrás de textos e
    iconos. Transparencia llega hasta dejar ver casi toda la imagen (15% de mezcla mínima); Difuminado siempre deja un suave mínimo.
  - Si luego eliges otra paleta o mueves «Color principal», se deja de usar
    la paleta de la imagen (la imagen se queda de fondo). Si vuelves a elegir
    la imagen, regresa su paleta.
  - El color propio de los botones sigue mandando si lo activas.

Requiere aplicar_fondo.py y aplicar_color_paleta.py primero.

Uso (en la carpeta de reproductor.py):
    python aplicar_imagen_paleta.py
Se crea una copia: reproductor_antes_de_imagen_paleta.py
"""
import sys
from pathlib import Path

ARCHIVO = Path(sys.argv[1] if len(sys.argv) > 1 else "reproductor.py")


def error(msg):
    raise SystemExit(
        "\nNo se cambió nada.\n" + msg +
        "\nPásale este mensaje a Claude para ajustarlo."
    )


FUNCIONES = '''_CACHE_PALETA_IMG = {}


def paleta_desde_imagen(ruta):
    """(color dominante, color vivo) de una imagen, o None si no se puede
    leer. El dominante crea la paleta; el vivo es el acento."""
    import colorsys
    try:
        clave = (ruta, os.path.getmtime(ruta))
    except (OSError, TypeError):
        return None
    if clave in _CACHE_PALETA_IMG:
        return _CACHE_PALETA_IMG[clave]
    resultado = None
    try:
        img = Image.open(ruta).convert("RGB")
        img.thumbnail((96, 96))
        q = img.quantize(colors=8, method=Image.Quantize.MEDIANCUT)
        pal = q.getpalette()[:24]
        cuentas = q.getcolors() or []
        total = float(sum(n for n, _ in cuentas)) or 1.0
        filas = []
        for n, i in cuentas:
            r, g, b = pal[3 * i], pal[3 * i + 1], pal[3 * i + 2]
            h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
            filas.append((n / total, l, s, rgb_a_hex((r, g, b))))
        medios = [f for f in filas if 0.08 < f[1] < 0.92] or filas
        dominante = max(medios, key=lambda f: f[0])[3]
        # El acento es el color más llamativo que NO sea el del fondo.
        vivos = [
            f for f in filas
            if f[3] != dominante and f[0] >= 0.02
            and 0.20 <= f[1] <= 0.85 and f[2] > 0.25
        ]
        vivo = (
            max(
                vivos,
                key=lambda f: f[2] * (0.3 + 0.7 * min(f[0] * 4, 1))
                * (1 - abs(f[1] - 0.58))
            )[3]
            if vivos else dominante
        )
        resultado = (dominante, vivo)
    except Exception:
        resultado = None
    _CACHE_PALETA_IMG[clave] = resultado
    return resultado


def acento_legible(tema, c):
    """(acento, acento_hover, boton, boton_hover) a partir de un color,
    ajustado para que se lea sobre el fondo de la paleta."""
    claro = luminancia(tema["FONDO"]) > 0.5
    ac = c
    if claro and luminancia(ac) > 0.55:
        ac = mezclar_hex(ac, "#000000", 0.55)
    elif not claro and luminancia(ac) < 0.18:
        ac = mezclar_hex(ac, "#ffffff", 0.45)
    peso = 0.82 if claro else 0.78
    return (
        ac, mezclar_hex(ac, "#ffffff", peso),
        c, mezclar_hex(c, "#ffffff", peso)
    )


def firma_paleta_fondo(a):
    """Qué parte del fondo decide la paleta (para saber cuándo reconstruir)."""
    t = a.get("fondo_tipo")
    if t == "color":
        return ("color", a.get("fondo_color"))
    if t == "imagen":
        return (
            "imagen", a.get("fondo_imagen"),
            bool(a.get("fondo_paleta_imagen", True))
        )
    return None


'''

# --------------------------------------------------------------------------
# Motor: las etiquetas ya no se convierten en imágenes (eso dibujaba cajas)
# --------------------------------------------------------------------------
LABEL_NUEVO = '''        elif clase == "Label":
            # Siempre color liso (el promedio de su zona): con el fondo
            # difuminado casi no se nota y no hay recuadros ni bordes.
            w.config(bg=medio)
            w._fondo_bg_puesto = medio

'''

CAMBIOS = [
    # 1) funciones nuevas antes de resolver_tema
    ("def resolver_tema(nombre, ajustes):\n",
     FUNCIONES + "def resolver_tema(nombre, ajustes):\n"),
    # 2) la paleta de la imagen en resolver_tema
    ('    if ajustes.get("fondo_tipo") == "color" and ajustes.get("fondo_color"):\n'
     '        tema = tema_desde_fondo(ajustes["fondo_color"])\n',
     '    pal_img = None\n'
     '    if (\n'
     '        ajustes.get("fondo_tipo") == "imagen"\n'
     '        and ajustes.get("fondo_paleta_imagen", True)\n'
     '        and ajustes.get("fondo_imagen")\n'
     '    ):\n'
     '        pal_img = paleta_desde_imagen(ajustes["fondo_imagen"])\n'
     '    if pal_img:\n'
     '        tema = tema_desde_fondo(pal_img[0])\n'
     '        (tema["ACENTO"], tema["ACENTO_HOVER"],\n'
     '         tema["ACENTO_BOTON"], tema["ACENTO_BOTON_HOVER"]) = (\n'
     '            acento_legible(tema, pal_img[1])\n'
     '        )\n'
     '    elif ajustes.get("fondo_tipo") == "color" and ajustes.get("fondo_color"):\n'
     '        tema = tema_desde_fondo(ajustes["fondo_color"])\n'),
    # 3) cambiar_personalizado: imagen y color deciden la paleta
    ('        antes_color = (a.get("fondo_tipo") == "color", a.get("fondo_color"))\n',
     '        antes_color = firma_paleta_fondo(a)\n'),
    ('        ahora_color = (a.get("fondo_tipo") == "color", a.get("fondo_color"))\n'
     '        cambia_paleta_color = (\n'
     '            (antes_color[0] or ahora_color[0]) and antes_color != ahora_color\n'
     '        )\n',
     '        ahora_color = firma_paleta_fondo(a)\n'
     '        cambia_paleta_color = antes_color != ahora_color\n'),
    ('        ahora_activo = a.get("fondo_tipo", "ninguno") != "ninguno"\n',
     '        if fondo_tipo == "imagen" or fondo_imagen is not None:\n'
     '            a["fondo_paleta_imagen"] = True   # vuelve la paleta de la imagen\n'
     '        ahora_activo = a.get("fondo_tipo", "ninguno") != "ninguno"\n'),
    ('                a["fondo_tipo"] = "ninguno"   # gana lo último que elijas\n',
     '                a["fondo_tipo"] = "ninguno"   # gana lo último que elijas\n'
     '            a["fondo_paleta_imagen"] = False\n'),
    # 4) elegir una paleta deja de usar la paleta de la imagen
    ('            self.ajustes["fondo_tipo"] = "ninguno"\n        self.tema_nombre = nombre\n',
     '            self.ajustes["fondo_tipo"] = "ninguno"\n'
     '        self.ajustes["fondo_paleta_imagen"] = False\n'
     '        self.tema_nombre = nombre\n'),
    ('    "fondo_color_elegido",\n',
     '    "fondo_color_elegido",\n    "fondo_paleta_imagen",\n'),
    # 5) la imagen siempre queda como fondo de ambiente
    ('    difuminado = max(0, min(100, int(difuminado)))\n'
     '    t = max(0, min(100, int(transparencia))) / 100\n',
     '    # Ambiente: nunca nítida ni sin mezclar con la paleta, para que los\n'
     '    # textos y los iconos no desentonen con la foto.\n'
     '    difuminado = 50 + max(0, min(100, int(difuminado))) * 0.5\n'
     '    t = (15 + max(0, min(100, int(transparencia))) * 0.85) / 100\n'),
    ('"Nítido", "Muy difuminado", 0', '"Suave", "Muy difuminado", 0'),
]


def main():
    if not ARCHIVO.exists():
        raise SystemExit(f"No encuentro {ARCHIVO}. Ejecútalo dentro de la carpeta de tu proyecto.")
    crudo = ARCHIVO.read_bytes().decode("utf-8")
    crlf = "\r\n" in crudo
    texto = crudo.replace("\r\n", "\n")

    if "def paleta_desde_imagen(" in texto:
        raise SystemExit("La paleta de la imagen ya estaba aplicada. No se cambió nada.")
    if "def _aplicar_fondo(self" not in texto:
        error("Primero hay que aplicar aplicar_fondo.py.")
    if "def tema_desde_fondo(" not in texto:
        error("Primero hay que aplicar aplicar_color_paleta.py.")

    for viejo, nuevo in CAMBIOS:
        n = texto.count(viejo)
        if n != 1:
            error(f"No encontré con claridad (apariciones: {n}) este punto de tu código:\n    {viejo.strip()[:90]!r}")
        texto = texto.replace(viejo, nuevo, 1)

    # Bloque de etiquetas del motor: de «elif clase == "Label"» a «Canvas».
    ini = '        elif clase == "Label":\n'
    fin = '        elif clase == "Canvas":\n'
    if texto.count(ini) != 1 or texto.count(fin) != 1:
        error("No encontré el bloque de etiquetas del motor del fondo.")
    i, j = texto.index(ini), texto.index(fin)
    if j < i:
        error("Orden inesperado en el motor del fondo.")
    texto = texto[:i] + LABEL_NUEVO + texto[j:]

    compile(texto, str(ARCHIVO), "exec")
    copia = ARCHIVO.with_name("reproductor_antes_de_imagen_paleta.py")
    copia.write_bytes(crudo.encode("utf-8"))
    if crlf:
        texto = texto.replace("\n", "\r\n")
    ARCHIVO.write_bytes(texto.encode("utf-8"))
    print("Listo. La imagen ahora crea la paleta y queda como fondo de ambiente.")
    print(f"Copia de seguridad: {copia.name}")


if __name__ == "__main__":
    main()
