import io
import json
import os
import random
import threading
import time
import tkinter as tk
import tkinter.font as tkfont
import urllib.request
import webbrowser
import zlib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tkinter import colorchooser, messagebox, filedialog, ttk
from PIL import Image, ImageTk, ImageFilter
import vlc
import yt_dlp
from PIL import Image, ImageDraw, ImageFont, ImageTk
try:
    from presencia_discord import PresenciaDiscord
except ImportError:          # el archivo no está junto al programa
    PresenciaDiscord = None


# ==============================================================
# PALETAS DE COLORES
# ==============================================================
# Para añadir una paleta propia, copia uno de los bloques de abajo, cámbiale
# el nombre y los colores, y aparecerá sola en Apariencia.
#
#   FONDO        fondo principal         PANEL         barra lateral e inferior
#   PANEL_HOVER  fila resaltada          PISTA         pista de las barras
#   TEXTO        texto principal         TEXTO_SUAVE   texto secundario
#   ACENTO       color de acento         ACENTO_HOVER  acento al pasar el mouse
TEMA_POR_DEFECTO = "Morado nocturno"
TEMA_PERSONALIZADO = "Personalizado"

TEMAS = {
    "Morado nocturno": {
        "FONDO": "#0f0f14", "PANEL": "#16161d", "PANEL_HOVER": "#262633",
        "PISTA": "#3a3a52", "TEXTO": "#f2f2f7", "TEXTO_SUAVE": "#8e8ea0",
        "ACENTO": "#7c5cff", "ACENTO_HOVER": "#957bff",
    },
    "Océano": {
        "FONDO": "#0b1117", "PANEL": "#111b24", "PANEL_HOVER": "#1b2a38",
        "PISTA": "#2f4558", "TEXTO": "#eaf3fa", "TEXTO_SUAVE": "#8aa0b2",
        "ACENTO": "#2ea8ff", "ACENTO_HOVER": "#5cbcff",
    },
    "Esmeralda": {
        "FONDO": "#0c130f", "PANEL": "#121c16", "PANEL_HOVER": "#1d2b23",
        "PISTA": "#33483c", "TEXTO": "#eef7f1", "TEXTO_SUAVE": "#8ba294",
        "ACENTO": "#1ed760", "ACENTO_HOVER": "#4ae584",
    },
    "Atardecer": {
        "FONDO": "#150e0c", "PANEL": "#1e1512", "PANEL_HOVER": "#2e211c",
        "PISTA": "#4a352d", "TEXTO": "#fbf1ec", "TEXTO_SUAVE": "#a8918a",
        "ACENTO": "#ff7a45", "ACENTO_HOVER": "#ff9a6e",
    },
    "Rosa neón": {
        "FONDO": "#140d13", "PANEL": "#1c121b", "PANEL_HOVER": "#2c1c2a",
        "PISTA": "#47304a", "TEXTO": "#fbeef6", "TEXTO_SUAVE": "#a58a9f",
        "ACENTO": "#ff4fa3", "ACENTO_HOVER": "#ff7bbb",
    },
    "Carmesí": {
        "FONDO": "#120c0d", "PANEL": "#1a1113", "PANEL_HOVER": "#2a1b1e",
        "PISTA": "#46303a", "TEXTO": "#f8eef0", "TEXTO_SUAVE": "#a58d92",
        "ACENTO": "#e5384f", "ACENTO_HOVER": "#ee6174",
    },
    "AMOLED": {
        "FONDO": "#000000", "PANEL": "#0b0b0b", "PANEL_HOVER": "#1b1b1b",
        "PISTA": "#383838", "TEXTO": "#ffffff", "TEXTO_SUAVE": "#9a9a9a",
        "ACENTO": "#b794ff", "ACENTO_HOVER": "#cdb4ff",
    },
    # ---------------- MINIMALISTA ----------------
    "Blanco limpio": {
        "FONDO": "#f8f8f6", "PANEL": "#eeeeec", "PANEL_HOVER": "#dededb",
        "PISTA": "#c8c8c4", "TEXTO": "#202020", "TEXTO_SUAVE": "#747474",
        "ACENTO": "#7a68c7", "ACENTO_HOVER": "#927fe0",
    },
    "Gris elegante": {
        "FONDO": "#eeeeee", "PANEL": "#e2e2e2", "PANEL_HOVER": "#d2d2d2",
        "PISTA": "#bdbdbd", "TEXTO": "#202020", "TEXTO_SUAVE": "#707070",
        "ACENTO": "#3f3f46", "ACENTO_HOVER": "#5a5a63",
    },
    "Beige cálido": {
        "FONDO": "#f5efe5", "PANEL": "#ebe1d2", "PANEL_HOVER": "#ddd0bd",
        "PISTA": "#c9b89f", "TEXTO": "#3b332b", "TEXTO_SUAVE": "#7d6f60",
        "ACENTO": "#b56f52", "ACENTO_HOVER": "#c98264",
    },
    "Lavanda suave": {
        "FONDO": "#f5f2fa", "PANEL": "#ebe6f4", "PANEL_HOVER": "#ddd6eb",
        "PISTA": "#c8bfd8", "TEXTO": "#302b38", "TEXTO_SUAVE": "#777080",
        "ACENTO": "#8b79b7", "ACENTO_HOVER": "#a08dcc",
    },
    "Azul hielo": {
        "FONDO": "#f2f7fa", "PANEL": "#e5eef3", "PANEL_HOVER": "#d5e2e9",
        "PISTA": "#b9ccd7", "TEXTO": "#26343b", "TEXTO_SUAVE": "#6f8089",
        "ACENTO": "#5f91aa", "ACENTO_HOVER": "#76a9c0",
    },
    "Verde salvia": {
        "FONDO": "#f2f5f0", "PANEL": "#e4ebe1", "PANEL_HOVER": "#d4dfd0",
        "PISTA": "#b8c8b2", "TEXTO": "#29332a", "TEXTO_SUAVE": "#718071",
        "ACENTO": "#718f70", "ACENTO_HOVER": "#89a688",
    },
    "Rosa empolvado": {
        "FONDO": "#faf3f4", "PANEL": "#f0e3e5", "PANEL_HOVER": "#e3d2d6",
        "PISTA": "#ceb9be", "TEXTO": "#382d30", "TEXTO_SUAVE": "#806f73",
        "ACENTO": "#b9828e", "ACENTO_HOVER": "#cb9aa5",
    },
    # Alias conservado para no romper configuraciones antiguas que tengan "Claro".
    "Claro": {
        "FONDO": "#f6f6fa", "PANEL": "#ececf3", "PANEL_HOVER": "#dedee9",
        "PISTA": "#c3c3d4", "TEXTO": "#1b1b28", "TEXTO_SUAVE": "#6b6b80",
        "ACENTO": "#6c4cf0", "ACENTO_HOVER": "#5638d4",
    },
}


def aplicar_tema(tema):
    """Cambia los colores globales. Todo lo que se construya después los usa."""
    global FONDO, PANEL, PANEL_HOVER, PISTA, TEXTO, TEXTO_SUAVE
    global ACENTO, ACENTO_HOVER, ACENTO_BOTON, ACENTO_BOTON_HOVER
    FONDO = tema["FONDO"]
    PANEL = tema["PANEL"]
    PANEL_HOVER = tema["PANEL_HOVER"]
    PISTA = tema["PISTA"]
    TEXTO = tema["TEXTO"]
    TEXTO_SUAVE = tema["TEXTO_SUAVE"]
    ACENTO = tema["ACENTO"]
    ACENTO_HOVER = tema["ACENTO_HOVER"]
    # Color de los botones: por defecto el mismo acento de la paleta.
    ACENTO_BOTON = tema.get("ACENTO_BOTON", ACENTO)
    ACENTO_BOTON_HOVER = tema.get("ACENTO_BOTON_HOVER", ACENTO_HOVER)


aplicar_tema(TEMAS[TEMA_POR_DEFECTO])


# ==============================================================
# TAMAÑOS
# ==============================================================
FUENTE = "Segoe UI"
FUENTE_ICONOS = "Segoe UI Symbol"

TAM_VENTANA = "1000x640"
ANCHO_LATERAL = 230
ALTO_BARRA = 92

TAM_MINIATURA = 40
ALTO_FILA = 56
ALTO_CABECERA_TABLA = 32
TAM_PORTADA = 140
TAM_CARATULA_BARRA = 56
ALTO_DEGRADADO = 28

# Anchos de las columnas de la tabla
COL_NUM = 52
COL_MINI = 52
COL_ARTISTA = 200
COL_DUR = 84
COL_CORAZON = 44

PALETA_PLAYLISTS = [
    "#6b4fd8", "#2f8f83", "#b0507a",
    "#b0803a", "#3f6fb5", "#7f9a3a"
]


# Archivos donde se guardan las playlists y los ajustes.
# Van en la carpeta del usuario (AppData), así cada persona tiene los suyos
# y no se pierden al cerrar el .exe.
def carpeta_datos():
    base = os.environ.get("APPDATA") or str(Path.home())
    carpeta = Path(base) / "Otium"
    carpeta.mkdir(parents=True, exist_ok=True)
    return carpeta


ARCHIVO_PLAYLISTS = carpeta_datos() / "playlists.json"
ARCHIVO_AJUSTES = carpeta_datos() / "ajustes.json"
ARCHIVO_FAVORITOS = carpeta_datos() / "favoritos.json"

# Si ya tenías un playlists.json junto al script, se copia una sola vez.
_ARCHIVO_ANTIGUO = Path(__file__).resolve().with_name("playlists.json")
if not ARCHIVO_PLAYLISTS.exists() and _ARCHIVO_ANTIGUO.exists():
    ARCHIVO_PLAYLISTS.write_bytes(_ARCHIVO_ANTIGUO.read_bytes())

REP_NO, REP_LISTA, REP_UNA = 0, 1, 2

# Cuánto tiempo se considera válido un enlace de audio ya resuelto
# (los enlaces de YouTube caducan a las pocas horas).
TTL_AUDIO = 2 * 3600

# ID de tu aplicación de Discord. Es solo un número entre comillas.   ← AÑADIR AQUÍ (2 líneas)
DISCORD_CLIENT_ID = "1556297145009840270"

MARCAS_NO_DISPONIBLE = (
    "private video", "deleted video", "unavailable video",
    "video privado", "video eliminado", "video no disponible",
    "no disponible", "borrado"
)
AVAILABILITY_MALA = (
    "private", "needs_auth", "premium_only", "subscriber_only"
)

# Errores que indican que ESA canción no se podrá reproducir nunca.
ERRORES_ACCESO = (
    "age-restricted",
    "age restricted",
    "confirm your age",
    "members-only",
    "members only",
    "private video",
    "this video is private",
    "video unavailable",
    "video is unavailable",
    "this video is not available",
    "music premium",
    "login required",
    "sign in required",
)

# Errores pasajeros (red, límites, bloqueo anti-bots): nunca descartan canciones.
ERRORES_TEMPORALES = (
    "not a bot",
    "http error 429",
    "http error 5",
    "timed out",
    "temporary failure",
    "connection",
    "network",
    "unable to download",
)


# ==============================================================
# AJUSTES (paleta elegida, etc.)
# ==============================================================
def cargar_ajustes():
    try:
        datos = json.loads(ARCHIVO_AJUSTES.read_text(encoding="utf-8"))
        return datos if isinstance(datos, dict) else {}
    except Exception:
        return {}


def guardar_ajustes(ajustes):
    try:
        ARCHIVO_AJUSTES.write_text(
            json.dumps(ajustes, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
    except Exception:
        pass


def entero_en_rango(valor, defecto, minimo, maximo):
    """Convierte un valor guardado en un entero válido (o usa el por defecto)."""
    try:
        return max(minimo, min(maximo, int(valor)))
    except (TypeError, ValueError, OverflowError):
        return defecto


def nombre_tema_valido(ajustes):
    nombre = ajustes.get("tema")
    if nombre == TEMA_PERSONALIZADO and ajustes.get("acento_personalizado"):
        return nombre
    if nombre in TEMAS:
        return nombre
    return TEMA_POR_DEFECTO


# ==============================================================
# ÍCONOS
# ==============================================================
# Windows 11 trae "Segoe Fluent Icons" y Windows 10 "Segoe MDL2 Assets":
# ambas usan los mismos códigos. Si no existen, se usan símbolos normales.
GLIFOS_FLUENT = {
    "play": "\uE768", "pausa": "\uE769",
    "anterior": "\uE892", "siguiente": "\uE893",
    "aleatorio": "\uE8B1",
    "repetir": "\uE8EE", "repetir1": "\uE8ED",
    "volumen": "\uE767", "mudo": "\uE74F",
    "buscar": "\uE721", "reloj": "\uE121",
    "mas": "\uE712", "paleta": "\uE790", "abajo": "\uE70D",
    "atras": "\uE72B",
    "nuevo": "\uE710",
    "corazon": "\uEB51", "corazon_lleno": "\uEB52",
}
GLIFOS_SIMPLES = {
    "play": "▶", "pausa": "⏸",
    "anterior": "⏮", "siguiente": "⏭",
    "aleatorio": "🔀",
    "repetir": "🔁", "repetir1": "🔂",
    "volumen": "🔊", "mudo": "🔇",
    "buscar": "🔍", "reloj": "🕒",
    "mas": "⋯", "paleta": "🎨", "abajo": "▾",
    "atras": "←",
    "nuevo": "+",
    "corazon": "♡", "corazon_lleno": "♥",
}
GLIFOS = GLIFOS_SIMPLES
FUENTE_ICO = FUENTE_ICONOS


def configurar_iconos(root):
    global GLIFOS, FUENTE_ICO
    familias = set(tkfont.families(root))
    if "Segoe Fluent Icons" in familias:
        FUENTE_ICO, GLIFOS = "Segoe Fluent Icons", GLIFOS_FLUENT
    elif "Segoe MDL2 Assets" in familias:
        FUENTE_ICO, GLIFOS = "Segoe MDL2 Assets", GLIFOS_FLUENT
    else:
        FUENTE_ICO, GLIFOS = FUENTE_ICONOS, GLIFOS_SIMPLES


def glifo(nombre):
    return GLIFOS[nombre]


# ==============================================================
# UTILIDADES DE COLOR E IMAGEN
# ==============================================================
def hex_a_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb_a_hex(rgb):
    return "#%02x%02x%02x" % tuple(int(max(0, min(255, v))) for v in rgb)


def mezclar_hex(a, b, t):
    """Mezcla dos colores: t = cuánto pesa 'a' (0 a 1)."""
    ra, rb = hex_a_rgb(a), hex_a_rgb(b)
    return rgb_a_hex(tuple(ra[i] * t + rb[i] * (1 - t) for i in range(3)))


def luminancia(hex_color):
    r, g, b = (c / 255 for c in hex_a_rgb(hex_color))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def color_sobre(hex_color):
    """Negro o blanco, según cuál se lea mejor sobre ese color."""
    return "#0b0b10" if luminancia(hex_color) > 0.6 else "#ffffff"


def tema_desde_acento(acento, claro=False, intensidad=50):
    """Genera una paleta completa a partir del color elegido por el usuario.
    Oscura por defecto; con claro=True usa fondos claros. La intensidad
    (0 a 100) controla cuánto se tiñen los fondos con el color."""
    try:
        i = min(max(float(intensidad), 0), 100) / 100
    except (TypeError, ValueError):
        i = 0.5
    k = 0.4 + 1.2 * i          # 0.4 (suave) ... 1.0 (normal) ... 1.6 (intenso)

    def t(base):
        return min(base * k, 0.6)

    if claro:
        # Sobre un fondo claro el acento debe ser lo bastante oscuro.
        if luminancia(acento) > 0.55:
            acento = mezclar_hex(acento, "#000000", 0.62)
        return {
            "FONDO": mezclar_hex(acento, "#fbfaf8", t(0.05)),
            "PANEL": mezclar_hex(acento, "#efeeec", t(0.08)),
            "PANEL_HOVER": mezclar_hex(acento, "#e0dfdc", t(0.14)),
            "PISTA": mezclar_hex(acento, "#c9c8c4", t(0.22)),
            "TEXTO": "#202020",
            "TEXTO_SUAVE": "#747474",
            "ACENTO": acento,
            "ACENTO_HOVER": mezclar_hex(acento, "#ffffff", 0.82),
        }

    if luminancia(acento) < 0.22:
        acento = mezclar_hex(acento, "#ffffff", 0.55)

    return {
        "FONDO": mezclar_hex(acento, "#0d0d12", t(0.05)),
        "PANEL": mezclar_hex(acento, "#15151c", t(0.07)),
        "PANEL_HOVER": mezclar_hex(acento, "#222230", t(0.12)),
        "PISTA": mezclar_hex(acento, "#38384d", t(0.18)),
        "TEXTO": "#f2f2f7",
        "TEXTO_SUAVE": "#8e8ea0",
        "ACENTO": acento,
        "ACENTO_HOVER": mezclar_hex(acento, "#ffffff", 0.78),
    }


def lum_relativa(hex_color):
    """Luminancia relativa (con gamma), como la usa el contraste WCAG."""
    def f(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = hex_a_rgb(hex_color)
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def tono_con_luminancia(h, s, lum):
    """Color de matiz h y saturación s con la luminancia pedida."""
    import colorsys
    bajo, alto = 0.0, 1.0
    for _ in range(18):
        l = (bajo + alto) / 2
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        if lum_relativa(rgb_a_hex((r * 255, g * 255, b * 255))) < lum:
            bajo = l
        else:
            alto = l
    r, g, b = colorsys.hls_to_rgb(h, (bajo + alto) / 2, s)
    return rgb_a_hex((r * 255, g * 255, b * 255))


def tema_desde_fondo(color):
    """Paleta completa a partir de un color de fondo. Si el color es claro,
    todo queda en tonos claros de ese matiz (texto oscuro); si es oscuro,
    en tonos oscuros (texto claro)."""
    import colorsys
    r, g, b = (c / 255 for c in hex_a_rgb(color))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    if s < 0.04:
        s = 0.0
    lc = lum_relativa(color)
    t = tono_con_luminancia

    if lc >= 0.30:                       # --- paleta clara ---
        panel = min(max(lc, 0.50), 0.80)
        s = min(s, 0.90)
        s_txt = min(s, 0.30)
        s_ac = min(max(s, 0.50), 0.85) if s else 0.0
        return {
            "FONDO": t(h, s, panel + (1 - panel) * 0.45),
            "PANEL": t(h, s, panel),
            "PANEL_HOVER": t(h, s, panel * 0.86),
            "PISTA": t(h, s, panel * 0.68),
            "TEXTO": t(h, s_txt, 0.012),
            "TEXTO_SUAVE": t(h, min(s, 0.20), 0.085),
            "ACENTO": t(h, s_ac, 0.10),
            "ACENTO_HOVER": t(h, s_ac, 0.17),
        }

    panel = min(max(lc, 0.008), 0.045)   # --- paleta oscura ---
    s = min(s, 0.85)
    s_txt = min(s, 0.30)
    s_ac = min(max(s, 0.55), 0.90) if s else 0.0
    return {
        "FONDO": t(h, s, panel * 0.55),
        "PANEL": t(h, s, panel),
        "PANEL_HOVER": t(h, s, panel * 1.9 + 0.004),
        "PISTA": t(h, s, panel * 3.2 + 0.010),
        "TEXTO": t(h, s_txt, 0.86),
        "TEXTO_SUAVE": t(h, min(s, 0.20), 0.40),
        "ACENTO": t(h, s_ac, 0.36),
        "ACENTO_HOVER": t(h, s_ac, 0.50),
    }


_CACHE_PALETA_IMG = {}


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


PALETA_PORTADA = None      # (dominante, vivo) de la portada que está sonando


def paleta_desde_pil(img):
    """(color dominante, color vivo) de una imagen ya abierta."""
    import colorsys
    img = img.convert("RGB")
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
    return (dominante, vivo)


def poner_paleta_portada(pal):
    global PALETA_PORTADA
    PALETA_PORTADA = pal


def paletas_distintas(a, b, umbral=36):
    """¿Cambió lo bastante la paleta como para valer la pena repintar?"""
    if not a or not b:
        return True
    for x, y in zip(a, b):
        ca, cb = hex_a_rgb(x), hex_a_rgb(y)
        if sum(abs(ca[i] - cb[i]) for i in range(3)) > umbral:
            return True
    return False


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


def resolver_tema(nombre, ajustes):
    pal_img = None
    modo_color = ajustes.get("color_interfaz", "personalizado")
    if modo_color == "portada" and PALETA_PORTADA:
        pal_img = PALETA_PORTADA
    elif (
        ajustes.get("fondo_tipo") == "imagen"
        and ajustes.get("fondo_paleta_imagen", True)
        and ajustes.get("fondo_imagen")
    ):
        pal_img = paleta_desde_imagen(ajustes["fondo_imagen"])
    if pal_img:
        tema = tema_desde_fondo(pal_img[0])
        (tema["ACENTO"], tema["ACENTO_HOVER"],
         tema["ACENTO_BOTON"], tema["ACENTO_BOTON_HOVER"]) = (
            acento_legible(tema, pal_img[1])
        )
    elif ajustes.get("fondo_tipo") == "color" and ajustes.get("fondo_color"):
        tema = tema_desde_fondo(ajustes["fondo_color"])
    elif nombre == TEMA_PERSONALIZADO and ajustes.get("acento_personalizado"):
        tema = tema_desde_acento(
            ajustes["acento_personalizado"],
            claro=ajustes.get("modo_personalizado") == "claro",
            intensidad=ajustes.get("intensidad_personalizado", 50)
        )
    else:
        tema = dict(TEMAS.get(nombre, TEMAS[TEMA_POR_DEFECTO]))

    # Automático: la paleta se queda y el acento sale de la portada.
    if modo_color == "automatico" and PALETA_PORTADA:
        (tema["ACENTO"], tema["ACENTO_HOVER"],
         tema["ACENTO_BOTON"], tema["ACENTO_BOTON_HOVER"]) = (
            acento_legible(tema, PALETA_PORTADA[1])
        )

    # Color propio para los botones (vale para cualquier paleta).
    if ajustes.get("botones_propios") and ajustes.get("color_botones"):
        c = ajustes["color_botones"]
        claro = luminancia(tema["FONDO"]) > 0.5
        tema["ACENTO_BOTON"] = c
        tema["ACENTO_BOTON_HOVER"] = mezclar_hex(
            c, "#ffffff", 0.82 if claro else 0.78
        )
        # El mismo color tiñe barras, iconos activos y textos destacados,
        # ajustado para que se lea sobre el fondo de la paleta.
        ac = c
        if claro and luminancia(ac) > 0.55:
            ac = mezclar_hex(ac, "#000000", 0.55)
        elif not claro and luminancia(ac) < 0.18:
            ac = mezclar_hex(ac, "#ffffff", 0.45)
        tema["ACENTO"] = ac
        tema["ACENTO_HOVER"] = mezclar_hex(
            ac, "#ffffff", 0.82 if claro else 0.78
        )
    return tema


def colorear_barra_titulo(root, color_fondo, color_texto):
    """Pinta la barra de título de Windows con los colores de la paleta.
    Funciona en Windows 11; en Windows 10 solo la pone en modo oscuro/claro.
    En otros sistemas no hace nada."""
    if os.name != "nt":
        return
    try:
        import ctypes

        root.update_idletasks()
        hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
        dwm = ctypes.windll.dwmapi

        def colorref(hex_color):
            r, g, b = hex_a_rgb(hex_color)
            return r | (g << 8) | (b << 16)

        def poner(atributo, valor):
            v = ctypes.c_int(valor)
            return dwm.DwmSetWindowAttribute(
                hwnd, atributo, ctypes.byref(v), ctypes.sizeof(v)
            )

        # Modo oscuro de la barra (el atributo es 20, o 19 en Windows 10 antiguos).
        oscuro = 1 if luminancia(color_fondo) < 0.5 else 0
        if poner(20, oscuro) != 0:
            poner(19, oscuro)

        poner(35, colorref(color_fondo))   # color de la barra de título
        poner(36, colorref(color_texto))   # color del texto de la barra
        poner(34, colorref(color_fondo))   # color del borde de la ventana
    except Exception:
        pass


def tinte(rgb):
    """Color de la cabecera a partir del color dominante de la portada."""
    return mezclar_hex(rgb_a_hex(rgb), FONDO, 0.36)


def color_playlist(playlist):
    if playlist.get("virtual"):
        return ACENTO
    clave = (playlist.get("url") or playlist.get("nombre") or "").encode("utf-8")
    return PALETA_PLAYLISTS[zlib.crc32(clave) % len(PALETA_PLAYLISTS)]


def redondear(img, radio=14):
    """Devuelve la imagen con las esquinas redondeadas (transparentes)."""
    img = img.convert("RGBA")
    mascara = Image.new("L", img.size, 0)
    ImageDraw.Draw(mascara).rounded_rectangle(
        (0, 0, img.size[0] - 1, img.size[1] - 1),
        radius=radio, fill=255
    )
    img.putalpha(mascara)
    return img


def icono_nota(tam, color, radio=8, escala_nota=0.5, color_nota=(255, 255, 255, 235), simbolo="♪"):
    """Cuadrado redondeado de color con una nota musical."""
    img = Image.new("RGBA", (tam, tam), (0, 0, 0, 0))
    dibujo = ImageDraw.Draw(img)
    dibujo.rounded_rectangle(
        (0, 0, tam - 1, tam - 1), radius=radio, fill=color
    )
    if escala_nota:
        for nombre in ("seguisym.ttf", "DejaVuSans.ttf"):
            try:
                fuente = ImageFont.truetype(nombre, int(tam * escala_nota))
                dibujo.text(
                    (tam / 2, tam / 2), simbolo, font=fuente,
                    fill=color_nota, anchor="mm"
                )
                break
            except Exception:
                continue
    return img


def icono_nueva(tam=36):
    """Cuadrado punteado con un '+', para 'Nueva playlist'."""
    img = Image.new("RGBA", (tam, tam), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = hex_a_rgb(TEXTO_SUAVE) + (255,)
    m = tam - 2
    for x in range(4, m - 3, 6):
        d.line((x, 1, x + 3, 1), fill=c, width=1)
        d.line((x, m, x + 3, m), fill=c, width=1)
    for y in range(4, m - 3, 6):
        d.line((1, y, 1, y + 3), fill=c, width=1)
        d.line((m, y, m, y + 3), fill=c, width=1)
    mid = tam // 2
    d.line((mid - 6, mid, mid + 6, mid), fill=c, width=2)
    d.line((mid, mid - 6, mid, mid + 6), fill=c, width=2)
    return img


# ==============================================================
# FUNCIONES AUXILIARES DE TEXTO / DATOS
# ==============================================================
def formato_seg(s):
    s = max(int(s or 0), 0)
    return f"{s // 60}:{s % 60:02d}"


def formato_total(segundos):
    m = int(segundos) // 60
    h, m = divmod(m, 60)
    return f"{h} h {m} min" if h else f"{m} min"


def cortar(texto, maximo):
    return texto if len(texto) <= maximo else texto[: maximo - 1].rstrip() + "…"


def ajustar(texto, fuente, ancho):
    """Recorta el texto con '…' para que quepa en 'ancho' píxeles."""
    if fuente.measure(texto) <= ancho:
        return texto
    lo, hi = 0, len(texto)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if fuente.measure(texto[:mid] + "…") <= ancho:
            lo = mid
        else:
            hi = mid - 1
    return texto[:lo].rstrip() + "…"


def esta_disponible(entrada):
    titulo = (entrada.get("title") or "").strip()
    if not titulo:
        return False
    if entrada.get("availability") in AVAILABILITY_MALA:
        return False
    bajo = titulo.lower()
    if bajo.startswith("[") and bajo.endswith("]") and any(
        m in bajo for m in MARCAS_NO_DISPONIBLE
    ):
        return False
    return True


def es_playlist_no_accesible(error):
    texto = str(error).lower()
    marcas = (
        "playlist does not exist",
        "this playlist does not exist",
        "playlist is private",
        "private playlist",
        "playlist not available",
        "playlist is unavailable",
        "not available to you",
        "login required",
        "sign in required",
        "requires authentication",
        "authentication required",
    )
    return any(marca in texto for marca in marcas)


def es_error_de_acceso(error):
    """True solo si el error es permanente para ESA canción."""
    texto = str(error).lower()
    if any(m in texto for m in ERRORES_TEMPORALES):
        return False
    return any(m in texto for m in ERRORES_ACCESO)


def mensaje_error_playlist(error, accion="cargar"):
    if es_playlist_no_accesible(error):
        return (
            "No se pudo acceder a esta playlist.\n\n"
            "Parece que es privada o que YouTube no permite acceder "
            "a ella sin iniciar sesión.\n\n"
            "Hazla pública o no listada en YouTube y vuelve a intentarlo."
        )
    return f"No se pudo {accion} la playlist:\n{error}"


def leer_playlist(url):
    """Lee una playlist de YouTube. Devuelve (nombre, lista_de_pistas).
    Cada pista es (titulo, id_video, artista, duracion)."""
    opciones = {
        "extract_flat": True,
        "quiet": True,
        "ignoreerrors": True
    }

    with yt_dlp.YoutubeDL(opciones) as ydl:
        info = ydl.extract_info(url, download=False)

    # Con ignoreerrors=True, yt-dlp devuelve None si no puede acceder.
    if not info:
        raise Exception("playlist does not exist or is private")

    entradas = [
        e for e in (info.get("entries") or [info])
        if e and e.get("id")
    ]

    pistas = []
    for e in entradas:
        if not esta_disponible(e):
            continue

        artista = e.get("channel") or e.get("uploader") or ""
        artista = artista.removesuffix(" - Topic")

        pistas.append((
            e["title"].strip(),
            e["id"],
            artista,
            e.get("duration")
        ))

    nombre = info.get("title") or "Nueva playlist"
    return str(nombre), pistas


def resolver_audio(video_id):
    """Pide a yt-dlp el enlace directo del audio de un video.
    Es la parte lenta (1 a 4 segundos), por eso se hace por adelantado."""
    url = f"https://www.youtube.com/watch?v={video_id}"
    with yt_dlp.YoutubeDL({"format": "bestaudio/best", "quiet": True}) as ydl:
        info = ydl.extract_info(url, download=False)
    try:
        ALBUMES[video_id] = (info.get("album") or "").strip()
    except Exception:
        pass
    return info["url"]


def descargar_cuadrada(video_id, tam):
    """Descarga la miniatura de un video y la recorta en cuadrado.
    Devuelve (imagen_cuadrada_RGB, color_promedio)."""
    url = f"https://i.ytimg.com/vi/{video_id}/mqdefault.jpg"
    with urllib.request.urlopen(url, timeout=10) as r:
        datos = r.read()
    img = Image.open(io.BytesIO(datos)).convert("RGB")
    w, h = img.size
    lado = min(w, h)
    izq, arr = (w - lado) // 2, (h - lado) // 2
    img = img.crop((izq, arr, izq + lado, arr + lado))
    color = img.resize((1, 1), Image.Resampling.BOX).getpixel((0, 0))
    img = img.resize((tam, tam), Image.Resampling.LANCZOS)
    return img, color


# ==============================================================
# WIDGETS PROPIOS
# (los colores por defecto se leen al crear el widget, no al
# definir la clase, para que sigan la paleta activa)
# ==============================================================
class Slider(tk.Canvas):
    """Barra plana: pista fina, relleno de color y perilla que
    aparece al pasar el mouse."""

    def __init__(
        self, padre, desde=0, hasta=100, valor=0, ancho=200, fondo=None,
        al_presionar=None, al_mover=None, al_soltar=None
    ):
        super().__init__(
            padre, width=ancho, height=24,
            bg=FONDO if fondo is None else fondo,
            highlightthickness=0, bd=0, cursor="hand2"
        )
        self.desde, self.hasta, self.valor = desde, hasta, valor
        self.al_presionar = al_presionar
        self.al_mover = al_mover
        self.al_soltar = al_soltar
        self.activo = False
        self.encima = False

        self.bind("<Configure>", lambda e: self._dibujar())
        self.bind("<ButtonPress-1>", self._presionar)
        self.bind("<B1-Motion>", self._mover)
        self.bind("<ButtonRelease-1>", self._soltar)
        self.bind("<Enter>", lambda e: self._hover(True))
        self.bind("<Leave>", lambda e: self._hover(False))

    def get(self):
        return self.valor

    def set(self, valor):
        if self.activo:
            return
        self.valor = valor
        self._dibujar()

    def _hover(self, estado):
        self.encima = estado
        self._dibujar()

    def _valor_en(self, x):
        ancho_util = max(self.winfo_width() - 16, 1)
        frac = min(max((x - 8) / ancho_util, 0), 1)
        return self.desde + frac * (self.hasta - self.desde)

    def _presionar(self, e):
        self.activo = True
        if self.al_presionar:
            self.al_presionar()
        self._mover(e)

    def _mover(self, e):
        self.valor = self._valor_en(e.x)
        self._dibujar()
        if self.al_mover:
            self.al_mover(self.valor)

    def _soltar(self, e):
        self.valor = self._valor_en(e.x)
        self.activo = False
        self._dibujar()
        if self.al_soltar:
            self.al_soltar()

    def _dibujar(self):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        if w < 20:
            return
        y = h // 2
        frac = (self.valor - self.desde) / (self.hasta - self.desde)
        frac = min(max(frac, 0), 1)
        xv = 8 + (w - 16) * frac
        resaltado = self.activo or self.encima

        self.create_line(
            8, y, w - 8, y, width=4,
            fill=PISTA, capstyle="round"
        )
        if xv > 8:
            self.create_line(
                8, y, xv, y, width=4, capstyle="round",
                fill=ACENTO_HOVER if resaltado else ACENTO
            )
        if resaltado:
            self.create_oval(
                xv - 7, y - 7, xv + 7, y + 7,
                fill=TEXTO, outline=""
            )


class BotonIcono(tk.Label):
    """Botón de ícono plano que cambia de color al pasar el mouse."""

    def __init__(
        self, padre, nombre, comando, tam=14,
        fondo=None, color=None, color_hover=None
    ):
        fondo = FONDO if fondo is None else fondo
        color = TEXTO_SUAVE if color is None else color
        color_hover = TEXTO if color_hover is None else color_hover
        super().__init__(
            padre, text=glifo(nombre), font=(FUENTE_ICO, tam),
            bg=fondo, fg=color, cursor="hand2", padx=8, pady=4
        )
        self.activo = False
        self.color_base = color
        self.color_hover = color_hover
        self.color_normal = color
        self.hover_normal = color_hover
        self.bind("<Button-1>", lambda e: comando())
        self.bind("<Enter>", lambda e: self.config(fg=self.color_hover))
        self.bind("<Leave>", lambda e: self.config(fg=self.color_base))

    def set_icono(self, nombre):
        self.config(text=glifo(nombre))

    def set_activo(self, activo):
        self.activo = activo
        if activo:
            self.color_base, self.color_hover = ACENTO, ACENTO_HOVER
        else:
            self.color_base, self.color_hover = self.color_normal, self.hover_normal
        self.config(fg=self.color_base)


class BotonCircular(tk.Canvas):
    """Botón redondo (play/pausa) dibujado sobre un Canvas."""

    def __init__(
        self, padre, tam, fondo, color, color_hover, color_icono,
        comando, tam_icono=14, nombre="play"
    ):
        super().__init__(
            padre, width=tam, height=tam, bg=fondo,
            highlightthickness=0, bd=0, cursor="hand2"
        )
        self.color = color
        self.color_hover = color_hover
        self.circulo = self.create_oval(
            1, 1, tam - 1, tam - 1, fill=color, outline=""
        )
        self.simbolo = self.create_text(
            tam / 2 + 1, tam / 2, text=glifo(nombre),
            font=(FUENTE_ICO, tam_icono), fill=color_icono
        )
        self.bind("<Button-1>", lambda e: comando())
        self.bind(
            "<Enter>",
            lambda e: self.itemconfig(self.circulo, fill=self.color_hover)
        )
        self.bind(
            "<Leave>",
            lambda e: self.itemconfig(self.circulo, fill=self.color)
        )

    def set_icono(self, nombre):
        self.itemconfig(self.simbolo, text=glifo(nombre))


class Pildora(tk.Canvas):
    """Buscador en forma de píldora, con lupa y texto de ayuda."""

    PLACEHOLDER = "Buscar canción o artista"

    def __init__(self, padre, fondo, relleno=None, ancho=250, alto=36,
                 al_cambiar=None):
        relleno = PANEL if relleno is None else relleno
        super().__init__(
            padre, width=ancho, height=alto, bg=fondo,
            highlightthickness=0, bd=0
        )
        self.relleno = relleno
        self.al_cambiar = al_cambiar
        self.mostrando_ph = True

        self.lupa = self.create_text(
            18, alto // 2, text=glifo("buscar"),
            font=(FUENTE_ICO, 11), fill=TEXTO_SUAVE
        )
        self.entrada = tk.Entry(
            self, bg=relleno, fg=TEXTO_SUAVE, insertbackground=TEXTO,
            relief="flat", bd=0, highlightthickness=0, font=(FUENTE, 10)
        )
        self.entrada.insert(0, self.PLACEHOLDER)
        self.ventana = self.create_window(
            36, alto // 2, window=self.entrada, anchor="w", width=ancho - 54
        )

        self.entrada.bind("<FocusIn>", self._foco_dentro)
        self.entrada.bind("<FocusOut>", self._foco_fuera)
        self.entrada.bind("<KeyRelease>", self._tecla)
        self.bind("<Configure>", self._redibujar)

    def _redibujar(self, e=None):
        w, h = self.winfo_width(), self.winfo_height()
        if w < 40:
            return
        self.delete("fondo")
        r = h // 2
        x2, y2 = w - 1, h - 1
        pts = [
            r, 0, x2 - r, 0, x2, 0, x2, r, x2, y2 - r, x2, y2,
            x2 - r, y2, r, y2, 0, y2, 0, y2 - r, 0, r, 0, 0
        ]
        self.create_polygon(
            pts, smooth=True, fill=self.relleno, outline="", tags="fondo"
        )
        self.tag_lower("fondo")
        self.coords(self.lupa, 18, h // 2)
        self.coords(self.ventana, 36, h // 2)
        self.itemconfig(self.ventana, width=w - 54)

    def _foco_dentro(self, e=None):
        if self.mostrando_ph:
            self.entrada.delete(0, "end")
            self.entrada.config(fg=TEXTO)
            self.mostrando_ph = False

    def _foco_fuera(self, e=None):
        if not self.entrada.get().strip():
            self.vaciar()

    def _tecla(self, e=None):
        if self.al_cambiar and not self.mostrando_ph:
            self.al_cambiar()

    def texto(self):
        if self.mostrando_ph:
            return ""
        return self.entrada.get().strip()

    def vaciar(self):
        self.entrada.delete(0, "end")
        self.entrada.insert(0, self.PLACEHOLDER)
        self.entrada.config(fg=TEXTO_SUAVE)
        self.mostrando_ph = True

    def poner_texto(self, texto):
        self.entrada.delete(0, "end")
        self.entrada.insert(0, texto)
        self.entrada.config(fg=TEXTO)
        self.mostrando_ph = False

class BotonOrden(tk.Canvas):
    """Botón en forma de píldora que abre el menú para ordenar."""

    # (texto del menú, columna, descendente, etiqueta corta)
    OPCIONES = (
        ("Original", None, False, ""),
        ("Título A-Z", "titulo", False, "Título A-Z"),
        ("Título Z-A", "titulo", True, "Título Z-A"),
        ("Artista A-Z", "artista", False, "Artista A-Z"),
        ("Artista Z-A", "artista", True, "Artista Z-A"),
        ("Duración: más corta primero", "duracion", False, "Más cortas"),
        ("Duración: más larga primero", "duracion", True, "Más largas"),
    )

    def __init__(self, padre, fondo, al_elegir, relleno=None, alto=36):
        super().__init__(
            padre, width=110, height=alto, bg=fondo,
            highlightthickness=0, bd=0, cursor="hand2"
        )
        self.relleno = PANEL if relleno is None else relleno
        self.al_elegir = al_elegir
        self.alto = alto
        self.col = None
        self.desc = False
        self.etiqueta = ""
        self.encima = False
        self.fuente = tkfont.Font(family=FUENTE, size=10, weight="bold")

        self.bind("<Enter>", lambda e: self._hover(True))
        self.bind("<Leave>", lambda e: self._hover(False))
        self.bind("<Button-1>", lambda e: self._abrir_menu())
        self._dibujar()

    def _hover(self, estado):
        self.encima = estado
        self._dibujar()

    def set_orden(self, columna, descendente):
        """Se llama cada vez que cambia el orden (también al hacer
        clic en los encabezados de la tabla)."""
        self.col, self.desc = columna, descendente
        self.etiqueta = next(
            (o[3] for o in self.OPCIONES
            if o[1] == columna and o[2] == descendente),
            ""
        )
        self._dibujar()

    def _dibujar(self):
        activo = self.col is not None
        texto = "Ordenar: " + self.etiqueta if activo else "Ordenar"
        w = self.fuente.measure(texto) + 58
        h = self.alto
        self.config(width=w)
        self.delete("all")

        r = h // 2
        x2, y2 = w - 1, h - 1
        pts = [
            r, 0, x2 - r, 0, x2, 0, x2, r, x2, y2 - r, x2, y2,
            x2 - r, y2, r, y2, 0, y2, 0, y2 - r, 0, r, 0, 0
        ]
        self.create_polygon(
            pts, smooth=True, outline="",
            fill=PANEL_HOVER if self.encima else self.relleno
        )
        self.create_text(
            18, h // 2, text=texto, anchor="w", font=self.fuente,
            fill=ACENTO_HOVER if activo else TEXTO
        )
        self.create_text(
            w - 20, h // 2, text=glifo("abajo"),
            font=(FUENTE_ICO, 9), fill=TEXTO_SUAVE
        )

    def _abrir_menu(self):
        menu = tk.Menu(
            self, tearoff=0, bg=PANEL, fg=TEXTO,
            activebackground=ACENTO, activeforeground=color_sobre(ACENTO),
            bd=0, relief="flat", font=(FUENTE, 10)
        )
        for i, (texto, col, desc, _) in enumerate(self.OPCIONES):
            if i in (1, 3, 5):
                menu.add_separator()
            marca = "✓  " if (col == self.col and desc == self.desc) else "     "
            menu.add_command(
                label=marca + texto,
                command=lambda c=col, d=desc: self.al_elegir(c, d)
            )
        try:
            menu.tk_popup(
                self.winfo_rootx(),
                self.winfo_rooty() + self.winfo_height() + 4
            )
        finally:
            menu.grab_release()
# ==============================================================
# TABLA DE CANCIONES
# ==============================================================
def config_columnas(frame):
    """Misma estructura de columnas para el encabezado y las filas."""
    frame.grid_columnconfigure(0, minsize=COL_NUM)
    frame.grid_columnconfigure(1, minsize=COL_MINI)
    frame.grid_columnconfigure(2, weight=1)
    frame.grid_columnconfigure(3, minsize=COL_ARTISTA)
    frame.grid_columnconfigure(4, minsize=COL_CORAZON)
    frame.grid_columnconfigure(5, minsize=COL_DUR)


class FilaCancion:
    """Una fila reutilizable: # | miniatura + título | artista | duración."""

    def __init__(self, padre, al_clic, f_titulo, f_texto,
                 al_corazon=None, es_favorito=None):
        self.indice = None
        self.video_id = None
        self.numero = 0
        self.sonando = False
        self.hover = False
        self.al_clic = al_clic
        self.al_corazon = al_corazon
        self.es_favorito = es_favorito

        self.marco = tk.Frame(padre, bg=FONDO, height=ALTO_FILA)
        self.marco.grid_propagate(False)
        config_columnas(self.marco)
        self.marco.grid_rowconfigure(0, weight=1)

        self.num = tk.Label(self.marco, bg=FONDO, fg=TEXTO_SUAVE, font=(FUENTE, 10))
        self.num.grid(row=0, column=0, sticky="nsew")

        self.miniatura = tk.Label(self.marco, bg=FONDO, bd=0)
        self.miniatura.grid(row=0, column=1)

        self.lbl_titulo = tk.Label(
            self.marco, bg=FONDO, fg=TEXTO, font=f_titulo, anchor="w"
        )
        self.lbl_titulo.grid(row=0, column=2, sticky="ew", padx=(4, 8))

        self.lbl_artista = tk.Label(
            self.marco, bg=FONDO, fg=TEXTO_SUAVE, font=f_texto, anchor="w"
        )
        self.lbl_artista.grid(row=0, column=3, sticky="ew", padx=(0, 8))

        self.dur = tk.Label(
            self.marco, bg=FONDO, fg=TEXTO_SUAVE, font=f_texto, anchor="e"
        )
        self.dur.grid(row=0, column=5, sticky="e", padx=(0, 16))

        # El corazón no está en self.widgets: su clic no reproduce la
        # canción, la marca o desmarca como «Mis favoritos».
        self.corazon = tk.Label(
            self.marco, bg=FONDO, fg=TEXTO_SUAVE,
            font=(FUENTE_ICO, 12), cursor="hand2", width=3
        )
        self.corazon.grid(row=0, column=4, sticky="nsew")
        self.corazon.bind("<Button-1>", self._clic_corazon)
        self.corazon.bind("<Enter>", self._entrar)
        self.corazon.bind("<Leave>", self._salir)

        self.widgets = [
            self.marco, self.num, self.miniatura,
            self.lbl_titulo, self.lbl_artista, self.dur
        ]
        for w in self.widgets:
            w.bind("<Button-1>", self._clic)
            w.bind("<Double-Button-1>", lambda e: "break")
            w.bind("<Enter>", self._entrar)
            w.bind("<Leave>", self._salir)

    def _clic(self, e=None):
        if self.indice is not None:
            self.al_clic(self.indice)

    def _clic_corazon(self, e=None):
        if self.indice is not None and self.al_corazon:
            self.al_corazon(self.indice)
        return "break"

    def _entrar(self, e=None):
        # Solo una fila puede estar resaltada: al entrar en una, la
        # anterior se apaga al instante (sin esperar el aviso de salida).
        previa = getattr(FilaCancion, "_hover_actual", None)
        if previa is not None and previa is not self:
            previa._apagar_hover()
        FilaCancion._hover_actual = self
        self.hover = True
        self._pintar()
        if not getattr(self, "_vigilando", False):
            self._vigilando = True
            self.marco.after(80, self._vigilar_hover)

    def _apagar_hover(self):
        if self.hover:
            self.hover = False
            try:
                self._pintar()
            except tk.TclError:
                pass

    def _vigilar_hover(self):
        # Red de seguridad: si Tk no avisó que el mouse salió de la fila
        # (scroll, salir de la ventana), se quita aquí.
        try:
            if not self.hover or not self.marco.winfo_exists():
                self._vigilando = False
                return
            self._comprobar_salida()
            if self.hover:
                self.marco.after(80, self._vigilar_hover)
            else:
                self._vigilando = False
        except tk.TclError:
            self._vigilando = False

    def _salir(self, e=None):
        # Se comprueba un instante después para evitar parpadeos al pasar
        # de un elemento de la fila a otro.
        self.marco.after(1, self._comprobar_salida)

    def _comprobar_salida(self):
        try:
            if not self.marco.winfo_exists():
                return
            x, y = self.marco.winfo_pointerxy()
            w = self.marco.winfo_containing(x, y)
            dentro = w is not None and str(w).startswith(str(self.marco))
        except Exception:
            dentro = False
        if not dentro:
            self.hover = False
            try:
                self._pintar()
            except tk.TclError:
                pass

    def _pintar(self):
        fondo = PANEL_HOVER if self.hover else FONDO
        for w in self.widgets:
            w.config(bg=fondo)

        if self.sonando:
            self.num.config(
                text=glifo("volumen"), font=(FUENTE_ICO, 11), fg=ACENTO_HOVER
            )
        elif self.hover:
            self.num.config(
                text=glifo("play"), font=(FUENTE_ICO, 11), fg=TEXTO
            )
        else:
            self.num.config(
                text=str(self.numero), font=(FUENTE, 10), fg=TEXTO_SUAVE
            )
        self.lbl_titulo.config(fg=ACENTO_HOVER if self.sonando else TEXTO)

        me_gusta = bool(
            self.es_favorito and self.video_id
            and self.es_favorito(self.video_id)
        )
        self.corazon.config(bg=fondo)
        if me_gusta:
            self.corazon.config(text=glifo("corazon_lleno"), fg=ACENTO_HOVER)
        elif self.hover:
            self.corazon.config(text=glifo("corazon"), fg=TEXTO_SUAVE)
        else:
            self.corazon.config(text="")

    def estado(self, sonando, forzar=False):
        if not forzar and sonando == self.sonando:
            return
        self.sonando = sonando
        self._pintar()

    def actualizar(self, indice, pista, imagen, ancho_titulo, ancho_artista, f_titulo, f_texto):
        titulo, video_id, artista, duracion = pista
        self.indice = indice
        self.video_id = video_id
        self.numero = indice + 1
        self.lbl_titulo.config(text=ajustar(titulo, f_titulo, ancho_titulo))
        self.lbl_artista.config(
            text=ajustar(artista or "Artista desconocido", f_texto, ancho_artista)
        )
        self.dur.config(text=formato_seg(duracion) if duracion else "")
        self.poner_miniatura(imagen)

    def poner_miniatura(self, imagen):
        self.miniatura.config(image=imagen)
        self.miniatura.image = imagen

    def colocar(self, y):
        self.marco.place(x=0, y=y, relwidth=1, height=ALTO_FILA)

    def ocultar(self):
        self.marco.place_forget()
        self.indice = None
        self.video_id = None


class ListaCanciones(tk.Frame):
    """Tabla con encabezado (#, Título, Artista, duración). Solo dibuja
    las filas visibles, así funciona igual con 20 que con 2000 canciones."""

    def __init__(self, padre, al_reproducir, al_ordenar, cache=None,
                al_favorito=None, es_favorito=None):
        super().__init__(padre, bg=FONDO)
        self.al_reproducir = al_reproducir
        self.al_ordenar = al_ordenar
        self.al_favorito = al_favorito
        self.es_favorito = es_favorito
        self.pistas = []
        self.filas = []
        self.offset = 0
        self.sonando_actual = None
        # La caché de miniaturas se comparte entre reconstrucciones
        # (al cambiar de paleta) para no volver a descargarlas.
        self.cache = cache if cache is not None else {}
        self.pedidas = set()
        self._ancho = 0
        self.pool = ThreadPoolExecutor(max_workers=4)

        self.f_titulo = tkfont.Font(family=FUENTE, size=10, weight="bold")
        self.f_texto = tkfont.Font(family=FUENTE, size=10)
        self.vacia = ImageTk.PhotoImage(
            redondear(
                Image.new("RGB", (TAM_MINIATURA, TAM_MINIATURA), PANEL_HOVER), 6
            )
        )

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # --- Encabezado ---
        self.cab = tk.Frame(self, bg=FONDO, height=ALTO_CABECERA_TABLA)
        self.cab.grid(row=0, column=0, sticky="ew")
        self.cab.grid_propagate(False)
        config_columnas(self.cab)
        self.cab.grid_rowconfigure(0, weight=1)

        fuente_cab = (FUENTE, 9, "bold")
        tk.Label(
            self.cab, text="#", bg=FONDO, fg=TEXTO_SUAVE, font=fuente_cab
        ).grid(row=0, column=0, sticky="nsew")

        self.h_titulo = tk.Label(
            self.cab, text="Título", bg=FONDO, fg=TEXTO_SUAVE,
            font=fuente_cab, cursor="hand2"
        )
        self.h_titulo.grid(row=0, column=1, columnspan=2, sticky="w", padx=(4, 0))

        self.h_artista = tk.Label(
            self.cab, text="Artista", bg=FONDO, fg=TEXTO_SUAVE,
            font=fuente_cab, cursor="hand2"
        )
        self.h_artista.grid(row=0, column=3, sticky="w")

        self.h_dur = tk.Label(
            self.cab, text=glifo("reloj"), bg=FONDO, fg=TEXTO_SUAVE,
            font=(FUENTE_ICO, 10), cursor="hand2"
        )
        self.h_dur.grid(row=0, column=5, sticky="e", padx=(0, 16))

        self.h_titulo.bind("<Button-1>", lambda e: self.al_ordenar("titulo"))
        self.h_artista.bind("<Button-1>", lambda e: self.al_ordenar("artista"))
        self.h_dur.bind("<Button-1>", lambda e: self.al_ordenar("duracion"))

        tk.Frame(self, bg=PANEL_HOVER, height=1).grid(
            row=1, column=0, columnspan=2, sticky="ew"
        )

        # --- Cuerpo ---
        self.vista = tk.Frame(self, bg=FONDO)
        self.vista.grid(row=2, column=0, sticky="nsew")
        self.vista.bind("<Configure>", lambda e: self._dibujar())

        self.scroll = ttk.Scrollbar(
            self, orient="vertical",
            style="Musica.Vertical.TScrollbar",
            command=self._comando_scroll
        )
        self.scroll.grid(row=2, column=1, sticky="ns")

    def cerrar(self):
        """Cancela las descargas pendientes (antes de destruir la lista)."""
        try:
            self.pool.shutdown(wait=False, cancel_futures=True)
        except TypeError:
            self.pool.shutdown(wait=False)

    def set_orden(self, columna, descendente):
        flecha = " ▼" if descendente else " ▲"
        self.h_titulo.config(
            text="Título" + (flecha if columna == "titulo" else ""),
            fg=ACENTO_HOVER if columna == "titulo" else TEXTO_SUAVE
        )
        self.h_artista.config(
            text="Artista" + (flecha if columna == "artista" else ""),
            fg=ACENTO_HOVER if columna == "artista" else TEXTO_SUAVE
        )
        self.h_dur.config(
            fg=ACENTO_HOVER if columna == "duracion" else TEXTO_SUAVE
        )

    # --- Scroll ---
    def _alto(self):
        return max(self.vista.winfo_height(), 1)

    def _rueda(self, e):
        try:
            sobre = self.winfo_containing(e.x_root, e.y_root)
        except Exception:
            return
        if sobre is None or not str(sobre).startswith(str(self)):
            return
        if len(self.pistas) * ALTO_FILA <= self._alto():
            return

        if e.num == 4:
            self.offset -= ALTO_FILA
        elif e.num == 5:
            self.offset += ALTO_FILA
        else:
            self.offset -= int(round(e.delta / 120 * ALTO_FILA))
        self._dibujar()

    def _comando_scroll(self, accion, valor, unidad=None):
        total = len(self.pistas) * ALTO_FILA
        if accion == "moveto":
            self.offset = int(float(valor) * total)
        elif accion == "scroll":
            paso = ALTO_FILA if unidad == "units" else self._alto()
            self.offset += int(valor) * paso
        self._dibujar()

    # --- Dibujo ---
    def _asegurar_filas(self, cantidad):
        while len(self.filas) < cantidad:
            self.filas.append(
                FilaCancion(
                    self.vista, self.al_reproducir,
                    self.f_titulo, self.f_texto,
                    self._clic_corazon, self.es_favorito
                )
            )
            nueva = self.filas[-1]
            for w in nueva.widgets + [nueva.corazon]:
                w.bind(
                    "<Button-3>",
                    lambda e, f=nueva: self._menu_derecho(f, e)
                )

    def _menu_derecho(self, fila, e):
        cb = getattr(self, "al_menu_cancion", None)
        if (
            cb and fila.indice is not None
            and 0 <= fila.indice < len(self.pistas)
        ):
            cb(fila.indice, e.x_root, e.y_root)
        return "break"

    def _clic_corazon(self, indice):
        if self.al_favorito and 0 <= indice < len(self.pistas):
            self.al_favorito(self.pistas[indice])

    def repintar_filas(self):
        """Vuelve a dibujar los corazones de las filas visibles."""
        for fila in self.filas:
            if fila.indice is not None:
                fila._pintar()

    def _dibujar(self):
        n = len(self.pistas)
        ancho = max(self.vista.winfo_width(), 1)
        alto = self._alto()
        total = n * ALTO_FILA

        # Si cambia el ancho hay que recortar de nuevo los textos.
        if ancho != self._ancho:
            self._ancho = ancho
            for fila in self.filas:
                fila.indice = None

        ancho_titulo = max(
            ancho - COL_NUM - COL_MINI - COL_ARTISTA - COL_CORAZON - COL_DUR - 28, 60
        )
        ancho_artista = COL_ARTISTA - 16

        self.offset = max(0, min(self.offset, max(0, total - alto)))
        primero = self.offset // ALTO_FILA
        desplaz = self.offset - primero * ALTO_FILA
        self._asegurar_filas(alto // ALTO_FILA + 2)

        for k, fila in enumerate(self.filas):
            idx = primero + k
            y = k * ALTO_FILA - desplaz

            if idx < n and y < alto:
                es_son = idx == self.sonando_actual

                if fila.indice != idx:
                    pista = self.pistas[idx]
                    fila.actualizar(
                        idx, pista, self._miniatura(pista[1]),
                        ancho_titulo, ancho_artista,
                        self.f_titulo, self.f_texto
                    )
                    fila.estado(es_son, forzar=True)
                else:
                    fila.estado(es_son)

                fila.colocar(y)
            else:
                fila.ocultar()

        if total <= alto:
            self.scroll.set(0, 1)
        else:
            self.scroll.set(
                self.offset / total,
                (self.offset + alto) / total
            )

    # --- Miniaturas ---
    def _miniatura(self, video_id):
        if video_id in self.cache:
            return self.cache[video_id]

        if video_id not in self.pedidas:
            self.pedidas.add(video_id)
            try:
                self.pool.submit(self._miniatura_hilo, video_id)
            except RuntimeError:
                pass

        return self.vacia

    def _miniatura_hilo(self, video_id):
        try:
            img, _ = descargar_cuadrada(video_id, TAM_MINIATURA)
            img = redondear(img, 6)
            self.after(
                0, lambda: self._miniatura_lista(video_id, img)
            )
        except Exception:
            pass

    def _miniatura_lista(self, video_id, img):
        foto = ImageTk.PhotoImage(img)
        self.cache[video_id] = foto
        try:
            if not self.winfo_exists():
                return
        except tk.TclError:
            return
        for fila in self.filas:
            if fila.video_id == video_id:
                fila.poner_miniatura(foto)

    # --- Contenido ---
    def cargar(self, pistas, sonando=None):
        """'sonando' = posición (dentro de 'pistas') de la canción que
        suena, si aparece en esta lista."""
        self.pistas = pistas
        self.offset = 0
        self.sonando_actual = sonando

        for fila in self.filas:
            fila.indice = None

        if sonando is not None:
            self.ver(sonando)
        else:
            self._dibujar()

    def marcar_sonando(self, i):
        self.sonando_actual = i
        if i is not None:
            self.ver(i)
        else:
            self._dibujar()

    def ver(self, i):
        alto = self._alto()
        arriba = i * ALTO_FILA
        if arriba < self.offset or arriba + ALTO_FILA > self.offset + alto:
            self.offset = arriba - (alto - ALTO_FILA) // 2
        self._dibujar()


# ==============================================================
# BARRA LATERAL (mis playlists)
# ==============================================================
class BarraLateral(tk.Frame):
    """Barra lateral de Otium.

    En modo normal muestra las playlists. En modo Apariencia reemplaza esa
    zona por el selector de paletas, sin abrir una ventana aparte.
    """
    def __init__(self, padre, al_abrir, al_nueva, al_menu,
                al_apariencia, al_guardar_apariencia):
        super().__init__(padre, bg=PANEL, width=ANCHO_LATERAL)
        self.pack_propagate(False)
        self.al_abrir = al_abrir
        self.al_nueva = al_nueva
        self.al_menu = al_menu
        self.al_apariencia = al_apariencia
        self.al_guardar_apariencia = al_guardar_apariencia
        self.apariencia = False
        self._tema_seleccionado = None

        self.cabecera = etiqueta(
            self, text="Mis playlists", bg=PANEL, fg=TEXTO_SUAVE,
            font=(FUENTE, 10, "bold"), anchor="w"
        )
        self.cabecera.pack(fill="x", padx=20, pady=(22, 10))

        # Zona central: playlists o Apariencia.
        self.zona = tk.Frame(self, bg=PANEL)
        self.zona.pack(fill="both", expand=True)

        # Pie: en modo normal abre Apariencia; en modo Apariencia guarda.
        self.pie = tk.Frame(self, bg=PANEL)
        self.pie.pack(side="bottom", fill="x", padx=10, pady=(0, 14))
        self._construir_pie_normal()

        self._construir_lista()
        self.img_nueva = ImageTk.PhotoImage(icono_nueva(36))

    def _construir_pie_normal(self):
        for w in self.pie.winfo_children():
            w.destroy()
        tk.Frame(self.pie, bg=PANEL_HOVER, height=1).pack(fill="x", pady=(0, 8))

        fila_ap = tk.Frame(self.pie, bg=PANEL, height=44, cursor="hand2")
        fila_ap.pack(fill="x")
        fila_ap.pack_propagate(False)
        ico = tk.Label(
            fila_ap, text=glifo("paleta"), font=(FUENTE_ICO, 14),
            bg=PANEL, fg=TEXTO_SUAVE
        )
        ico.pack(side="left", padx=(14, 14))
        lbl_ap = tk.Label(
            fila_ap, text="Apariencia", bg=PANEL, fg=TEXTO_SUAVE,
            font=(FUENTE, 10), anchor="w"
        )
        lbl_ap.pack(side="left", fill="x", expand=True)

        widgets = [fila_ap, ico, lbl_ap]
        for w in widgets:
            w.bind("<Button-1>", lambda e: self.after_idle(self.al_apariencia))
            w.bind(
                "<Enter>",
                lambda e, ws=widgets: [x.config(bg=PANEL_HOVER) for x in ws]
            )
            w.bind(
                "<Leave>",
                lambda e, ws=widgets: [x.config(bg=PANEL) for x in ws]
            )

    def _construir_pie_apariencia(self):
        for w in self.pie.winfo_children():
            w.destroy()
        tk.Frame(self.pie, bg=PANEL_HOVER, height=1).pack(fill="x", pady=(0, 8))

        boton = tk.Button(
            self.pie, text="Guardar", command=self.al_guardar_apariencia,
            bg=ACENTO, fg=color_sobre(ACENTO),
            activebackground=ACENTO_HOVER,
            activeforeground=color_sobre(ACENTO_HOVER),
            relief="flat", bd=0, cursor="hand2",
            font=(FUENTE, 10, "bold"), pady=7
        )
        boton.pack(fill="x", padx=2)
        boton.bind("<Enter>", lambda e: boton.config(bg=ACENTO_HOVER))
        boton.bind("<Leave>", lambda e: boton.config(bg=ACENTO))

    def _construir_lista(self):
        for w in self.zona.winfo_children():
            w.destroy()

        marco = tk.Frame(self.zona, bg=PANEL)
        marco.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(
            marco, bg=PANEL, highlightthickness=0, bd=0
        )
        # Fila «Nueva playlist» flotante: se muestra solo cuando la lista
        # de playlists es más larga que el panel.
        self.flotante = tk.Frame(marco, bg=PANEL)
        self._flota = None
        self._flot_hecha = False
        self._n_items = 0
        self.canvas.pack(fill="both", expand=True)
        self.interior = tk.Frame(self.canvas, bg=PANEL)
        self.ventana = self.canvas.create_window(
            (0, 0), window=self.interior, anchor="nw"
        )
        self.interior.bind(
            "<Configure>",
            lambda e: self._al_cambiar_interior()
        )
        self.canvas.bind(
            "<Configure>",
            lambda e: self._al_cambiar_canvas(e)
        )
    def _color_personalizado_actual(self):
        return getattr(
            self,
            "ajustes",
            {}
        ).get(
            "acento_personalizado",
            ACENTO
        )

    def abrir_apariencia(self, tema_actual, al_seleccionar):
        self.apariencia = True
        self._tema_seleccionado = tema_actual
        self.cabecera.config(text="Apariencia")
        self._construir_pie_apariencia()

        for w in self.zona.winfo_children():
            w.destroy()

        # Canvas vertical: ahora solo hay Oscuro, pero queda preparado para
        # añadir Minimalista y otras categorías después.
        marco = tk.Frame(self.zona, bg=PANEL)
        marco.pack(fill="both", expand=True)

        canvas = tk.Canvas(
            marco, bg=PANEL, highlightthickness=0, bd=0
        )
        canvas.pack(side="left", fill="both", expand=True)
        barra = ttk.Scrollbar(
            marco, orient="vertical", command=canvas.yview,
            style="Musica.Vertical.TScrollbar"
        )
        barra.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=barra.set)

        interior = tk.Frame(canvas, bg=PANEL)
        ventana = canvas.create_window((0, 0), window=interior, anchor="nw")

        def ajustar_ancho(event):
            canvas.itemconfig(ventana, width=event.width)

        interior.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.bind("<Configure>", ajustar_ancho)

        # ======================================================
        # CATEGORÍA: OSCURO
        # ======================================================
        caja_oscuro = tk.Frame(
            interior, bg=PANEL,
            highlightthickness=1, highlightbackground=PANEL_HOVER
        )
        caja_oscuro.pack(fill="x", padx=8, pady=(4, 6))

        tk.Label(
            caja_oscuro, text="OSCURO", bg=PANEL, fg=TEXTO,
            font=(FUENTE, 9, "bold"), anchor="w"
        ).pack(fill="x", padx=10, pady=(9, 7))

        fila_oscuro = tk.Frame(caja_oscuro, bg=PANEL)
        fila_oscuro.pack(fill="x", padx=7, pady=(0, 10))

        # Las siete paletas oscuras van TODAS en una sola fila.
        nombres_oscuro = (
            "Morado nocturno", "Océano", "Esmeralda", "Atardecer",
            "Rosa neón", "Carmesí", "AMOLED"
        )
        for nombre in nombres_oscuro:
            tema = TEMAS[nombre]
            self._crear_circulo_paleta(
                fila_oscuro, nombre, tema,
                seleccionado=(nombre == self._tema_seleccionado),
                al_clic=lambda n=nombre: al_seleccionar(n)
            ).pack(side="left", padx=1)

        # ======================================================
        # CATEGORÍA: MINIMALISTA
        # ======================================================
        caja_minimalista = tk.Frame(
            interior, bg=PANEL,
            highlightthickness=1, highlightbackground=PANEL_HOVER
        )
        caja_minimalista.pack(fill="x", padx=8, pady=6)

        tk.Label(
            caja_minimalista, text="MINIMALISTA", bg=PANEL, fg=TEXTO,
            font=(FUENTE, 9, "bold"), anchor="w"
        ).pack(fill="x", padx=10, pady=(9, 7))

        fila_minimalista = tk.Frame(caja_minimalista, bg=PANEL)
        fila_minimalista.pack(fill="x", padx=7, pady=(0, 10))

        nombres_minimalista = (
            "Blanco limpio", "Gris elegante", "Beige cálido",
            "Lavanda suave", "Azul hielo", "Verde salvia",
            "Rosa empolvado"
        )
        for nombre in nombres_minimalista:
            tema = TEMAS[nombre]
            self._crear_circulo_paleta(
                fila_minimalista, nombre, tema,
                seleccionado=(nombre == self._tema_seleccionado),
                al_clic=lambda n=nombre: al_seleccionar(n)
            ).pack(side="left", padx=1)

        # ==========================================================
        # Categoria: PERSONALIZADO
        # ==========================================================
        caja_personalizado = tk.Frame(
            interior,bg=PANEL,
            highlightthickness=1, highlightbackground=PANEL_HOVER
        )
        caja_personalizado.pack(fill="x", padx=10, pady=(10, 0))

        tk.Label(
            caja_personalizado, text="PERSONALIZADO", bg=PANEL, fg=TEXTO,
            font=(FUENTE, 9, "bold"), anchor="w"
        ).pack(fill="x", padx=10, pady=(8, 5))


        fila_personalizado = tk.Frame(caja_personalizado, bg=PANEL)
        fila_personalizado.pack(fill="x", padx=8, pady=(0, 10))


        def elegir_color_personalizado():
            inicial = self._color_personalizado_actual()

            _, elegido = colorchooser.askcolor(
                color=inicial,
                title="Elige tu color personalizado"
            )

            if not elegido:
                return

            self.ajustes["acento_personalizado"] = elegido

            al_seleccionar(TEMA_PERSONALIZADO)


        color_personalizado = self.ajustes.get(
            "acento_personalizado",
            ACENTO
        )

        marco_color = tk.Frame(
            fila_personalizado,
            bg=PANEL,
            width=28,
            height=28,
            cursor="hand2"
        )
        marco_color.pack(side="left", padx=4)
        marco_color.pack_propagate(False)

        circulo_color = tk.Canvas(
            marco_color,
            width=24,
            height=24,
            bg=PANEL,
            highlightthickness=0,
            cursor="hand2"
        )
        circulo_color.pack()

        circulo_color.create_oval(
            2, 2, 22, 22,
            fill=color_personalizado,
            outline=PANEL_HOVER,
            width=1
        )

        marco_color.bind(
            "<Button-1>",
            lambda e: elegir_color_personalizado()
        )

        circulo_color.bind(
            "<Button-1>",
            lambda e: elegir_color_personalizado()
        )

        self._tooltip_circulo(
        circulo_color,
        "Elegir color personalizado"
        )

        # Modo del color personalizado: Oscuro o Claro.
        modo_actual = getattr(self, "ajustes", {}).get(
            "modo_personalizado", "oscuro"
        )

        def elegir_modo(valor):
            self.ajustes.setdefault("acento_personalizado", ACENTO)
            self.ajustes["modo_personalizado"] = valor
            al_seleccionar(TEMA_PERSONALIZADO)

        for texto, valor in (("Oscuro", "oscuro"), ("Claro", "claro")):
            activo = (
                valor == modo_actual and tema_actual == TEMA_PERSONALIZADO
            )
            etiqueta = tk.Label(
                fila_personalizado, text=texto,
                bg=ACENTO if activo else PANEL_HOVER,
                fg=color_sobre(ACENTO) if activo else TEXTO,
                font=(FUENTE, 8, "bold"), padx=10, pady=3, cursor="hand2"
            )
            etiqueta.pack(side="left", padx=(8 if valor == "oscuro" else 3, 0))
            etiqueta.bind("<Button-1>", lambda e, v=valor: elegir_modo(v))

        # Espacio final para futuras categorías.
        tk.Frame(interior, bg=PANEL, height=8).pack(fill="x")

        canvas.bind_all("<MouseWheel>", lambda e: self._rueda_apariencia(e, canvas), add="+")
        canvas.bind_all("<Button-4>", lambda e: self._rueda_apariencia(e, canvas), add="+")
        canvas.bind_all("<Button-5>", lambda e: self._rueda_apariencia(e, canvas), add="+")

    def _rueda_apariencia(self, e, canvas):
        try:                                   # ← AÑADIR ESTAS 4 LÍNEAS
            if not canvas.winfo_exists():
                return
        except tk.TclError:
            return
        try:
            sobre = self.winfo_containing(e.x_root, e.y_root)
        except Exception:
            return
        if sobre is None or not str(sobre).startswith(str(self)):
            return
        if e.num == 4:
            canvas.yview_scroll(-2, "units")
        elif e.num == 5:
            canvas.yview_scroll(2, "units")
        else:
            canvas.yview_scroll(int(-e.delta / 120) * 2, "units")

    def _crear_circulo_paleta(self, padre, nombre, tema, seleccionado, al_clic):
        marco = tk.Frame(padre, bg=PANEL, width=24, height=28, cursor="hand2")
        marco.pack_propagate(False)

        circulo = tk.Canvas(
            marco, width=24, height=24, bg=PANEL,
            highlightthickness=0, bd=0, cursor="hand2"
        )
        circulo.pack()

        # Círculo exterior para indicar la paleta seleccionada.
        if seleccionado:
            circulo.create_oval(
                1, 1, 23, 23, fill=tema["FONDO"],
                outline=ACENTO_HOVER, width=2
            )
            circulo.create_oval(
                4, 4, 20, 20, fill=tema["ACENTO"], outline=""
            )
        else:
            circulo.create_oval(
                2, 2, 22, 22, fill=tema["ACENTO"],
                outline=tema["PISTA"], width=1
            )

        # Tooltip sencillo con el nombre de la paleta.
        circulo.bind("<Button-1>", lambda e: al_clic())
        marco.bind("<Button-1>", lambda e: al_clic())
        self._tooltip_circulo(circulo, nombre)
        self._tooltip_circulo(marco, nombre)
        return marco

    def _tooltip_circulo(self, widget, texto):
        def entrar(event):
            if hasattr(self, "_tooltip") and self._tooltip is not None:
                try:
                    self._tooltip.destroy()
                except Exception:
                    pass
            self._tooltip = tk.Toplevel(self)
            self._tooltip.wm_overrideredirect(True)
            self._tooltip.configure(bg="#202027")
            tk.Label(
                self._tooltip, text=texto, bg="#202027", fg="#ffffff",
                font=(FUENTE, 8), padx=6, pady=3
            ).pack()
            self._tooltip.geometry(
                f"+{event.x_root + 8}+{event.y_root + 8}"
            )

        def salir(event):
            if hasattr(self, "_tooltip") and self._tooltip is not None:
                try:
                    self._tooltip.destroy()
                except Exception:
                    pass
                self._tooltip = None

        widget.bind("<Enter>", entrar)
        widget.bind("<Leave>", salir)

    def cerrar_apariencia(self):
        self.apariencia = False
        if hasattr(self, "_tooltip") and self._tooltip is not None:
            try:
                self._tooltip.destroy()
            except Exception:
                pass
            self._tooltip = None
        self.cabecera.config(text="Mis playlists")
        self._construir_pie_normal()
        self._construir_lista()

    def _rueda(self, e):
        try:
            sobre = self.winfo_containing(e.x_root, e.y_root)
        except Exception:
            return
        if sobre is None or not str(sobre).startswith(str(self)):
            return
        if self.apariencia:
            return
        if self.interior.winfo_height() <= self.canvas.winfo_height():
            return
        if e.num == 4:
            self.canvas.yview_scroll(-2, "units")
        elif e.num == 5:
            self.canvas.yview_scroll(2, "units")
        else:
            self.canvas.yview_scroll(int(-e.delta / 120) * 2, "units")

    def refrescar(self, playlists, actual, sonando):
        if self.apariencia:
            return
        for w in self.interior.winfo_children():
            w.destroy()

        for p in playlists:
            self._crear_item(p, p is actual, p is sonando)
        self._n_items = len(playlists)
        self._crear_nueva()
        self._flota = None
        self.canvas.yview_moveto(0)
        self.after_idle(self._ajustar_nueva)

    def _crear_item(self, playlist, seleccionada, sonando):
        bg = PANEL_HOVER if seleccionada else PANEL
        fila = tk.Frame(self.interior, bg=bg, height=52, cursor="hand2")
        fila.pack(fill="x", padx=10, pady=1)
        fila.pack_propagate(False)

        imagen = ImageTk.PhotoImage(
            icono_nota(
                36, color_playlist(playlist), 8, 0.5,
                simbolo="♥" if playlist.get("virtual") else "♪"
            )
        )
        lbl_img = tk.Label(fila, image=imagen, bg=bg, bd=0)
        lbl_img.image = imagen
        lbl_img.pack(side="left", padx=(8, 10), pady=8)

        if sonando:
            color_texto = ACENTO_HOVER
        else:
            color_texto = TEXTO if seleccionada else TEXTO_SUAVE
        lbl = tk.Label(
            fila, text=cortar(playlist["nombre"], 20), bg=bg, fg=color_texto,
            font=(FUENTE, 10, "bold" if seleccionada else "normal"),
            anchor="w"
        )
        lbl.pack(side="left", fill="x", expand=True)

        widgets = [fila, lbl_img, lbl]
        for w in widgets:
            w.bind(
                "<Button-1>",
                lambda e, p=playlist: self.after_idle(lambda: self.al_abrir(p))
            )
            w.bind(
                "<Button-3>",
                lambda e, p=playlist: self.al_menu(p, e.x_root, e.y_root)
            )
            if not seleccionada:
                w.bind(
                    "<Enter>",
                    lambda e, ws=widgets: [x.config(bg=PANEL_HOVER) for x in ws]
                )
                w.bind(
                    "<Leave>",
                    lambda e, ws=widgets: [x.config(bg=PANEL) for x in ws]
                )

    def _al_cambiar_interior(self):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _al_cambiar_canvas(self, e):
        self.canvas.itemconfig(self.ventana, width=e.width)
        self._ajustar_nueva()

    def _ajustar_nueva(self):
        """Si hay más playlists que espacio, «Nueva playlist» queda fija
        abajo (flotando); si caben, va justo después de la última."""
        if self.apariencia or not hasattr(self, "flotante"):
            return
        try:
            disponible = self.canvas.master.winfo_height()
            if disponible <= 1:
                return
            desborda = (self._n_items + 1) * 54 + 4 > disponible
            if desborda == self._flota:
                return
            self._flota = desborda
            if desborda:
                if not self._flot_hecha:
                    tk.Frame(
                        self.flotante, bg=PANEL_HOVER, height=1
                    ).pack(fill="x", padx=10, pady=(0, 4))
                    self._crear_nueva(self.flotante)
                    self.flotante.pack_propagate(True)
                    self._flot_hecha = True
                self._fila_inline.pack_forget()
                self.flotante.pack(
                    side="bottom", fill="x", pady=(0, 6),
                    before=self.canvas
                )
            else:
                self.flotante.pack_forget()
                self._fila_inline.pack(fill="x", padx=10, pady=1)
        except tk.TclError:
            pass

    def _crear_nueva(self, padre=None):
        fila = tk.Frame(
            padre or self.interior, bg=PANEL, height=52, cursor="hand2"
        )
        if padre is None:
            self._fila_inline = fila
        fila.pack(fill="x", padx=10, pady=1)
        fila.pack_propagate(False)

        lbl_img = tk.Label(fila, image=self.img_nueva, bg=PANEL, bd=0)
        lbl_img.pack(side="left", padx=(8, 10), pady=8)
        lbl = tk.Label(
            fila, text="Nueva playlist", bg=PANEL, fg=TEXTO_SUAVE,
            font=(FUENTE, 10), anchor="w"
        )
        lbl.pack(side="left", fill="x", expand=True)

        widgets = [fila, lbl_img, lbl]
        for w in widgets:
            w.bind("<Button-1>", lambda e: self.after_idle(self.al_nueva))
            w.bind(
                "<Enter>",
                lambda e, ws=widgets: [x.config(bg=PANEL_HOVER) for x in ws]
            )
            w.bind(
                "<Leave>",
                lambda e, ws=widgets: [x.config(bg=PANEL) for x in ws]
            )


def rect_redondeado(lienzo, x1, y1, x2, y2, r, **opciones):
    """Rectángulo con esquinas redondeadas dibujado en un Canvas."""
    p = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
         x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
         x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return lienzo.create_polygon(p, smooth=True, **opciones)


class Interruptor(tk.Canvas):
    """Interruptor encendido/apagado, redondo."""

    def __init__(self, padre, valor=False, al_cambiar=None, fondo=None):
        super().__init__(
            padre, width=40, height=22, bd=0, highlightthickness=0,
            bg=PANEL if fondo is None else fondo, cursor="hand2"
        )
        self.valor = bool(valor)
        self.al_cambiar = al_cambiar
        self.bind("<Button-1>", self._clic)
        self._dibujar()

    def _clic(self, e=None):
        self.valor = not self.valor
        self._dibujar()
        if self.al_cambiar:
            self.al_cambiar(self.valor)

    def _dibujar(self):
        self.delete("all")
        color = ACENTO_BOTON if self.valor else PISTA
        self.create_oval(1, 1, 21, 21, fill=color, outline="")
        self.create_oval(19, 1, 39, 21, fill=color, outline="")
        self.create_rectangle(11, 1, 29, 21, fill=color, outline="")
        x = 29 if self.valor else 11
        self.create_oval(x - 8, 3, x + 8, 19, fill="#ffffff", outline="")


class PantallaApariencia(tk.Frame):
    """
    Pantalla de Apariencia de Otium.

    ETAPA 1
    ------------------------------------------------------------
    - Paletas prediseñadas.
    - Personalizado.
    - Color principal.
    - Intensidad del color.
    - Color de botones.
    - Modo oscuro / claro.
    - Vista previa de paletas.
    - Scroll vertical.
    - Restablecer.
    - Guardar.

    Las opciones de fondo, transparencia, difuminado,
    portada dinámica, efecto vidrio, etc. se incorporarán
    posteriormente.
    """

    NOMBRES_OSCURAS = (
        "Morado nocturno",
        "Océano",
        "Esmeralda",
        "Atardecer",
        "Rosa neón",
        "Carmesí",
        "AMOLED",
    )

    NOMBRES_CLARAS = (
        "Blanco limpio",
        "Gris elegante",
        "Beige cálido",
        "Lavanda suave",
        "Azul hielo",
        "Verde salvia",
        "Rosa empolvado",
    )

    SECCIONES = (
        ("paletas", "Paletas", "◐"),
        ("fondos", "Fondos", "▣"),
        ("efectos", "Efectos", "✦"),
        ("reproductor", "Reproductor", "▶"),
        ("dinamico", "Dinámico", "♪"),
    )

    NOMBRES_FONDO = {
        "ninguno": "Sin fondo",
        "color": "Color",
        "portada_cancion": "Portada de la canción",
        "portada_playlist": "Portada de la playlist",
        "imagen": "Imagen personalizada",
    }

    PREVIA_W = 220
    PREVIA_H = 150
    ANCHO_PREVIA = 246
    ANCHO_MENU = 150
    MIN_ZONA_PREVIA = 820

    ANCHO_TARJETA = 154
    ALTO_TARJETA = 112

    def __init__(self, padre, app):
        super().__init__(
            padre,
            bg=FONDO
        )

        self.app = app

        self._scroll_inicial = getattr(
            app,
            "_scroll_apariencia",
            0.0
        )

        self._listo = False
        self._grupos = []
        self._columnas = 4

        self._construir()



    def _panel_fondo_reproductor(self, padre=None):
        """Opciones de fondo del reproductor."""
        a = self.app.ajustes
        caja = self._caja(
            "Fondo",
            "Imagen y portadas: cabecera y barras. Color: adapta toda la paleta."
        )

        tipo_radio = a.get("fondo_tipo", "ninguno")
        if tipo_radio == "ambiente":
            tipo_radio = "ninguno"
        self._var_fondo = tk.StringVar(value=tipo_radio)
        opciones = [
            ("Ninguno", "ninguno"),
            ("Color (toda la paleta)", "color"),
            ("Portada de la canción", "portada_cancion"),
            ("Portada de la playlist", "portada_playlist"),
        ]
        for texto, valor in opciones:
            fila = tk.Frame(caja, bg=PANEL)
            fila.pack(fill="x", padx=14, pady=1)
            tk.Radiobutton(
                fila, text=texto, value=valor, variable=self._var_fondo,
                bg=PANEL, fg=TEXTO, selectcolor=PANEL_HOVER,
                activebackground=PANEL, activeforeground=TEXTO,
                font=(FUENTE, 9), anchor="w", highlightthickness=0, bd=0,
                cursor="hand2",
                command=lambda v=valor: self._cambiar_fondo_tipo(v)
            ).pack(side="left", fill="x", expand=True)

        # --- Color ---
        fila_color = tk.Frame(caja, bg=PANEL)
        fila_color.pack(fill="x", padx=14, pady=(10, 4))
        tk.Label(
            fila_color, text="Color de fondo", bg=PANEL, fg=TEXTO_SUAVE,
            font=(FUENTE, 9)
        ).pack(side="left")
        muestra = tk.Label(
            fila_color, bg=a.get("fondo_color") or FONDO, width=4,
            height=1, relief="flat", cursor="hand2",
            highlightthickness=1, highlightbackground=PANEL_HOVER
        )
        muestra.pack(side="right")
        self._muestra_color = muestra
        muestra.bind("<Button-1>", lambda e: self._elegir_fondo_color(muestra))

        # --- Imagen personalizada ---
        activa = a.get("fondo_tipo") == "imagen"
        ruta = a.get("fondo_imagen", "")
        titulo = tk.Frame(caja, bg=PANEL)
        titulo.pack(fill="x", padx=14, pady=(12, 0))
        tk.Label(
            titulo, text="Imagen personalizada", bg=PANEL,
            fg=ACENTO_HOVER if activa else TEXTO,
            font=(FUENTE, 9, "bold"), anchor="w"
        ).pack(side="left")
        if activa:
            tk.Label(
                titulo, text="  ·  en uso", bg=PANEL, fg=TEXTO_SUAVE,
                font=(FUENTE, 8)
            ).pack(side="left")
        elif ruta:
            usar = tk.Label(
                titulo, text="Usar esta imagen", bg=PANEL, fg=ACENTO_HOVER,
                font=(FUENTE, 8, "underline"), cursor="hand2"
            )
            usar.pack(side="right")
            usar.bind(
                "<Button-1>",
                lambda e: (
                    self.app.cambiar_personalizado(fondo_tipo="imagen"),
                    self._refrescar_ajustes_img()
                )
            )
        fila_img = tk.Frame(caja, bg=PANEL)
        fila_img.pack(fill="x", padx=14, pady=(6, 4))
        tk.Button(
            fila_img, text="Elegir imagen...", command=self._elegir_imagen_fondo,
            bg=PANEL_HOVER, fg=TEXTO, activebackground=ACENTO,
            activeforeground=color_sobre(ACENTO), relief="flat", bd=0,
            font=(FUENTE, 9), cursor="hand2", padx=10, pady=4
        ).pack(side="left")
        tk.Label(
            fila_img, text=os.path.basename(ruta) if ruta else "Ninguna",
            bg=PANEL, fg=TEXTO_SUAVE, font=(FUENTE, 8), anchor="w"
        ).pack(side="left", padx=10)

        # --- Barras de la imagen: se despliegan con Imagen o Portadas ---
        self._espacio_fondo = tk.Frame(caja, bg=PANEL, height=6)
        self._espacio_fondo.pack()
        self._ajustes_img = tk.Frame(caja, bg=PANEL)
        self._escala_fondo(
            self._ajustes_img, "Nitidez", "fondo_difuminado",
            "Borrosa", "Nítida", 0, invertir=True
        )
        self._escala_fondo(
            self._ajustes_img, "Transparencia", "fondo_transparencia",
            "Transparente", "Opaco", FONDO_TRANSP_DEF
        )
        self._refrescar_ajustes_img()

    def _refrescar_ajustes_img(self):
        """Despliega las barras solo si el fondo es una imagen o una portada."""
        try:
            marco = self._ajustes_img
            if not marco.winfo_exists():
                return
            if (self.app.ajustes.get("fondo_tipo") in TIPOS_LIENZO
                    and self.app.ajustes.get("fondo_tipo") != "ambiente"):
                marco.pack(fill="x", before=self._espacio_fondo)
            else:
                marco.pack_forget()
        except (AttributeError, tk.TclError):
            pass

    def _panel_efectos_reproductor(self, padre=None):
        """Efectos visuales."""
        a = self.app.ajustes

        caja = self._caja("Efecto vidrio", "Se aplica sobre el fondo elegido.")
        self._crear_interruptor(
            caja, "Efecto vidrio",
            "Suaviza y aclara un poco el fondo",
            "efecto_vidrio"
        )
        tk.Frame(caja, bg=PANEL, height=6).pack()

        caja = self._caja(
            "Luz y movimiento",
            "Detalles que dan vida al reproductor."
        )
        self._fila_interruptor(
            caja, "Resplandor de portada",
            "Un halo con los colores de la portada alrededor de la carátula.",
            a.get("resplandor_portada", False),
            lambda v: self._cambiar_efecto("resplandor_portada", v)
        )
        if a.get("resplandor_portada"):
            self._escala_efecto(
                caja, "Intensidad", "resplandor_intensidad",
                "Suave", "Fuerte", 60
            )
        self._fila_interruptor(
            caja, "Brillo ambiental",
            "Una luz suave del color de la canción sube desde los bordes. "
            "Se ve sin fondo, con imagen o con portada (no con fondo de color).",
            a.get("brillo_ambiental", False),
            lambda v: self._cambiar_efecto("brillo_ambiental", v)
        )
        if a.get("brillo_ambiental"):
            self._escala_efecto(
                caja, "Intensidad", "brillo_intensidad",
                "Suave", "Fuerte", 50
            )
        self._fila_interruptor(
            caja, "Animación suave del fondo",
            "Cuando el fondo cambia, se funde con el anterior en vez de saltar.",
            a.get("fondo_animacion", False),
            lambda v: self._cambiar_efecto("fondo_animacion", v)
        )
        tk.Frame(caja, bg=PANEL, height=6).pack()

    # ==========================================================
    # SECCIÓN REPRODUCTOR
    # ==========================================================
    def _panel_reproductor(self):
        a = self.app.ajustes

        caja = self._caja(
            "Tamaño de la portada",
            "Afecta a la portada grande de la playlist y a la carátula "
            "de la barra inferior."
        )
        self._fila_radios(
            caja, a.get("portada_tam", "mediana"),
            (
                ("Pequeña", "pequena", ""),
                ("Mediana", "mediana", "la de siempre"),
                ("Grande", "grande", ""),
            ),
            lambda c: self._cambiar_reproductor("portada_tam", c)
        )
        tk.Frame(caja, bg=PANEL, height=8).pack()

        caja = self._caja(
            "Estilo de los controles",
            "Cómo se ven los botones de la barra inferior."
        )
        self._fila_radios(
            caja, a.get("controles_estilo", "clasicos"),
            (
                ("Minimalistas", "minimalistas", "iconos finos, sin círculo"),
                ("Clásicos", "clasicos", "los de siempre"),
                ("Grandes", "grandes", "botones más grandes"),
            ),
            lambda c: self._cambiar_reproductor("controles_estilo", c)
        )
        tk.Frame(caja, bg=PANEL, height=8).pack()

        caja = self._caja(
            "Información de la canción",
            "Lo que se muestra a la izquierda de la barra inferior."
        )
        self._fila_interruptor(
            caja, "Mostrar nombres y portada en los controles",
            "Si lo apagas, la barra inferior solo muestra los controles.",
            a.get("info_en_barra", True),
            lambda v: self._cambiar_reproductor("info_en_barra", v)
        )
        if a.get("info_en_barra", True):
            self._fila_radios(
                caja, a.get("info_barra", "titulo_artista"),
                (
                    ("Título + artista", "titulo_artista", ""),
                    ("Título + artista + álbum", "titulo_artista_album", ""),
                ),
                lambda c: self._cambiar_reproductor("info_barra", c)
            )
            if a.get("info_barra") == "titulo_artista_album":
                tk.Label(
                    caja,
                    text="El álbum lo da YouTube cuando lo conoce; si no, "
                         "se muestra el nombre de la playlist.",
                    bg=PANEL, fg=TEXTO_SUAVE, font=(FUENTE, 8), anchor="w"
                ).pack(fill="x", padx=16, pady=(4, 6))
        tk.Frame(caja, bg=PANEL, height=6).pack()

    def _cambiar_reproductor(self, clave, valor):
        self.app.cambiar_reproductor(clave, valor)
        self._tras_elegir_fondo()

    def _cambiar_efecto(self, clave, valor):
        self.app.cambiar_efecto(clave, valor)
        self._tras_elegir_fondo()

    def _escala_efecto(self, caja, titulo, clave, izq, der, defecto):
        """Barra de intensidad de un efecto."""
        tk.Label(
            caja, text=titulo, bg=PANEL, fg=TEXTO,
            font=(FUENTE, 9, "bold"), anchor="w"
        ).pack(fill="x", padx=14, pady=(2, 2))
        fila = tk.Frame(caja, bg=PANEL)
        fila.pack(fill="x", padx=14, pady=(0, 6))
        tk.Label(
            fila, text=izq, bg=PANEL, fg=TEXTO_SUAVE, font=(FUENTE, 8)
        ).pack(side="left")
        valor = int(self.app.ajustes.get(clave, defecto))
        lbl = tk.Label(
            fila, text=f"{valor}%", bg=PANEL, fg=TEXTO_SUAVE,
            font=(FUENTE, 8), width=5, anchor="e"
        )
        lbl.pack(side="right")
        tk.Label(
            fila, text=der, bg=PANEL, fg=TEXTO_SUAVE, font=(FUENTE, 8)
        ).pack(side="right")

        def mover(v):
            v = int(v)
            lbl.config(text=f"{v}%")
            self.app.programar_efecto(clave, v)

        Slider(
            fila, 0, 100, valor, ancho=160, fondo=PANEL, al_mover=mover
        ).pack(side="left", fill="x", expand=True, padx=8)

    def _fila_interruptor(self, caja, titulo, descripcion, valor,
                          al_cambiar):
        fila = tk.Frame(caja, bg=PANEL)
        fila.pack(fill="x", padx=14, pady=7)

        textos = tk.Frame(fila, bg=PANEL)
        textos.pack(side="left", fill="x", expand=True)

        tk.Label(
            textos, text=titulo, bg=PANEL, fg=TEXTO,
            font=(FUENTE, 9, "bold"), anchor="w"
        ).pack(fill="x")

        tk.Label(
            textos, text=descripcion, bg=PANEL, fg=TEXTO_SUAVE,
            font=(FUENTE, 8), anchor="w", justify="left", wraplength=420
        ).pack(fill="x", pady=(2, 0))

        Interruptor(
            fila, bool(valor), lambda v: al_cambiar(bool(v))
        ).pack(side="right", padx=(10, 0))

    def _fila_radios(self, caja, valor, opciones, al_elegir):
        var = tk.StringVar(value=valor)
        self.__dict__.setdefault("_vars_radio", []).append(var)

        for texto, clave, detalle in opciones:
            fila = tk.Frame(caja, bg=PANEL)
            fila.pack(fill="x", padx=14, pady=1)
            tk.Radiobutton(
                fila, text=texto, value=clave, variable=var,
                bg=PANEL, fg=TEXTO, selectcolor=PANEL_HOVER,
                activebackground=PANEL, activeforeground=TEXTO,
                font=(FUENTE, 9), anchor="w", highlightthickness=0, bd=0,
                cursor="hand2", command=lambda c=clave: al_elegir(c)
            ).pack(side="left")
            if detalle:
                tk.Label(
                    fila, text=detalle, bg=PANEL, fg=TEXTO_SUAVE,
                    font=(FUENTE, 8)
                ).pack(side="left", padx=(6, 0))

    def _barras_fondo(self, caja):
        """Nitidez y Transparencia, dentro de la caja que las pide."""
        self._escala_fondo(
            caja, "Nitidez", "fondo_difuminado",
            "Borrosa", "Nítida", 0, invertir=True
        )
        self._escala_fondo(
            caja, "Transparencia", "fondo_transparencia",
            "Transparente", "Opaco", FONDO_TRANSP_DEF
        )

    def _panel_dinamico(self):
        """Todo lo que reacciona a la canción que suena."""
        a = self.app.ajustes
        app = self.app

        # --- Modo ambiente ---
        caja = self._caja(
            "Modo ambiente",
            "El reproductor crea una atmósfera con la canción: colores y "
            "fondo siguen su portada."
        )
        self._fila_interruptor(
            caja, "Activar modo ambiente",
            "Cada canción cambia los colores y el fondo. Al apagarlo "
            "vuelve lo que tenías.",
            a.get("modo_ambiente", False),
            lambda v: (
                app.cambiar_dinamico(modo_ambiente=v),
                self._tras_elegir_fondo()
            )
        )
        if a.get("modo_ambiente"):
            self._barras_fondo(caja)
        tk.Frame(caja, bg=PANEL, height=6).pack()

        # --- Color de la interfaz ---
        caja = self._caja(
            "Color de la interfaz",
            "De dónde salen los colores de Otium."
        )
        self._fila_radios(
            caja, a.get("color_interfaz", "personalizado"),
            (
                ("Color personalizado", "personalizado", "el de tu paleta"),
                ("Color de la portada", "portada",
                 "toda la paleta sigue la portada"),
                ("Automático", "automatico",
                 "solo el acento sigue la portada"),
            ),
            lambda c: (
                app.cambiar_dinamico(color_interfaz=c),
                self._tras_elegir_fondo()
            )
        )
        tk.Label(
            caja,
            text="Los colores cambian cuando carga la portada de la "
                 "canción que suena.",
            bg=PANEL, fg=TEXTO_SUAVE, font=(FUENTE, 8), anchor="w"
        ).pack(fill="x", padx=16, pady=(6, 10))

        # --- Fondo dinámico ---
        caja = self._caja(
            "Fondo dinámico",
            "El fondo cambia con cada canción."
        )
        self._fila_interruptor(
            caja, "Cambiar fondo al cambiar de canción",
            "Se activa el fondo solo y puedes elegir de dónde sale.",
            a.get("fondo_dinamico", False),
            lambda v: (
                app.cambiar_dinamico(fondo_dinamico=v),
                self._tras_elegir_fondo()
            )
        )
        self._fila_radios(
            caja, a.get("fondo_dinamico_origen", "portada"),
            (
                ("Portada de la canción", "portada", ""),
                ("Fondo aleatorio", "aleatorio",
                 "de los de Otium y los tuyos"),
                ("Colores de la portada", "colores",
                 "degradado con sus colores"),
            ),
            lambda c: (
                app.cambiar_dinamico(origen=c),
                self._tras_elegir_fondo()
            )
        )
        if a.get("fondo_dinamico"):
            self._barras_fondo(caja)
        tk.Frame(caja, bg=PANEL, height=8).pack()


    def _escala_fondo(self, caja, titulo, clave, izq, der, defecto,
                      invertir=False):
        """Deslizador que guarda su valor al moverlo y pinta al hacer una
        pausa (sin reconstruir la pantalla). Con invertir=True la barra
        muestra 100 - valor guardado (Nitidez = 100 - difuminado)."""
        tk.Label(
            caja, text=titulo, bg=PANEL, fg=TEXTO,
            font=(FUENTE, 9, "bold"), anchor="w"
        ).pack(fill="x", padx=14, pady=(8, 2))
        fila = tk.Frame(caja, bg=PANEL)
        fila.pack(fill="x", padx=14, pady=(0, 6))
        tk.Label(
            fila, text=izq, bg=PANEL, fg=TEXTO_SUAVE, font=(FUENTE, 8)
        ).pack(side="left")
        crudo = int(self.app.ajustes.get(clave, defecto))
        valor = 100 - crudo if invertir else crudo
        lbl = tk.Label(
            fila, text=f"{valor}%", bg=PANEL, fg=TEXTO_SUAVE,
            font=(FUENTE, 8), width=5, anchor="e"
        )
        lbl.pack(side="right")
        tk.Label(
            fila, text=der, bg=PANEL, fg=TEXTO_SUAVE, font=(FUENTE, 8)
        ).pack(side="right")

        def mover(v):
            v = int(v)
            lbl.config(text=f"{v}%")
            self.app.programar_fondo(**{clave: 100 - v if invertir else v})

        Slider(
            fila, 0, 100, valor, ancho=160, fondo=PANEL, al_mover=mover
        ).pack(side="left", fill="x", expand=True, padx=8)

    def _crear_interruptor(
            self,
            padre,
            titulo,
            descripcion,
            clave
        ):
        fila = tk.Frame(
            padre,
            bg=PANEL
        )
        fila.pack(
            fill="x",
            padx=14,
            pady=7
        )

        textos = tk.Frame(
            fila,
            bg=PANEL
        )
        textos.pack(
            side="left",
            fill="x",
            expand=True
        )

        tk.Label(
            textos,
            text=titulo,
            bg=PANEL,
            fg=TEXTO,
            font=(FUENTE, 9, "bold"),
            anchor="w"
        ).pack(
            fill="x"
        )

        tk.Label(
            textos,
            text=descripcion,
            bg=PANEL,
            fg=TEXTO_SUAVE,
            font=(FUENTE, 8),
            anchor="w"
        ).pack(
            fill="x",
            pady=(2, 0)
        )

        valor = bool(
            self.app.ajustes.get(
                clave,
                False
            )
        )

        interruptor = Interruptor(
            fila,
            valor,
            lambda v, k=clave:
                self.app.cambiar_personalizado(
                    **{k: bool(v)}
                )
        )

        interruptor.pack(
            side="right",
            padx=(10, 0)
        )

        return interruptor


    def _cambiar_fondo_tipo(self, tipo):
        if tipo == "color" and not self.app.ajustes.get("fondo_color_elegido"):
            self._elegir_fondo_color(self._muestra_color)
            return
        if tipo == "imagen" and not self.app.ajustes.get("fondo_imagen"):
            self._elegir_imagen_fondo()
            return
        self.app.cambiar_personalizado(fondo_tipo=tipo)
        self._refrescar_ajustes_img()

    def _restaurar_radio_fondo(self):
        try:
            self._var_fondo.set(
                self.app.ajustes.get("fondo_tipo", "ninguno")
            )
        except Exception:
            pass

    def _elegir_fondo_color(self, muestra):
        actual = self.app.ajustes.get("fondo_color") or FONDO
        try:
            elegido = colorchooser.askcolor(
                color=actual, title="Color de fondo",
                parent=self.winfo_toplevel()
            )
        except tk.TclError:
            elegido = colorchooser.askcolor(title="Color de fondo")
        if not elegido or not elegido[1]:
            self._restaurar_radio_fondo()
            return
        muestra.config(bg=elegido[1])
        self._var_fondo.set("color")
        self.app.ajustes["fondo_color_elegido"] = True
        self.app.cambiar_personalizado(
            fondo_tipo="color", fondo_color=elegido[1]
        )

    def _elegir_imagen_fondo(self):
        ruta = filedialog.askopenfilename(
            title="Elegir imagen de fondo",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.webp *.bmp")]
        )
        if not ruta:
            self._restaurar_radio_fondo()
            return
        self._var_fondo.set("imagen")
        # Se reconstruye la pantalla para mostrar el nombre del archivo.
        self.app.cambiar_personalizado(fondo_tipo="imagen", fondo_imagen=ruta)
        self.app._mostrar_pantalla_apariencia()


    # ==========================================================
    # CONSTRUCCIÓN PRINCIPAL
    # ==========================================================

    def _construir(self):

        app = self.app

        # ------------------------------------------------------
        # CABECERA
        # ------------------------------------------------------

        cab = tk.Frame(
            self,
            bg=FONDO
        )

        cab.pack(
            fill="x",
            padx=(24, 30),
            pady=(20, 0)
        )

        BotonIcono(
            cab,
            "atras",
            app.cancelar_apariencia,
            tam=14,
            fondo=FONDO
        ).pack(
            side="left",
            padx=(0, 8)
        )

        tk.Label(
            cab,
            text="Apariencia",
            bg=FONDO,
            fg=TEXTO,
            font=(FUENTE, 20, "bold")
        ).pack(
            side="left"
        )

        tk.Label(
            cab,
            text="Personaliza Otium a tu manera",
            bg=FONDO,
            fg=TEXTO_SUAVE,
            font=(FUENTE, 9)
        ).pack(
            side="right",
            pady=(5, 0)
        )

        tk.Label(
            self,
            text="Elige una paleta o crea tu propia apariencia.",
            bg=FONDO,
            fg=TEXTO_SUAVE,
            font=(FUENTE, 10),
            anchor="w"
        ).pack(
            fill="x",
            padx=30,
            pady=(3, 12)
        )

        # (el menú de secciones está en la columna izquierda, más abajo)
        self._tabs = {}

        # ------------------------------------------------------
        # PIE FIJO
        # ------------------------------------------------------

        pie = tk.Frame(
            self,
            bg=PANEL
        )

        pie.pack(
            side="bottom",
            fill="x"
        )

        tk.Frame(
            pie,
            bg=PANEL_HOVER,
            height=1
        ).pack(
            fill="x"
        )

        fila_botones = tk.Frame(
            pie,
            bg=PANEL
        )

        fila_botones.pack(
            fill="x",
            padx=28,
            pady=12
        )

        app.boton(
            fila_botones,
            "Guardar",
            app.guardar_apariencia,
            ancho=12,
            acento=True
        ).pack(
            side="right"
        )

        app.boton(
            fila_botones,
            "Cancelar",
            app.cancelar_apariencia,
            ancho=12
        ).pack(
            side="right",
            padx=(0, 10)
        )

        app.boton(
            fila_botones,
            "Restablecer",
            app.restablecer_apariencia,
            ancho=12
        ).pack(
            side="right",
            padx=(0, 10)
        )

        # ------------------------------------------------------
        # ÁREA CON SCROLL
        # ------------------------------------------------------

        zona = tk.Frame(
            self,
            bg=FONDO
        )

        zona.pack(
            fill="both",
            expand=True,
            padx=(30, 10)
        )

        menu = tk.Frame(
            zona,
            bg=FONDO,
            width=self.ANCHO_MENU
        )

        menu.pack(
            side="left",
            fill="y",
            padx=(0, 14)
        )

        menu.pack_propagate(False)

        self._crear_menu(menu)

        self._previa = tk.Frame(
            zona,
            bg=FONDO,
            width=self.ANCHO_PREVIA
        )

        self._previa.pack(
            side="right",
            fill="y",
            padx=(14, 8)
        )

        self._previa.pack_propagate(False)

        self._crear_previa(self._previa)

        marco = tk.Frame(
            zona,
            bg=FONDO
        )

        marco.pack(
            side="left",
            fill="both",
            expand=True
        )

        self._marco_zona = marco
        self._previa_visible = True
        zona.bind("<Configure>", self._ajustar_previa)

        self.canvas = tk.Canvas(
            marco,
            bg=FONDO,
            highlightthickness=0,
            bd=0
        )

        barra = ttk.Scrollbar(
            marco,
            orient="vertical",
            command=self.canvas.yview,
            style="Musica.Vertical.TScrollbar"
        )

        barra.pack(
            side="right",
            fill="y"
        )

        self.canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.canvas.configure(
            yscrollcommand=lambda a, b: (
                barra.set(a, b),
                self._anotar_scroll(a)
            )
        )

        self.cuerpo = tk.Frame(
            self.canvas,
            bg=FONDO
        )

        self._ventana = self.canvas.create_window(
            (0, 0),
            window=self.cuerpo,
            anchor="nw"
        )

        self.cuerpo.bind(
            "<Configure>",
            lambda e:
                self.canvas.configure(
                    scrollregion=self.canvas.bbox("all")
                )
        )

        self.canvas.bind(
            "<Configure>",
            self._redimensionar
        )

        self.mostrar_pestana(
            getattr(
                app,
                "_pestana_apariencia",
                "paletas"
            )
        )

        self.after(
            80,
            self._restaurar_scroll
        )

    # ==========================================================
    # FONDOS POR DEFECTO, MIS FONDOS Y ALEATORIO
    # ==========================================================

    def _ruta_en_uso(self):
        a = self.app.ajustes
        if a.get("fondo_tipo") != "imagen":
            return ""
        return _norm_ruta(a.get("fondo_imagen", ""))

    def _tras_elegir_fondo(self):
        """Redibuja esta pantalla (si no la reconstruyó ya el cambio)."""
        if self.app.pantalla_apariencia is self:
            self.app._mostrar_pantalla_apariencia()

    def _tile_fondo(self, padre, nombre, mini, seleccionado, al_clic,
                    al_borrar=None):

        tile = tk.Frame(
            padre,
            bg=PANEL,
            width=self.ANCHO_TARJETA,
            height=110,
            cursor="hand2"
        )

        tile.pack_propagate(False)

        foto = ImageTk.PhotoImage(mini)
        self._fotos_fondos.append(foto)

        borde = ACENTO if seleccionado else PANEL_HOVER

        img = tk.Label(
            tile,
            image=foto,
            bg=PANEL,
            bd=0,
            highlightthickness=2,
            highlightbackground=borde,
            highlightcolor=borde,
            cursor="hand2"
        )

        img.pack()

        txt = tk.Label(
            tile,
            text=nombre,
            bg=PANEL,
            fg=TEXTO if seleccionado else TEXTO_SUAVE,
            font=(FUENTE, 8, "bold" if seleccionado else "normal"),
            cursor="hand2"
        )

        txt.pack(pady=(2, 0))

        for w in (tile, img, txt):
            w.bind("<Button-1>", lambda e: al_clic())

        if al_borrar is not None:

            x = tk.Label(
                tile,
                text="✕",
                bg=PANEL_HOVER,
                fg=TEXTO,
                font=(FUENTE, 8, "bold"),
                padx=4,
                cursor="hand2"
            )

            x.place(relx=1.0, x=-6, y=6, anchor="ne")

            x.bind("<Button-1>", lambda e: al_borrar())

        return tile

    def _panel_fondos_defecto(self):

        self._fotos_fondos = []

        caja = self._caja(
            "Fondos por defecto",
            "Dibujados por Otium. Al elegir uno, toda la interfaz "
            "adapta sus colores."
        )

        en_uso = self._ruta_en_uso()

        rejilla = tk.Frame(caja, bg=PANEL)
        rejilla.pack(fill="x", padx=14, pady=(0, 10))

        tarjetas = []

        for nombre in FONDOS_PREDEFINIDOS:

            sel = bool(en_uso) and en_uso == _norm_ruta(
                ruta_fondo_predefinido(nombre, False)
            )

            tarjetas.append(
                self._tile_fondo(
                    rejilla, nombre, miniatura_predefinido(nombre), sel,
                    lambda n=nombre: self._usar_predefinido(n)
                )
            )

        self._grupos.append((rejilla, tarjetas))
        self._organizar_tarjetas()

    def _panel_mis_fondos(self):

        caja = self._caja(
            "Mis fondos",
            "Tus imágenes, guardadas en Otium para usarlas cuando quieras."
        )

        en_uso = self._ruta_en_uso()

        rejilla = tk.Frame(caja, bg=PANEL)
        rejilla.pack(fill="x", padx=14, pady=(0, 10))

        tarjetas = []

        for ruta in listar_mis_fondos():

            tarjetas.append(
                self._tile_fondo(
                    rejilla, "Mi imagen", miniatura_archivo(ruta),
                    bool(en_uso) and en_uso == _norm_ruta(ruta),
                    lambda r=ruta: self._usar_mio(r),
                    lambda r=ruta: self._quitar_mio(r)
                )
            )

        nuevo = tk.Frame(
            rejilla,
            bg=PANEL_HOVER,
            width=self.ANCHO_TARJETA,
            height=88,
            cursor="hand2"
        )

        nuevo.pack_propagate(False)

        mas = tk.Label(
            nuevo, text="+", bg=PANEL_HOVER, fg=TEXTO,
            font=(FUENTE, 22, "bold"), cursor="hand2"
        )
        mas.pack(pady=(10, 0))

        txt = tk.Label(
            nuevo, text="Añadir imagen", bg=PANEL_HOVER, fg=TEXTO_SUAVE,
            font=(FUENTE, 8), cursor="hand2"
        )
        txt.pack()

        for w in (nuevo, mas, txt):
            w.bind("<Button-1>", lambda e: self._anadir_mis_fondos())

        tarjetas.append(nuevo)

        self._grupos.append((rejilla, tarjetas))
        self._organizar_tarjetas()

    def _panel_aleatorio(self):

        caja = self._caja(
            "Fondo aleatorio",
            "Elige un fondo al azar entre los de Otium y los tuyos."
        )

        fila = tk.Frame(caja, bg=PANEL)
        fila.pack(fill="x", padx=14, pady=(2, 4))

        tk.Button(
            fila, text="Sorprenderme", command=self._fondo_al_azar,
            bg=PANEL_HOVER, fg=TEXTO, activebackground=ACENTO,
            activeforeground=color_sobre(ACENTO), relief="flat", bd=0,
            font=(FUENTE, 9), cursor="hand2", padx=12, pady=4
        ).pack(side="left")

        self._crear_interruptor(
            caja, "Cambiar al abrir Otium",
            "Cada vez que abras la app tendrás un fondo distinto",
            "fondo_aleatorio"
        )

        tk.Frame(caja, bg=PANEL, height=6).pack()

    def _usar_predefinido(self, nombre):
        try:
            ruta = str(ruta_fondo_predefinido(nombre))
        except Exception:
            return
        self.app.cambiar_personalizado(
            fondo_tipo="imagen", fondo_imagen=ruta
        )
        self._tras_elegir_fondo()

    def _usar_mio(self, ruta):
        self.app.cambiar_personalizado(
            fondo_tipo="imagen", fondo_imagen=str(ruta)
        )
        self._tras_elegir_fondo()

    def _anadir_mis_fondos(self):
        rutas = filedialog.askopenfilenames(
            title="Añadir imágenes a Mis fondos",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.webp *.bmp")]
        )
        if not rutas:
            return
        agregadas = [r for r in map(importar_mi_fondo, rutas) if r]
        if agregadas:
            self._tras_elegir_fondo()

    def _quitar_mio(self, ruta):
        en_uso = self._ruta_en_uso() == _norm_ruta(ruta)
        borrar_mi_fondo(ruta)
        if en_uso:
            self.app.cambiar_personalizado(
                fondo_tipo="ninguno", fondo_imagen=""
            )
        self._tras_elegir_fondo()

    def _fondo_al_azar(self):
        self.app.fondo_al_azar()
        self._tras_elegir_fondo()

    # ==========================================================
    # MENÚ LATERAL DE SECCIONES
    # ==========================================================

    def _crear_menu(self, menu):

        self._seccion = getattr(
            self.app,
            "_pestana_apariencia",
            "paletas"
        )

        tk.Label(
            menu,
            text="SECCIONES",
            bg=FONDO,
            fg=TEXTO_SUAVE,
            font=(FUENTE, 8, "bold"),
            anchor="w"
        ).pack(
            fill="x",
            padx=8,
            pady=(4, 8)
        )

        self._tabs = {}

        for clave, texto, glifo in self.SECCIONES:

            fila = tk.Frame(
                menu,
                bg=FONDO,
                cursor="hand2"
            )

            fila.pack(
                fill="x",
                pady=2
            )

            icono = tk.Label(
                fila,
                text=glifo,
                bg=FONDO,
                fg=TEXTO_SUAVE,
                font=(FUENTE_ICONOS, 12),
                width=2,
                cursor="hand2"
            )

            icono.pack(
                side="left",
                padx=(8, 2),
                pady=9
            )

            nombre = tk.Label(
                fila,
                text=texto,
                bg=FONDO,
                fg=TEXTO_SUAVE,
                font=(FUENTE, 10, "bold"),
                anchor="w",
                cursor="hand2"
            )

            nombre.pack(
                side="left",
                fill="x",
                expand=True
            )

            for w in (fila, icono, nombre):

                w.bind(
                    "<Button-1>",
                    lambda e, c=clave:
                        self.mostrar_pestana(c)
                )

                w.bind(
                    "<Enter>",
                    lambda e, c=clave:
                        self._hover_menu(c)
                )

                w.bind(
                    "<Leave>",
                    lambda e:
                        self._pintar_menu()
                )

            self._tabs[clave] = (fila, icono, nombre)

    def _pintar_menu(self, hover=None):

        for clave, (fila, icono, nombre) in self._tabs.items():

            try:

                if clave == getattr(self, "_seccion", None):
                    bg = mezclar_hex(ACENTO, FONDO, 0.35)
                    fg_t, fg_i = TEXTO, ACENTO_HOVER

                elif clave == hover:
                    bg = PANEL
                    fg_t, fg_i = TEXTO, TEXTO_SUAVE

                else:
                    bg = FONDO
                    fg_t, fg_i = TEXTO_SUAVE, TEXTO_SUAVE

                fila.config(bg=bg)
                icono.config(bg=bg, fg=fg_i)
                nombre.config(bg=bg, fg=fg_t)

            except tk.TclError:
                pass

    def _hover_menu(self, clave):

        self._pintar_menu(hover=clave)

    # ==========================================================
    # VISTA PREVIA
    # ==========================================================

    def _ajustar_previa(self, e):
        """Oculta la vista previa si la ventana es muy angosta."""
        try:
            cabe = e.width >= self.MIN_ZONA_PREVIA

            if cabe and not self._previa_visible:

                self._previa.pack(
                    side="right",
                    fill="y",
                    padx=(14, 8),
                    before=self._marco_zona
                )

                self._previa_visible = True

            elif not cabe and self._previa_visible:

                self._previa.pack_forget()

                self._previa_visible = False

        except (AttributeError, tk.TclError):
            pass

    def _crear_previa(self, padre):

        caja = tk.Frame(
            padre,
            bg=PANEL,
            highlightthickness=1,
            highlightbackground=PANEL_HOVER
        )

        caja.pack(
            fill="x",
            pady=(2, 0)
        )

        tk.Label(
            caja,
            text="Vista previa",
            bg=PANEL,
            fg=TEXTO,
            font=(FUENTE, 11, "bold"),
            anchor="w"
        ).pack(
            fill="x",
            padx=14,
            pady=(12, 2)
        )

        tk.Label(
            caja,
            text="Así se ve tu reproductor ahora.",
            bg=PANEL,
            fg=TEXTO_SUAVE,
            font=(FUENTE, 8),
            anchor="w"
        ).pack(
            fill="x",
            padx=14,
            pady=(0, 8)
        )

        self._lbl_previa = tk.Label(
            caja,
            bg=PANEL,
            bd=0,
            highlightthickness=0
        )

        self._lbl_previa.pack(
            padx=12
        )

        self._txt_paleta = tk.Label(
            caja,
            bg=PANEL,
            fg=TEXTO,
            font=(FUENTE, 9),
            anchor="w"
        )

        self._txt_paleta.pack(
            fill="x",
            padx=14,
            pady=(10, 0)
        )

        self._txt_fondo = tk.Label(
            caja,
            bg=PANEL,
            fg=TEXTO_SUAVE,
            font=(FUENTE, 9),
            anchor="w"
        )

        self._txt_fondo.pack(
            fill="x",
            padx=14,
            pady=(2, 0)
        )

        muestras = tk.Frame(
            caja,
            bg=PANEL
        )

        muestras.pack(
            fill="x",
            padx=14,
            pady=(8, 14)
        )

        self._muestras = []

        for _ in range(5):

            m = tk.Label(
                muestras,
                width=3,
                height=1,
                bd=0,
                highlightthickness=1,
                highlightbackground=PANEL_HOVER
            )

            m.pack(
                side="left",
                padx=(0, 5)
            )

            self._muestras.append(m)

        self.refrescar_previa()

    def refrescar_previa(self):
        """Redibuja la miniatura con los ajustes actuales."""
        try:
            if not self._lbl_previa.winfo_exists():
                return
        except (AttributeError, tk.TclError):
            return

        try:
            foto = ImageTk.PhotoImage(self._img_previa())
            self._foto_previa = foto
            self._lbl_previa.config(image=foto)

            tipo = self.app.ajustes.get("fondo_tipo", "ninguno")

            self._txt_paleta.config(
                text="Paleta: " + str(self.app.tema_nombre)
            )

            self._txt_fondo.config(
                text="Fondo: " + self.NOMBRES_FONDO.get(tipo, "Sin fondo")
            )

            for m, c in zip(
                self._muestras,
                (ACENTO, ACENTO_HOVER, FONDO, PANEL, TEXTO)
            ):
                m.config(bg=c)

        except (tk.TclError, Exception):
            pass

    def _img_previa(self):
        """Miniatura del reproductor dibujada con Pillow."""
        from PIL import ImageColor

        w, h, k = self.PREVIA_W, self.PREVIA_H, 3
        W, H = w * k, h * k

        def rgb(c):
            try:
                return ImageColor.getrgb(c)[:3]
            except Exception:
                return (30, 30, 30)

        app = self.app
        a = app.ajustes

        fondo = Image.new("RGB", (W, H), rgb(FONDO))
        con_foto = False

        comp = getattr(app, "_fondo_comp", None)

        if (
            a.get("fondo_tipo", "ninguno") in TIPOS_LIENZO
            and comp is not None
            and getattr(app, "_fondo_vivo", False)
        ):
            try:
                cw, ch = comp.size
                esc = max(W / cw, H / ch)
                c2 = comp.convert("RGB").resize(
                    (max(1, round(cw * esc)), max(1, round(ch * esc))),
                    Image.Resampling.BILINEAR
                )
                x0 = (c2.width - W) // 2
                y0 = (c2.height - H) // 2
                fondo = c2.crop((x0, y0, x0 + W, y0 + H))
                con_foto = True
            except Exception:
                pass

        capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(capa)

        alfa = 165 if con_foto else 255

        def caja(x1, y1, x2, y2, r, color, al=255):
            d.rounded_rectangle(
                [x1 * k, y1 * k, x2 * k, y2 * k],
                radius=r * k,
                fill=rgb(color) + (al,)
            )

        def punto(cx, cy, r, color):
            d.ellipse(
                [(cx - r) * k, (cy - r) * k, (cx + r) * k, (cy + r) * k],
                fill=rgb(color) + (255,)
            )

        # Barra lateral
        caja(5, 5, 50, h - 32, 6, PANEL, alfa)

        for i in range(4):
            y = 14 + i * 14
            caja(
                11, y, 44, y + 5, 2,
                ACENTO if i == 0 else TEXTO_SUAVE
            )

        # Cabecera
        caja(
            56, 5, w - 5, 38, 6,
            mezclar_hex(ACENTO, FONDO, 0.32), alfa
        )
        caja(62, 11, 86, 32, 4, ACENTO)
        caja(92, 14, 150, 19, 2, TEXTO)
        caja(92, 24, 130, 28, 2, TEXTO_SUAVE)

        # Canciones
        for i in range(4):
            y = 44 + i * 17
            caja(56, y, w - 5, y + 14, 4, PANEL, alfa)
            caja(
                62, y + 4, 102 + i * 9, y + 8, 2,
                ACENTO if i == 0 else TEXTO_SUAVE
            )
            caja(w - 30, y + 5, w - 12, y + 8, 1, TEXTO_SUAVE)

        # Barra de reproducción
        caja(5, h - 27, w - 5, h - 5, 6, PANEL, alfa)

        mitad = w / 2

        caja(14, h - 17, mitad - 20, h - 14, 1, PANEL_HOVER)
        caja(14, h - 17, 14 + (mitad - 34) * 0.45, h - 14, 1, ACENTO)

        punto(mitad, h - 16, 7, globals().get("ACENTO_BOTON", ACENTO))

        caja(mitad + 22, h - 17, w - 16, h - 14, 1, PANEL_HOVER)
        caja(
            mitad + 22, h - 17,
            mitad + 22 + (mitad - 38) * 0.6, h - 14,
            1, ACENTO
        )

        img = Image.alpha_composite(
            fondo.convert("RGBA"), capa
        ).convert("RGB")

        return img.resize((w, h), Image.Resampling.LANCZOS)

    # ==========================================================
    # SCROLL
    # ==========================================================

    def _rueda(self, e):
        """Rueda del mouse sobre la pantalla de Apariencia."""
        try:
            sobre = self.winfo_containing(e.x_root, e.y_root)
        except Exception:
            return
        if sobre is None or not str(sobre).startswith(str(self)):
            return
        try:
            if e.num == 4:
                self.canvas.yview_scroll(-2, "units")
            elif e.num == 5:
                self.canvas.yview_scroll(2, "units")
            else:
                self.canvas.yview_scroll(int(-e.delta / 120) * 2, "units")
        except tk.TclError:
            pass

    def _anotar_scroll(self, valor):

        if not self._listo:
            return

        try:
            self.app._scroll_apariencia = float(valor)
        except (TypeError, ValueError):
            pass

    def _restaurar_scroll(self):

        try:
            self.canvas.yview_moveto(
                self._scroll_inicial
            )
        except tk.TclError:
            return

        self._listo = True

    def _redimensionar(self, event):

        self.canvas.itemconfig(
            self._ventana,
            width=event.width
        )

        ancho = max(
            event.width,
            1
        )

        if ancho >= 700:
            columnas = 4

        elif ancho >= 530:
            columnas = 3

        elif ancho >= 350:
            columnas = 2

        else:
            columnas = 1

        if columnas != self._columnas:

            self._columnas = columnas

            self._organizar_tarjetas()

    # ==========================================================
    # PESTAÑAS
    # ==========================================================

    def mostrar_pestana(self, clave):

        if clave not in {s[0] for s in self.SECCIONES}:
            clave = "paletas"        # p. ej. la antigua pestaña «personalizado»

        self.app._pestana_apariencia = clave
        self._seccion = clave
        self._pintar_menu()

        for widget in self.cuerpo.winfo_children():

            widget.destroy()

        self._grupos = []

        if clave == "paletas":

            self._crear_paletas()

        elif clave == "fondos":

            self._encabezado(
                "Fondos",
                "Elige qué hay detrás del reproductor."
            )

            self._panel_fondos_defecto()

            self._panel_mis_fondos()

            self._panel_aleatorio()

            self._panel_fondo_reproductor()

        elif clave == "efectos":

            self._encabezado(
                "Efectos",
                "Detalles visuales que se aplican sobre el fondo."
            )

            self._panel_efectos_reproductor()

        elif clave == "reproductor":

            self._encabezado(
                "Reproductor",
                "Tamaño de las portadas, controles e información."
            )

            self._panel_reproductor()

        else:

            self._encabezado(
                "Dinámico",
                "Haz que Otium cambie según lo que suena."
            )

            self._panel_dinamico()

        self.canvas.yview_moveto(0)

        self.refrescar_previa()

    def _encabezado(self, titulo, subtitulo):

        tk.Label(
            self.cuerpo,
            text=titulo,
            bg=FONDO,
            fg=TEXTO,
            font=(FUENTE, 13, "bold"),
            anchor="w"
        ).pack(
            fill="x",
            pady=(8, 2)
        )

        tk.Label(
            self.cuerpo,
            text=subtitulo,
            bg=FONDO,
            fg=TEXTO_SUAVE,
            font=(FUENTE, 9),
            anchor="w"
        ).pack(
            fill="x",
            pady=(0, 12)
        )

    # ==========================================================
    # PALETAS
    # ==========================================================

    def _crear_paletas(self):

        tk.Label(
            self.cuerpo,
            text="Paletas recomendadas",
            bg=FONDO,
            fg=TEXTO,
            font=(FUENTE, 12, "bold"),
            anchor="w"
        ).pack(
            fill="x",
            pady=(8, 3)
        )

        tk.Label(
            self.cuerpo,
            text="Elige una apariencia prediseñada para Otium.",
            bg=FONDO,
            fg=TEXTO_SUAVE,
            font=(FUENTE, 9),
            anchor="w"
        ).pack(
            fill="x",
            pady=(0, 12)
        )

        self._crear_categoria(
            "OSCURO",
            self.NOMBRES_OSCURAS
        )

        self._crear_categoria(
            "MINIMALISTA",
            self.NOMBRES_CLARAS
        )

        # ------------------------------------------------------
        # PERSONALIZADO (antes era otra pestaña)
        # ------------------------------------------------------

        tk.Label(
            self.cuerpo,
            text="PERSONALIZADO",
            bg=FONDO,
            fg=TEXTO,
            font=(FUENTE, 9, "bold"),
            anchor="w"
        ).pack(
            fill="x",
            pady=(20, 2)
        )

        tk.Label(
            self.cuerpo,
            text="Crea tu propio estilo: color principal, botones y modo.",
            bg=FONDO,
            fg=TEXTO_SUAVE,
            font=(FUENTE, 9),
            anchor="w"
        ).pack(
            fill="x",
            pady=(0, 4)
        )

        self._panel_color_reproductor()

        self._panel_color_botones()

        self._panel_modo()

        self._organizar_tarjetas()

    def _crear_categoria(
        self,
        titulo,
        nombres
    ):

        tk.Label(
            self.cuerpo,
            text=titulo,
            bg=FONDO,
            fg=TEXTO,
            font=(FUENTE, 9, "bold"),
            anchor="w"
        ).pack(
            fill="x",
            pady=(10, 7)
        )

        rejilla = tk.Frame(
            self.cuerpo,
            bg=FONDO
        )

        rejilla.pack(
            fill="x"
        )

        tarjetas = []

        for nombre in nombres:

            if nombre not in TEMAS:
                continue

            tarjeta = self._crear_tarjeta(
                rejilla,
                nombre
            )

            tarjetas.append(tarjeta)

        self._grupos.append(
            (
                rejilla,
                tarjetas
            )
        )

    def _organizar_tarjetas(self):

        columnas = max(
            1,
            self._columnas
        )

        for rejilla, tarjetas in self._grupos:

            for i, tarjeta in enumerate(tarjetas):

                tarjeta.grid(
                    row=i // columnas,
                    column=i % columnas,
                    padx=(0, 12),
                    pady=6,
                    sticky="nw"
                )

    # ==========================================================
    # TARJETAS DE PALETAS
    # ==========================================================

    def _crear_tarjeta(
        self,
        padre,
        nombre
    ):

        tema = TEMAS[nombre]

        seleccionada = (
            nombre == self.app.tema_nombre
        )

        tarjeta = tk.Frame(
            padre,
            bg=FONDO,
            width=self.ANCHO_TARJETA,
            height=self.ALTO_TARJETA,
            cursor="hand2"
        )

        tarjeta.pack_propagate(False)

        lienzo = tk.Canvas(
            tarjeta,
            width=self.ANCHO_TARJETA,
            height=82,
            bg=FONDO,
            highlightthickness=0,
            bd=0,
            cursor="hand2"
        )

        lienzo.pack()

        self._dibujar_preview(
            lienzo,
            tema,
            seleccionada
        )

        etiqueta = tk.Label(
            tarjeta,
            text=nombre,
            bg=FONDO,
            fg=(
                TEXTO
                if seleccionada
                else TEXTO_SUAVE
            ),
            font=(
                FUENTE,
                8,
                "bold"
                if seleccionada
                else "normal"
            ),
            cursor="hand2"
        )

        etiqueta.pack(
            pady=(2, 0)
        )

        def seleccionar(
            event=None,
            n=nombre
        ):
            self.app.elegir_paleta(n)

        for widget in (
            tarjeta,
            lienzo,
            etiqueta
        ):

            widget.bind(
                "<Button-1>",
                seleccionar
            )

        return tarjeta

    def _dibujar_preview(
        self,
        canvas,
        tema,
        seleccionada=False
    ):

        w = self.ANCHO_TARJETA
        h = 82

        borde = (
            tema["ACENTO"]
            if seleccionada
            else tema["PANEL_HOVER"]
        )

        grosor = (
            2
            if seleccionada
            else 1
        )

        rect_redondeado(
            canvas,
            2,
            2,
            w - 2,
            h - 2,
            10,
            fill=tema["FONDO"],
            outline=borde,
            width=grosor
        )

        # Barra lateral
        rect_redondeado(
            canvas,
            8,
            8,
            32,
            h - 8,
            6,
            fill=tema["PANEL"],
            outline=""
        )

        # Cabecera
        rect_redondeado(
            canvas,
            39,
            8,
            w - 8,
            28,
            6,
            fill=mezclar_hex(
                tema["ACENTO"],
                tema["FONDO"],
                0.32
            ),
            outline=""
        )

        # Colores de muestra
        colores = (
            tema["ACENTO"],
            tema["ACENTO_HOVER"],
            tema["PANEL_HOVER"],
            tema["TEXTO_SUAVE"]
        )

        for i, color in enumerate(colores):

            canvas.create_oval(
                46 + i * 13,
                16,
                55 + i * 13,
                25,
                fill=color,
                outline=""
            )

        # Líneas de canciones
        for i in range(3):

            y = 40 + i * 9

            canvas.create_line(
                43,
                y,
                105 + i * 9,
                y,
                fill=tema["TEXTO_SUAVE"],
                width=3,
                capstyle="round"
            )

        # Barra inferior
        rect_redondeado(
            canvas,
            39,
            h - 19,
            w - 8,
            h - 8,
            5,
            fill=tema["PANEL"],
            outline=""
        )

        canvas.create_oval(
            w - 39,
            h - 17,
            w - 27,
            h - 5,
            fill=tema["ACENTO"],
            outline=""
        )

    # ==========================================================
    # PERSONALIZADO
    # ==========================================================

    def _crear_personalizado(self):

        tk.Label(
            self.cuerpo,
            text="Personalizar apariencia",
            bg=FONDO,
            fg=TEXTO,
            font=(FUENTE, 13, "bold"),
            anchor="w"
        ).pack(
            fill="x",
            pady=(8, 2)
        )

        tk.Label(
            self.cuerpo,
            text="Crea una combinación propia para Otium.",
            bg=FONDO,
            fg=TEXTO_SUAVE,
            font=(FUENTE, 9),
            anchor="w"
        ).pack(
            fill="x",
            pady=(0, 12)
        )

        self._panel_color_reproductor()

        self._panel_color_botones()

        self._panel_modo()

        self._panel_fondo_reproductor()

        self._panel_efectos_reproductor()

        self._panel_proximamente()

    # ==========================================================
    # CAJA DE CONFIGURACIÓN
    # ==========================================================

    def _caja(
        self,
        titulo,
        descripcion=None
    ):

        caja = tk.Frame(
            self.cuerpo,
            bg=PANEL,
            highlightthickness=1,
            highlightbackground=PANEL_HOVER
        )

        caja.pack(
            fill="x",
            pady=(7, 5)
        )

        tk.Label(
            caja,
            text=titulo,
            bg=PANEL,
            fg=TEXTO,
            font=(FUENTE, 11, "bold"),
            anchor="w"
        ).pack(
            fill="x",
            padx=16,
            pady=(12, 2)
        )

        if descripcion:

            tk.Label(
                caja,
                text=descripcion,
                bg=PANEL,
                fg=TEXTO_SUAVE,
                font=(FUENTE, 8),
                anchor="w"
            ).pack(
                fill="x",
                padx=16,
                pady=(0, 8)
            )

        return caja

    # ==========================================================
    # COLOR DEL REPRODUCTOR
    # ==========================================================

    def _panel_color_reproductor(self):

        app = self.app
        ajustes = app.ajustes

        acento = (
            ajustes.get(
                "acento_personalizado"
            )
            or ACENTO
        )

        caja = self._caja(
            "Color del reproductor",
            "Elige el color principal y controla su intensidad."
        )

        fila = tk.Frame(
            caja,
            bg=PANEL
        )

        fila.pack(
            fill="x",
            padx=16,
            pady=(0, 12)
        )

        # ------------------------------------------------------
        # CÍRCULO DE COLOR
        # ------------------------------------------------------

        circulo = tk.Canvas(
            fila,
            width=48,
            height=48,
            bg=PANEL,
            highlightthickness=0,
            cursor="hand2"
        )

        circulo.pack(
            side="left"
        )

        circulo.create_oval(
            4,
            4,
            44,
            44,
            fill=acento,
            outline=PISTA,
            width=2
        )

        circulo.bind(
            "<Button-1>",
            lambda e:
                self._elegir_principal()
        )

        # ------------------------------------------------------
        # NOMBRE DEL COLOR
        # ------------------------------------------------------

        textos = tk.Frame(
            fila,
            bg=PANEL
        )

        textos.pack(
            side="left",
            padx=12
        )

        tk.Label(
            textos,
            text="Color principal",
            bg=PANEL,
            fg=TEXTO,
            font=(FUENTE, 10, "bold"),
            anchor="w"
        ).pack(
            fill="x"
        )

        tk.Label(
            textos,
            text=acento.upper(),
            bg=PANEL,
            fg=TEXTO_SUAVE,
            font=(FUENTE, 8),
            anchor="w"
        ).pack(
            fill="x",
            pady=(2, 0)
        )

        # ------------------------------------------------------
        # INTENSIDAD
        # ------------------------------------------------------

        zona = tk.Frame(
            fila,
            bg=PANEL
        )

        zona.pack(
            side="right",
            fill="x",
            expand=True,
            padx=(30, 0)
        )

        encabezado = tk.Frame(
            zona,
            bg=PANEL
        )

        encabezado.pack(
            fill="x"
        )

        tk.Label(
            encabezado,
            text="Intensidad",
            bg=PANEL,
            fg=TEXTO,
            font=(FUENTE, 9, "bold")
        ).pack(
            side="left"
        )

        valor = int(
            ajustes.get(
                "intensidad_personalizado",
                50
            )
        )

        etiqueta_valor = tk.Label(
            encabezado,
            text=f"{valor}%",
            bg=PANEL,
            fg=TEXTO_SUAVE,
            font=(FUENTE, 8)
        )

        etiqueta_valor.pack(
            side="right"
        )

        slider = Slider(
            zona,
            0,
            100,
            valor=valor,
            ancho=230,
            fondo=PANEL,
            al_mover=lambda v:
                etiqueta_valor.config(
                    text=f"{int(v)}%"
                ),
            al_soltar=lambda:
                app.cambiar_personalizado(
                    intensidad=round(
                        slider.get()
                    )
                )
        )

        slider.pack(
            fill="x",
            pady=(3, 0)
        )

        extremos = tk.Frame(
            zona,
            bg=PANEL
        )

        extremos.pack(
            fill="x"
        )

        tk.Label(
            extremos,
            text="Suave",
            bg=PANEL,
            fg=TEXTO_SUAVE,
            font=(FUENTE, 8)
        ).pack(
            side="left"
        )

        tk.Label(
            extremos,
            text="Intenso",
            bg=PANEL,
            fg=TEXTO_SUAVE,
            font=(FUENTE, 8)
        ).pack(
            side="right"
        )

    # ==========================================================
    # COLOR DE LOS BOTONES
    # ==========================================================

    def _panel_color_botones(self):

        app = self.app
        ajustes = app.ajustes

        acento = (
            ajustes.get(
                "acento_personalizado"
            )
            or ACENTO
        )

        propios = bool(
            ajustes.get(
                "botones_propios"
            )
        )

        color_botones = (
            ajustes.get(
                "color_botones"
            )
            or acento
        )

        caja = self._caja(
            "Color de los botones",
            "Todos los botones principales utilizarán el mismo color."
        )

        fila = tk.Frame(
            caja,
            bg=PANEL
        )

        fila.pack(
            fill="x",
            padx=16,
            pady=(0, 14)
        )

        # ------------------------------------------------------
        # CÍRCULO
        # ------------------------------------------------------

        circulo = tk.Canvas(
            fila,
            width=48,
            height=48,
            bg=PANEL,
            highlightthickness=0,
            cursor="hand2"
        )

        circulo.pack(
            side="left"
        )

        circulo.create_oval(
            4,
            4,
            44,
            44,
            fill=(
                color_botones
                if propios
                else acento
            ),
            outline=PISTA,
            width=2
        )

        if propios:

            circulo.bind(
                "<Button-1>",
                lambda e:
                    self._elegir_botones()
            )

        # ------------------------------------------------------
        # TEXTO
        # ------------------------------------------------------

        textos = tk.Frame(
            fila,
            bg=PANEL
        )

        textos.pack(
            side="left",
            padx=12
        )

        tk.Label(
            textos,
            text=(
                "Usar color principal"
                if not propios
                else "Color personalizado"
            ),
            bg=PANEL,
            fg=TEXTO,
            font=(FUENTE, 10, "bold"),
            anchor="w"
        ).pack(
            fill="x"
        )

        tk.Label(
            textos,
            text=(
                "Los botones utilizan el color principal."
                if not propios
                else "Pulsa el círculo para cambiarlo."
            ),
            bg=PANEL,
            fg=TEXTO_SUAVE,
            font=(FUENTE, 8),
            anchor="w"
        ).pack(
            fill="x",
            pady=(2, 0)
        )

        # ------------------------------------------------------
        # INTERRUPTOR
        # ------------------------------------------------------

        Interruptor(
            fila,
            valor=not propios,
            al_cambiar=lambda valor:
                app.cambiar_personalizado(
                    botones_propios=not valor
                )
        ).pack(
            side="right"
        )

    # ==========================================================
    # MODO OSCURO / CLARO
    # ==========================================================

    def _panel_modo(self):

        app = self.app
        ajustes = app.ajustes

        modo_actual = ajustes.get(
            "modo_personalizado",
            "oscuro"
        )

        caja = self._caja(
            "Modo de apariencia",
            "Utiliza tu color personalizado sobre un fondo oscuro o claro."
        )

        fila = tk.Frame(
            caja,
            bg=PANEL
        )

        fila.pack(
            fill="x",
            padx=16,
            pady=(0, 14)
        )

        for texto, clave in (
            ("Oscuro", "oscuro"),
            ("Claro", "claro")
        ):

            activo = (
                clave == modo_actual
                and app.tema_nombre ==
                TEMA_PERSONALIZADO
            )

            boton = tk.Label(
                fila,
                text=texto,
                bg=(
                    ACENTO_BOTON
                    if activo
                    else PANEL_HOVER
                ),
                fg=(
                    color_sobre(
                        ACENTO_BOTON
                    )
                    if activo
                    else TEXTO
                ),
                font=(FUENTE, 9, "bold"),
                padx=18,
                pady=7,
                cursor="hand2"
            )

            boton.pack(
                side="left",
                padx=(0, 7)
            )

            boton.bind(
                "<Button-1>",
                lambda e, m=clave:
                    app.cambiar_personalizado(
                        modo=m
                    )
            )

    # ==========================================================
    # OPCIONES QUE AÑADIREMOS EN ETAPA 2
    # ==========================================================

    def _panel_proximamente(self, textos=()):

        caja = self._caja(
            "Próximamente",
            "Estas opciones llegarán en los próximos pasos."
        )

        for texto in textos:
            fila = tk.Frame(caja, bg=PANEL)
            fila.pack(fill="x", padx=16, pady=3)
            tk.Label(
                fila, text="○", bg=PANEL, fg=PANEL_HOVER, font=(FUENTE, 12)
            ).pack(side="left")
            tk.Label(
                fila, text=texto, bg=PANEL, fg=TEXTO_SUAVE, font=(FUENTE, 9)
            ).pack(side="left", padx=8)
        tk.Frame(caja, bg=PANEL, height=8).pack()

    # ==========================================================
    # SELECTOR COLOR PRINCIPAL
    # ==========================================================

    def _elegir_principal(self):

        inicial = (
            self.app.ajustes.get(
                "acento_personalizado"
            )
            or ACENTO
        )

        _, elegido = colorchooser.askcolor(
            color=inicial,
            title="Elige el color principal",
            parent=self.winfo_toplevel()
        )

        if not elegido:
            return

        self.app.cambiar_personalizado(
            acento=elegido
        )

    # ==========================================================
    # SELECTOR COLOR DE BOTONES
    # ==========================================================

    def _elegir_botones(self):

        ajustes = self.app.ajustes

        inicial = (
            ajustes.get(
                "color_botones"
            )
            or ajustes.get(
                "acento_personalizado"
            )
            or ACENTO
        )

        _, elegido = colorchooser.askcolor(
            color=inicial,
            title="Elige el color de los botones",
            parent=self.winfo_toplevel()
        )

        if not elegido:
            return

        self.app.cambiar_personalizado(
            color_botones=elegido
        )


# ==============================================================
# FONDO DE LA INTERFAZ (imagen / color / portada)
# ==============================================================
FONDO_TRANSP_DEF = 35   # transparencia por defecto (0 = se ve toda la imagen)


def descargar_portada_fondo(video_id):
    """Miniatura grande, recortada en cuadrado, para usarla de fondo."""
    ultimo = None
    for nombre in ("maxresdefault", "mqdefault"):
        try:
            url = f"https://i.ytimg.com/vi/{video_id}/{nombre}.jpg"
            with urllib.request.urlopen(url, timeout=10) as r:
                datos = r.read()
            img = Image.open(io.BytesIO(datos)).convert("RGB")
            w, h = img.size
            lado = min(w, h)
            izq, arr = (w - lado) // 2, (h - lado) // 2
            return img.crop((izq, arr, izq + lado, arr + lado))
        except Exception as e:
            ultimo = e
    raise ultimo


def color_medio(img):
    """Color promedio de una imagen, en hexadecimal."""
    r, g, b = img.resize((1, 1), Image.Resampling.BOX).getpixel((0, 0))[:3]
    return "#%02x%02x%02x" % (r, g, b)


def componer_fondo(src, ancho, alto, tipo, color, difuminado,
                   transparencia, vidrio, base, estilo="transparente"):
    """Imagen final del tamaño de la ventana: recorte tipo «cubrir»,
    difuminado, vidrio y mezcla con el color del tema.
    estilo «nitida»: se respetan los deslizadores tal cual.
    estilo «transparente»: siempre suave y mezclada con la paleta."""
    if tipo == "color":
        return Image.new("RGB", (ancho, alto), color)

    d = max(0, min(100, int(difuminado)))
    tr = max(0, min(100, int(transparencia)))
    if estilo == "nitida":
        t = tr / 100 * 0.85
    else:
        d = 50 + d * 0.5
        t = (15 + tr * 0.85) / 100
    img = src.convert("RGB")
    iw, ih = img.size

    # Con difuminado se trabaja a media resolución (más rápido).
    s = 1.0 if (d == 0 and not vidrio) else 0.5
    w2, h2 = max(1, int(ancho * s)), max(1, int(alto * s))
    esc = max(w2 / iw, h2 / ih)
    nw, nh = max(1, round(iw * esc)), max(1, round(ih * esc))
    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
    izq, arr = (nw - w2) // 2, (nh - h2) // 2
    img = img.crop((izq, arr, izq + w2, arr + h2))

    radio = d / 100 * 60 * s + (10 * s if vidrio else 0)
    if radio > 0:
        img = img.filter(ImageFilter.GaussianBlur(radio))
    if s != 1.0:
        img = img.resize((ancho, alto), Image.Resampling.BICUBIC)
    if vidrio:
        img = Image.blend(img, Image.new("RGB", img.size, "#ffffff"), 0.08)
    if t > 0:
        img = Image.blend(img, Image.new("RGB", img.size, base), t)
    return img


# ---- Texto e iconos sobre lienzo: dejan ver la imagen de fondo ----------
TIPOS_LIENZO = ("imagen", "portada_cancion", "portada_playlist",
                "ambiente")
AJUSTES_REF = {}


def usa_lienzo():
    return AJUSTES_REF.get("fondo_tipo", "ninguno") in TIPOS_LIENZO


class EtiquetaLienzo(tk.Canvas):
    """Como un Label, pero el texto se dibuja sobre un lienzo y no tapa la
    imagen de fondo."""

    def __init__(self, padre, text="", fg=None, bg=None, font=None,
                 anchor="center", width=None, padx=1, pady=1, **kw):
        for k in ("justify", "wraplength", "textvariable", "relief", "bd"):
            kw.pop(k, None)
        self._txt = text
        self._fg = TEXTO if fg is None else fg
        self._ancla = anchor
        self._padx, self._pady = padx, pady
        self._chars = width
        self._fuente = (
            tkfont.Font(font=font) if font is not None
            else tkfont.Font(family=FUENTE, size=10)
        )
        super().__init__(
            padre, bg=FONDO if bg is None else bg,
            highlightthickness=0, bd=0, **kw
        )
        self._item = self.create_text(
            0, 0, text=text, fill=self._fg,
            font=self._fuente if font is None else font, anchor="w"
        )
        self.bind("<Configure>", lambda e: self._colocar())
        self._medir()

    def _medir(self):
        if self._chars:
            ancho = self._chars * self._fuente.measure("0")
        else:
            ancho = self._fuente.measure(self._txt)
        ancho += 2 * self._padx
        alto = self._fuente.metrics("linespace") + 2 * self._pady
        tk.Canvas.config(self, width=ancho, height=alto)

    def _colocar(self):
        w, h = max(self.winfo_width(), 1), max(self.winfo_height(), 1)
        a = str(self._ancla)
        if a in ("w", "nw", "sw"):
            x, ancla = self._padx, "w"
        elif a in ("e", "ne", "se"):
            x, ancla = w - self._padx, "e"
        else:
            x, ancla = w / 2, "center"
        self.itemconfig(self._item, anchor=ancla)
        self.coords(self._item, x, h / 2)

    def config(self, cnf=None, **kw):
        if cnf:
            kw.update(cnf)
        cambia = False
        if "text" in kw:
            self._txt = str(kw.pop("text"))
            self.itemconfig(self._item, text=self._txt)
            cambia = True
        for k in ("fg", "foreground"):
            if k in kw:
                self._fg = kw.pop(k)
                self.itemconfig(self._item, fill=self._fg)
        if "font" in kw:
            f = kw.pop("font")
            self._fuente = tkfont.Font(font=f)
            self.itemconfig(self._item, font=f)
            cambia = True
        if "anchor" in kw:
            self._ancla = kw.pop("anchor")
            self._colocar()
        for k in ("padx", "pady", "justify", "wraplength", "image",
                  "compound", "textvariable", "relief"):
            kw.pop(k, None)
        if kw:
            tk.Canvas.config(self, **kw)
        if cambia:
            self._medir()
            self._colocar()

    configure = config

    def cget(self, key):
        if key == "text":
            return self._txt
        if key in ("fg", "foreground"):
            return self._fg
        if key == "anchor":
            return self._ancla
        if key == "image":
            return ""
        return tk.Canvas.cget(self, key)


class BotonIconoLienzo(tk.Canvas):
    """BotonIcono dibujado sobre un lienzo (deja ver la imagen de fondo)."""

    def __init__(self, padre, nombre, comando, tam=14,
                 fondo=None, color=None, color_hover=None):
        fondo = FONDO if fondo is None else fondo
        color = TEXTO_SUAVE if color is None else color
        color_hover = TEXTO if color_hover is None else color_hover
        self._fuente = tkfont.Font(family=FUENTE_ICO, size=tam)
        self._tam = tam
        super().__init__(
            padre, bg=fondo, highlightthickness=0, bd=0, cursor="hand2"
        )
        self.activo = False
        self.color_base = color
        self.color_hover = color_hover
        self.color_normal = color
        self.hover_normal = color_hover
        self._texto = self.create_text(
            0, 0, text=glifo(nombre), font=(FUENTE_ICO, tam),
            fill=color, anchor="center"
        )
        self._medir(nombre)
        self.bind("<Button-1>", lambda e: comando())
        self.bind("<Enter>", lambda e: self.config(fg=self.color_hover))
        self.bind("<Leave>", lambda e: self.config(fg=self.color_base))
        self.bind("<Configure>", lambda e: self._colocar())

    def _medir(self, nombre):
        ancho = self._fuente.measure(glifo(nombre)) + 18
        alto = self._fuente.metrics("linespace") + 10
        tk.Canvas.config(self, width=ancho, height=alto)

    def _colocar(self):
        self.coords(
            self._texto,
            max(self.winfo_width(), 1) / 2, max(self.winfo_height(), 1) / 2
        )

    def config(self, cnf=None, **kw):
        if cnf:
            kw.update(cnf)
        for k in ("fg", "foreground"):
            if k in kw:
                self.itemconfig(self._texto, fill=kw.pop(k))
        if "text" in kw:
            self.itemconfig(self._texto, text=kw.pop("text"))
        for k in ("padx", "pady", "font", "image", "compound"):
            kw.pop(k, None)
        if kw:
            tk.Canvas.config(self, **kw)

    configure = config

    def set_icono(self, nombre):
        self.itemconfig(self._texto, text=glifo(nombre))
        self._medir(nombre)

    def set_activo(self, activo):
        self.activo = activo
        if activo:
            self.color_base, self.color_hover = ACENTO, ACENTO_HOVER
        else:
            self.color_base, self.color_hover = self.color_normal, self.hover_normal
        self.config(fg=self.color_base)


def etiqueta(padre, **kw):
    """Label normal, o sobre lienzo si el fondo es una imagen."""
    if usa_lienzo():
        return EtiquetaLienzo(padre, **kw)
    return tk.Label(padre, **kw)


def boton_icono(*args, **kw):
    if usa_lienzo():
        return BotonIconoLienzo(*args, **kw)
    return BotonIcono(*args, **kw)


# ==============================================================
# FONDOS POR DEFECTO Y MIS FONDOS
# ==============================================================
FONDOS_PREDEFINIDOS = (
    "Nocturno", "Atardecer", "Bosque", "Ciudad", "Cielo estrellado",
    "Auroras", "Montañas", "Mar", "Luna",
)


def _rgb_f(c):
    if isinstance(c, str):
        c = c.lstrip("#")
        return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))
    return tuple(c)


def _mezcla_f(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _degradado_f(w, h, paradas):
    """Degradado vertical. paradas = [(posición 0..1, color)]."""
    paradas = [(p, _rgb_f(c)) for p, c in paradas]
    col = Image.new("RGB", (1, 256))
    px = col.load()
    for y in range(256):
        t = y / 255
        for i in range(len(paradas) - 1):
            p0, c0 = paradas[i]
            p1, c1 = paradas[i + 1]
            if t <= p1 or i == len(paradas) - 2:
                u = 0 if p1 == p0 else min(1, max(0, (t - p0) / (p1 - p0)))
                px[0, y] = _mezcla_f(c0, c1, u)
                break
    return col.resize((w, h), Image.Resampling.BILINEAR)


def _capa_f(img, dibujar, color, desenfoque=0, alfa=1.0):
    """Pinta `color` donde dibuja la función `dibujar(ImageDraw)`."""
    mascara = Image.new("L", img.size, 0)
    dibujar(ImageDraw.Draw(mascara))
    if desenfoque > 0:
        mascara = mascara.filter(ImageFilter.GaussianBlur(desenfoque))
    if alfa < 1.0:
        mascara = mascara.point(lambda v: int(v * alfa))
    img.paste(_rgb_f(color), mask=mascara)


def _brillo_f(img, cx, cy, r, color, alfa=0.5):
    w, h = img.size
    _capa_f(
        img,
        lambda d: d.ellipse([cx * w - r, cy * h - r, cx * w + r, cy * h + r],
                            fill=255),
        color, desenfoque=r * 0.55, alfa=alfa
    )


def _estrellas_f(img, rng, n, ymax=1.0, tam=1.0):
    w, h = img.size
    s = w / 1280

    def pequenas(d):
        for _ in range(n):
            x, y = rng.random() * w, rng.random() * h * ymax
            r = (0.6 + rng.random() * 1.1) * s * tam
            d.ellipse([x - r, y - r, x + r, y + r],
                      fill=int(110 + rng.random() * 145))

    _capa_f(img, pequenas, "#ffffff", desenfoque=0.5 * s)

    def grandes(d):
        for _ in range(max(2, n // 40)):
            x, y = rng.random() * w, rng.random() * h * ymax
            r = (1.6 + rng.random() * 1.2) * s * tam
            d.ellipse([x - r, y - r, x + r, y + r], fill=255)

    _capa_f(img, grandes, "#ffffff", desenfoque=1.4 * s, alfa=0.9)


def _cresta_f(w, h, rng, base, amp, n=4):
    """Línea de montañas/colinas: lista de puntos (x, y) en píxeles."""
    ondas = [(rng.uniform(0.8, 3.2) * (i + 1) * 0.8,
              rng.uniform(0, 6.28), amp / (i + 1.3)) for i in range(n)]
    pts = []
    pasos = 90
    for i in range(pasos + 1):
        x = i / pasos
        y = base + sum(a * __import__("math").sin(6.2832 * f * x + p)
                       for f, p, a in ondas)
        pts.append((x * w, y * h))
    return pts


def _fondo_nocturno(w, h):
    rng = random.Random(11)
    img = _degradado_f(w, h, [(0, "#070b1f"), (0.55, "#1a1446"),
                              (1, "#3a1c5e")])
    _brillo_f(img, 0.78, 0.9, w * 0.38, "#b0306e", 0.38)
    _brillo_f(img, 0.18, 0.28, w * 0.30, "#2b4bd6", 0.22)
    _brillo_f(img, 0.5, 0.55, w * 0.25, "#6a2fb0", 0.20)
    _estrellas_f(img, rng, 140, 0.8)
    return img


def _fondo_atardecer(w, h):
    rng = random.Random(5)
    img = _degradado_f(w, h, [(0, "#2b1055"), (0.35, "#7a2c6e"),
                              (0.6, "#e0566b"), (0.8, "#ffa45b"),
                              (1, "#ffd08a")])
    _brillo_f(img, 0.5, 0.7, w * 0.30, "#ffd9a0", 0.55)
    sol = h * 0.70
    r = w * 0.065
    _capa_f(img, lambda d: d.ellipse([0.5 * w - r, sol - r, 0.5 * w + r,
                                      sol + r], fill=255),
            "#fff3cf", desenfoque=1.5)
    for base, amp, col, sem in ((0.84, 0.035, "#6b2a5c", 3),
                                (0.92, 0.03, "#2a1038", 8)):
        pts = _cresta_f(w, h, random.Random(sem), base, amp, 3)
        _capa_f(img, lambda d, p=pts: d.polygon(p + [(w, h), (0, h)],
                                                fill=255), col, 0.8)
    return img


def _pino_f(d, x, base, alto, ancho):
    for i in range(3):
        top = base - alto * (1 - i * 0.28)
        bot = base - alto * (0.62 - i * 0.28) * 0.55 if i < 2 else base
        mitad = ancho * (0.55 + i * 0.22)
        d.polygon([(x, top), (x - mitad, base - alto * (0.30 - i * 0.12)
                                          if False else bot + alto * 0.18),
                   (x + mitad, bot + alto * 0.18)], fill=255)


def _fondo_bosque(w, h):
    rng = random.Random(21)
    img = _degradado_f(w, h, [(0, "#0b1f1a"), (0.55, "#14402f"),
                              (1, "#0a1f17")])
    _brillo_f(img, 0.78, 0.18, w * 0.22, "#9be8c2", 0.28)
    capas = ((0.78, 0.30, "#1b5440", 26), (0.88, 0.38, "#10382b", 20),
             (1.0, 0.50, "#071c14", 14))
    for base, alto, col, n in capas:
        def dib(d, base=base, alto=alto, n=n):
            for i in range(n):
                x = (i + rng.uniform(-0.3, 0.3)) / (n - 1) * w
                a = alto * h * rng.uniform(0.7, 1.15)
                _pino_f(d, x, base * h, a, a * 0.20)
            d.rectangle([0, base * h, w, h], fill=255)
        _capa_f(img, dib, col, 0.6)
        _capa_f(img, lambda d, b=base: d.rectangle(
            [0, (b - 0.12) * h, w, (b + 0.02) * h], fill=255),
            "#9fd9c0", desenfoque=h * 0.05, alfa=0.14)
    return img


def _fondo_ciudad(w, h):
    rng = random.Random(8)
    img = _degradado_f(w, h, [(0, "#0d0b2a"), (0.6, "#3b1d63"),
                              (1, "#c0508a")])
    _brillo_f(img, 0.5, 0.95, w * 0.45, "#ff7ab8", 0.40)
    edificios = []
    for capa, (col, alto_max, base) in enumerate((("#2a1750", 0.50, 0.9),
                                                    ("#120a2b", 0.40, 1.0))):
        x = -10.0
        lista = []
        while x < w:
            ancho = rng.uniform(0.04, 0.09) * w
            alto = rng.uniform(0.18, alto_max) * h
            lista.append((x, base * h - alto, x + ancho, base * h))
            x += ancho + rng.uniform(0, 0.008) * w
        _capa_f(img, lambda d, l=lista: [d.rectangle(b, fill=255) for b in l],
                col, 0.5)
        edificios.append(lista)

    def ventanas(d):
        for (x1, y1, x2, y2) in edificios[1]:
            paso = max(6, w * 0.012)
            yy = y1 + paso
            while yy < y2 - paso:
                xx = x1 + paso * 0.6
                while xx < x2 - paso:
                    if rng.random() < 0.28:
                        d.rectangle([xx, yy, xx + paso * 0.45,
                                     yy + paso * 0.55], fill=255)
                    xx += paso
                yy += paso * 1.3

    _capa_f(img, ventanas, "#ffd98a", 0.4, 0.85)
    return img


def _fondo_estrellado(w, h):
    rng = random.Random(33)
    img = _degradado_f(w, h, [(0, "#02030c"), (1, "#101a3d")])

    def banda(d):
        d.polygon([(-0.1 * w, 0.95 * h), (0.2 * w, 0.62 * h),
                   (1.1 * w, 0.02 * h), (1.1 * w, 0.30 * h),
                   (0.3 * w, 0.98 * h)], fill=255)

    _capa_f(img, banda, "#8fa4ff", desenfoque=w * 0.07, alfa=0.38)
    _capa_f(img, banda, "#e8d8ff", desenfoque=w * 0.025, alfa=0.14)
    _estrellas_f(img, rng, 600, 1.0)
    return img


def _fondo_auroras(w, h):
    rng = random.Random(14)
    img = _degradado_f(w, h, [(0, "#020816"), (0.7, "#0b1f3a"),
                              (1, "#0d2b3a")])
    import math
    _estrellas_f(img, rng, 220, 0.7)
    for base, fase, col in ((0.34, 0.0, "#3dffa8"), (0.42, 2.0, "#25d0c9"),
                            (0.30, 4.0, "#9b6bff")):
        pts = [(i / 60 * w * 1.2 - 0.1 * w,
                (base + 0.10 * math.sin(i / 60 * 7 + fase)
                 + 0.04 * math.sin(i / 60 * 17 + fase * 2)) * h)
               for i in range(61)]
        _capa_f(img, lambda d, p=pts: d.line(p, fill=255, width=int(h * 0.16),
                                              joint="curve"),
                col, desenfoque=h * 0.07, alfa=0.55)
        _capa_f(img, lambda d, p=pts: d.line(p, fill=255, width=int(h * 0.04),
                                              joint="curve"),
                "#d8fff0", desenfoque=h * 0.02, alfa=0.35)
    pts = _cresta_f(w, h, random.Random(2), 0.9, 0.03, 3)
    _capa_f(img, lambda d: d.polygon(pts + [(w, h), (0, h)], fill=255),
            "#03080f", 0.8)
    return img


def _fondo_montanas(w, h):
    img = _degradado_f(w, h, [(0, "#243b6b"), (0.5, "#7a8fc4"),
                              (1, "#f3c9a8")])
    cielo = _rgb_f("#cfd8f0")
    capas = ((0.55, 0.10, "#5a6fa8", 41), (0.68, 0.11, "#42558f", 42),
             (0.80, 0.12, "#2d3a6b", 43), (0.92, 0.10, "#171e3d", 44))
    for i, (base, amp, col, sem) in enumerate(capas):
        pts = _cresta_f(w, h, random.Random(sem), base, amp, 5)
        _capa_f(img, lambda d, p=pts: d.polygon(p + [(w, h), (0, h)],
                                                fill=255), col, 0.8)
        _capa_f(img, lambda d, b=base: d.rectangle(
            [0, (b + 0.02) * h, w, (b + 0.16) * h], fill=255),
            "#dfe6f7", desenfoque=h * 0.06, alfa=0.20)
    return img


def _fondo_mar(w, h):
    rng = random.Random(9)
    hor = int(h * 0.55)
    cielo = _degradado_f(w, hor, [(0, "#16325f"), (0.6, "#7a6aa0"),
                                  (1, "#f2a173")])
    mar = _degradado_f(w, h - hor, [(0, "#2a5f8f"), (1, "#06182f")])
    img = Image.new("RGB", (w, h))
    img.paste(cielo, (0, 0))
    img.paste(mar, (0, hor))
    _brillo_f(img, 0.5, 0.55, w * 0.25, "#ffd9a0", 0.45)
    r = w * 0.05
    _capa_f(img, lambda d: d.ellipse([0.5 * w - r, hor - r * 0.9,
                                      0.5 * w + r, hor + r * 1.1], fill=255),
            "#fff0c8", 1.2)
    _capa_f(img, lambda d: d.rectangle([0, hor, w, h], fill=0), "#000000")

    def reflejo(d):
        for _ in range(70):
            y = hor + (rng.random() ** 1.6) * (h - hor)
            ancho = (0.02 + 0.10 * (y - hor) / (h - hor)) * w * rng.random()
            x = 0.5 * w + rng.uniform(-1, 1) * ancho * 1.4
            d.rectangle([x - ancho / 2, y, x + ancho / 2, y + max(1, h * 0.004)],
                        fill=int(120 + rng.random() * 135))

    _capa_f(img, reflejo, "#ffe2b0", desenfoque=0.8, alfa=0.8)
    return img


def _fondo_luna(w, h):
    rng = random.Random(3)
    img = _degradado_f(w, h, [(0, "#050816"), (1, "#15224d")])
    _estrellas_f(img, rng, 200, 0.9)
    cx, cy, r = 0.70 * w, 0.36 * h, w * 0.085
    _brillo_f(img, 0.70, 0.36, w * 0.30, "#7d95ff", 0.30)
    _brillo_f(img, 0.70, 0.36, w * 0.14, "#dfe8ff", 0.35)
    _capa_f(img, lambda d: d.ellipse([cx - r, cy - r, cx + r, cy + r],
                                     fill=255), "#f4f1e6", 0.8)

    def crateres(d):
        for _ in range(9):
            a = rng.uniform(0, 6.28)
            dd = rng.uniform(0, 0.7) * r
            rr = rng.uniform(0.07, 0.2) * r
            x, y = cx + dd * __import__("math").cos(a), \
                cy + dd * __import__("math").sin(a)
            d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=255)

    _capa_f(img, crateres, "#b9b6ac", desenfoque=r * 0.05, alfa=0.45)

    def nubes(d):
        for _ in range(6):
            x = rng.uniform(0.0, 1.0) * w
            y = rng.uniform(0.5, 0.85) * h
            d.ellipse([x - w * 0.18, y - h * 0.03, x + w * 0.18, y + h * 0.03],
                      fill=255)

    _capa_f(img, nubes, "#2a3a74", desenfoque=h * 0.03, alfa=0.55)
    return img


_GENERADORES_FONDO = {
    "Nocturno": _fondo_nocturno, "Atardecer": _fondo_atardecer,
    "Bosque": _fondo_bosque, "Ciudad": _fondo_ciudad,
    "Cielo estrellado": _fondo_estrellado, "Auroras": _fondo_auroras,
    "Montañas": _fondo_montanas, "Mar": _fondo_mar, "Luna": _fondo_luna,
}


def generar_fondo(nombre, ancho=1600, alto=900):
    """Dibuja uno de los fondos por defecto con código (sin archivos)."""
    return _GENERADORES_FONDO[nombre](ancho, alto).convert("RGB")


# ---------------------------------------------------------------- carpetas
def carpeta_fondos():
    c = carpeta_datos() / "fondos"
    c.mkdir(parents=True, exist_ok=True)
    return c


def carpeta_mis_fondos():
    c = carpeta_fondos() / "mis"
    c.mkdir(parents=True, exist_ok=True)
    return c


def _norm_ruta(r):
    return os.path.normcase(os.path.abspath(str(r))) if r else ""


def ruta_fondo_predefinido(nombre, crear=True):
    """Archivo del fondo por defecto (se dibuja la primera vez que se usa)."""
    ruta = carpeta_fondos() / (
        "predef_%d.jpg" % (FONDOS_PREDEFINIDOS.index(nombre) + 1)
    )
    if crear and not ruta.exists():
        generar_fondo(nombre).save(str(ruta), "JPEG", quality=90)
    return ruta


# ------------------------------------------------------------- miniaturas
_MINIATURAS_FONDO = {}


def _cubrir_f(img, w, h):
    iw, ih = img.size
    esc = max(w / iw, h / ih)
    img = img.resize((max(1, round(iw * esc)), max(1, round(ih * esc))),
                     Image.Resampling.LANCZOS)
    x, y = (img.width - w) // 2, (img.height - h) // 2
    return img.crop((x, y, x + w, y + h))


def miniatura_predefinido(nombre, w=150, h=84):
    clave = ("pre", nombre, w, h)
    if clave not in _MINIATURAS_FONDO:
        _MINIATURAS_FONDO[clave] = _cubrir_f(
            generar_fondo(nombre, w * 3, h * 3), w, h
        )
    return _MINIATURAS_FONDO[clave]


def miniatura_archivo(ruta, w=150, h=84):
    try:
        clave = ("arc", str(ruta), os.path.getmtime(ruta), w, h)
    except OSError:
        return Image.new("RGB", (w, h), "#333333")
    if clave not in _MINIATURAS_FONDO:
        try:
            img = Image.open(ruta)
            img.draft("RGB", (w * 2, h * 2))
            _MINIATURAS_FONDO[clave] = _cubrir_f(img.convert("RGB"), w, h)
        except Exception:
            _MINIATURAS_FONDO[clave] = Image.new("RGB", (w, h), "#333333")
    return _MINIATURAS_FONDO[clave]


# --------------------------------------------------------------- Mis fondos
def listar_mis_fondos():
    try:
        archivos = [p for p in carpeta_mis_fondos().iterdir()
                    if p.suffix.lower() == ".jpg"]
        return sorted(archivos, key=lambda p: p.stat().st_mtime)
    except Exception:
        return []


def importar_mi_fondo(ruta):
    """Copia una imagen a la biblioteca (reducida si es enorme)."""
    try:
        img = Image.open(ruta).convert("RGB")
        img.thumbnail((2400, 2400))
        destino = carpeta_mis_fondos() / (
            "mi_%d_%04d.jpg" % (int(time.time() * 1000), random.randint(0, 9999))
        )
        img.save(str(destino), "JPEG", quality=90)
        return destino
    except Exception:
        return None


def borrar_mi_fondo(ruta):
    try:
        os.remove(str(ruta))
    except OSError:
        pass


# ------------------------------------------------------------- al azar
def elegir_fondo_aleatorio(ajustes):
    """Ruta de un fondo al azar (por defecto o propio), distinto al actual."""
    actual = ""
    if ajustes.get("fondo_tipo") == "imagen":
        actual = _norm_ruta(ajustes.get("fondo_imagen", ""))
    candidatos = [
        ("pre", n, _norm_ruta(ruta_fondo_predefinido(n, False)))
        for n in FONDOS_PREDEFINIDOS
    ] + [("mi", str(p), _norm_ruta(p)) for p in listar_mis_fondos()]
    otros = [c for c in candidatos if c[2] != actual] or candidatos
    tipo, valor, _ = random.choice(otros)
    if tipo == "pre":
        return str(ruta_fondo_predefinido(valor))
    return valor


def fondo_aleatorio_inicio(ajustes):
    """Si está activado, cada vez que se abre Otium cambia el fondo."""
    if not ajustes.get("fondo_aleatorio"):
        return
    try:
        ruta = elegir_fondo_aleatorio(ajustes)
        if ruta:
            ajustes["fondo_tipo"] = "imagen"
            ajustes["fondo_imagen"] = ruta
            ajustes["fondo_paleta_imagen"] = True
    except Exception:
        pass





def fondo_desde_colores(dominante, vivo, ancho=1280, alto=720):
    """Fondo suave dibujado con los colores de la portada."""
    base = _rgb_f(dominante)
    vv = _rgb_f(vivo)
    arriba = _mezcla_f(base, (0, 0, 0), 0.62)
    abajo = _mezcla_f(base, vv, 0.25)
    abajo = _mezcla_f(abajo, (0, 0, 0), 0.35)
    img = _degradado_f(ancho, alto, [(0, arriba), (1, abajo)])
    _brillo_f(img, 0.22, 0.30, ancho * 0.36, vv, 0.42)
    _brillo_f(img, 0.82, 0.82, ancho * 0.40, _mezcla_f(base, (255, 255, 255), 0.25), 0.30)
    _brillo_f(img, 0.60, 0.15, ancho * 0.22, vv, 0.18)
    return img.convert("RGB")


def con_resplandor(img, pad, color, fuerza):
    """La carátula con un halo suave de color alrededor."""
    img = img.convert("RGBA")
    w, h = img.size
    ancho, alto = w + 2 * pad, h + 2 * pad
    mascara = Image.new("L", (ancho, alto), 0)
    ImageDraw.Draw(mascara).rounded_rectangle(
        [pad, pad, pad + w, pad + h], radius=max(6, pad), fill=255
    )
    mascara = mascara.filter(ImageFilter.GaussianBlur(pad * 0.7))
    k = 0.35 + 0.85 * max(0.0, min(1.0, fuerza))
    mascara = mascara.point(lambda v: int(min(255, v * k)))
    halo = Image.new("RGBA", (ancho, alto), _rgb_f(color) + (0,))
    halo.putalpha(mascara)
    halo.alpha_composite(img, (pad, pad))
    return halo


def aplicar_brillo_ambiental(img, color, fuerza):
    """Luz suave del color de la canción que sube desde los bordes."""
    ancho = img.size[0]
    f = max(0.0, min(1.0, fuerza))
    salida = img.copy()
    _brillo_f(salida, 0.50, 1.10, ancho * 0.40, color, 0.50 * f)
    _brillo_f(salida, 0.00, 0.00, ancho * 0.20, color, 0.26 * f)
    _brillo_f(salida, 1.00, 0.30, ancho * 0.18, color, 0.20 * f)
    return salida


# ==============================================================
# REPRODUCTOR: tamaño de portada, estilo de controles e información
# ==============================================================
ALBUMES = {}     # video_id -> álbum (lo entrega YouTube al preparar el audio)

# nombre: (portada de la cabecera, carátula de la barra inferior)
TAMANOS_PORTADA = {
    "pequena": (104, 44),
    "mediana": (140, 56),
    "grande": (176, 72),
}


def aplicar_reproductor(ajustes):
    """Pasa a las variables globales el tamaño elegido para las portadas."""
    global TAM_PORTADA, TAM_CARATULA_BARRA, ALTO_BARRA
    tam = ajustes.get("portada_tam", "mediana")
    if tam not in TAMANOS_PORTADA:
        tam = "mediana"
    TAM_PORTADA, TAM_CARATULA_BARRA = TAMANOS_PORTADA[tam]
    alto_controles = 106 if ajustes.get("controles_estilo") == "grandes" else 92
    ALTO_BARRA = max(alto_controles, TAM_CARATULA_BARRA + 28)


def medidas_controles(estilo):
    """Tamaños de los botones de la barra inferior según el estilo."""
    if estilo == "minimalistas":
        return {"chico": 12, "medio": 14, "play": 34, "ipl": 15,
                "sep": 5, "relleno": False}
    if estilo == "grandes":
        return {"chico": 18, "medio": 22, "play": 52, "ipl": 18,
                "sep": 8, "relleno": True}
    return {"chico": 14, "medio": 16, "play": 40, "ipl": 14,
            "sep": 6, "relleno": True}


def ancho_texto_barra():
    """Ancho para el título y artista de la barra (más corto con portada grande)."""
    return 190 + (56 - TAM_CARATULA_BARRA)


# ==============================================================
# REPRODUCTOR
# ==============================================================
class Reproductor:
    def __init__(self, root, ajustes):
        self.root = root
        self.ajustes = ajustes
        self.tema_nombre = nombre_tema_valido(ajustes)
        self.apariencia_abierta = False

        root.title("Otium")
        root.geometry(TAM_VENTANA)
        root.minsize(900, 580)
        root.configure(bg=FONDO)
        configurar_iconos(root)

        # --- Biblioteca ---
        self.playlists = []
        self.playlist_actual = None    # la que se muestra en pantalla
        self.playlist_sonando = None   # de la que sale la música
        self.cargar_playlists_guardadas()

        # --- Favoritos: «Mis favoritos» es una playlist automática ---
        self.me_gusta = {
            "nombre": "Mis favoritos", "url": "", "pistas": [],
            "no_disponibles": set(), "virtual": True
        }
        self.favoritos = []        # canciones con corazón (la última primero)
        self.ids_favoritos = set()
        self.cargar_favoritos()

        # --- Estado de reproducción ---
        self.pistas_originales = []    # canciones de la playlist mostrada
        self.pistas_vista = []         # esas mismas, ya filtradas y ordenadas
        self.cola = []                 # canciones que se reproducen (copia)
        self.indice = -1               # posición de la canción actual en la cola
        self.video_actual = None
        self.info_actual = None        # (título, artista) de la canción actual
        self.caratula_ok = False       # ¿ya cargó la carátula real?
        self.pausado = False
        self.arrastrando = False

        self.orden_col = None
        self.orden_desc = False

        self.aleatorio = bool(ajustes.get("aleatorio", False))
        self.repetir = entero_en_rango(ajustes.get("repetir"), REP_NO, 0, 2)
        self.historial = []            # ids de canciones ya sonadas
        self.reproducidas = set()      # ids ya sonadas (modo aleatorio)

        self.volumen_previo = 70
        self.volumen_guardado = entero_en_rango(ajustes.get("volumen"), 70, 0, 100)
        self._inicio_ms = 0            # minuto desde el que continuar
        self._reanudando = False       # canción cargada al abrir, aún en pausa
        self._media_id = None          # canción cuyo audio tiene cargado VLC
        self.dur_actual = None         # duración (s) de la canción actual
        self._ticks = 0                # para guardar el minuto cada 5 s
        self._guardar_job = None
        self._msg_job = None
        self._ultimo_play = None
        self.cache_portadas = {}
        self.cache_miniaturas = {}
        self.pool = ThreadPoolExecutor(max_workers=2)

        # Precarga del audio de la siguiente canción
        self.cache_audio = {}                  # video_id -> (enlace, momento)
        self.pool_audio = ThreadPoolExecutor(max_workers=1)
        self._precargando = set()              # ids que se están resolviendo
        self._esperando = None                 # id que la canción actual espera
        self._proxima_id = None                # id de la siguiente prevista

        self.instancia = vlc.Instance("--no-video")
        self.player = self.instancia.media_player_new()

        # Discord Rich Presence: muestra en tu perfil lo que escuchas   ← AÑADIR AQUÍ (4 líneas)
        self.discord = PresenciaDiscord(
            DISCORD_CLIENT_ID,
            activo=bool(ajustes.get("discord", True))
        ) if PresenciaDiscord else None

        self.configurar_estilos()

        self.f_barra_titulo = tkfont.Font(family=FUENTE, size=10, weight="bold")
        self.f_barra_texto = tkfont.Font(family=FUENTE, size=9)
        aplicar_reproductor(self.ajustes)
        self._tam_imgs = (TAM_PORTADA, TAM_CARATULA_BARRA)
        self._crear_imagenes_tema()

        # --- Interfaz ---
        root.grid_columnconfigure(0, minsize=ANCHO_LATERAL)
        root.grid_columnconfigure(1, weight=1)
        root.grid_rowconfigure(0, weight=1)
        root.grid_rowconfigure(1, minsize=ALTO_BARRA)

        self._construir_lateral()
        self._construir_contenido()
        self._construir_barra()

        # Atajos de teclado
        root.bind("<space>", self._tecla_espacio)
        root.bind("<Left>", lambda e: self._tecla(self.anterior))
        root.bind("<Right>", lambda e: self._tecla(self.siguiente))
        root.bind("<Up>", lambda e: self._tecla(lambda: self._ajustar_volumen(5)))
        root.bind("<Down>", lambda e: self._tecla(lambda: self._ajustar_volumen(-5)))
        root.bind_all("<Button-1>", self._clic_global, add="+")
        for evento in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            root.bind_all(evento, self._rueda_global, add="+")
        root.protocol("WM_DELETE_WINDOW", self._cerrar)

        # Pantalla inicial
        self._refrescar_lateral()
        self._aplicar_estado_botones()
        self.player.audio_set_volume(self.volumen_guardado)

        if self.playlists:
            self.abrir_playlist(self._playlist_guardada() or self.playlists[0])
            self._reanudar_guardada()
        else:
            self.panel_vacio.tkraise()

        colorear_barra_titulo(self.root, FONDO, TEXTO)
        self._parar_revision = threading.Event()                          
        self.root.after(4000, self._iniciar_revision_automatica)
        self.vigilar()

    # ==========================================================
    # CONSTRUCCIÓN DE LA INTERFAZ
    # ==========================================================
    def _crear_imagenes_tema(self):
        """Imágenes vacías que dependen de los colores de la paleta."""
        nota_suave = hex_a_rgb(TEXTO_SUAVE) + (255,)
        self.img_portada_vacia = ImageTk.PhotoImage(
            icono_nota(
                TAM_PORTADA, mezclar_hex(ACENTO, FONDO, 0.35), 14, 0.5
            )
        )
        self.img_caratula_vacia = ImageTk.PhotoImage(
            icono_nota(TAM_CARATULA_BARRA, PANEL_HOVER, 8, 0.5, nota_suave)
        )
        self.img_portada = self.img_portada_vacia
        if not self.caratula_ok:
            self.img_caratula = self.img_caratula_vacia

    def _construir_lateral(self):
        globals()["AJUSTES_REF"] = self.ajustes
        self.lateral = BarraLateral(
            self.root,
            al_abrir=self.abrir_playlist,
            al_nueva=self.menu_nueva_playlist,
            al_menu=self.mostrar_menu,
            al_apariencia=self.dialogo_apariencia,
            al_guardar_apariencia=self.guardar_apariencia
        )
        self.lateral.grid(row=0, column=0, sticky="nsew")
        self.lateral.ajustes = self.ajustes   # lo usa la sección PERSONALIZADO

    def _construir_contenido(self):
        self.contenido = tk.Frame(self.root, bg=FONDO)
        self.pantalla_apariencia = None
        self.contenido.grid(row=0, column=1, sticky="nsew")
        self.contenido.grid_rowconfigure(0, weight=1)
        self.contenido.grid_columnconfigure(0, weight=1)

        # --- Pantalla sin playlists ---
        self.panel_vacio = tk.Frame(self.contenido, bg=FONDO)
        self.panel_vacio.grid(row=0, column=0, sticky="nsew")
        tk.Label(
            self.panel_vacio, text="♪", font=(FUENTE_ICONOS, 54),
            bg=FONDO, fg=PANEL_HOVER
        ).place(relx=0.5, rely=0.38, anchor="center")
        tk.Label(
            self.panel_vacio,
            text="Aún no tienes playlists.\n"
                 "Pulsa «Nueva playlist» en la barra lateral para añadir una.",
            font=(FUENTE, 11), bg=FONDO, fg=TEXTO_SUAVE, justify="center"
        ).place(relx=0.5, rely=0.55, anchor="center")

        # --- Pantalla de una playlist ---
        self.panel_lista = tk.Frame(self.contenido, bg=FONDO)
        self.panel_lista.grid(row=0, column=0, sticky="nsew")

        bg = FONDO
        self.cab = tk.Frame(self.panel_lista, bg=bg)
        self.cab.pack(fill="x")
        self.cab.grid_columnconfigure(1, weight=1)

        self.portada = tk.Label(
            self.cab, image=self.img_portada_vacia, bg=bg, bd=0
        )
        self.portada.grid(row=0, column=0, padx=(24, 20), pady=(24, 10))

        info = tk.Frame(self.cab, bg=bg)
        info.grid(row=0, column=1, sticky="sw", pady=(24, 10))
        lbl_tipo = etiqueta(
            info, text="Playlist", bg=bg, fg=TEXTO_SUAVE,
            font=(FUENTE, 9), anchor="w"
        )
        lbl_tipo.pack(fill="x")
        self.lbl_nombre = etiqueta(
            info, text="", bg=bg, fg=TEXTO,
            font=(FUENTE, 26, "bold"), anchor="w"
        )
        self.lbl_nombre.pack(fill="x")
        self.lbl_resumen = etiqueta(
            info, text="", bg=bg, fg=TEXTO_SUAVE,
            font=(FUENTE, 9), anchor="w"
        )
        self.lbl_resumen.pack(fill="x")

        acciones = tk.Frame(self.cab, bg=bg)
        acciones.grid(
            row=1, column=0, columnspan=2, sticky="ew", padx=24, pady=(0, 14)
        )
        self.btn_play_cab = BotonCircular(
            acciones, 52, bg, ACENTO_BOTON, ACENTO_BOTON_HOVER,
            color_sobre(ACENTO_BOTON),
            self.play_cabecera, tam_icono=18
        )
        self.btn_play_cab.pack(side="left")
        self.btn_aleatorio_cab = boton_icono(
            acciones, "aleatorio", self.alternar_aleatorio, tam=16, fondo=bg
        )
        self.btn_aleatorio_cab.pack(side="left", padx=(12, 0))
        self.btn_mas = boton_icono(
            acciones, "mas",
            lambda: self.mostrar_menu(
                self.playlist_actual,
                self.btn_mas.winfo_rootx(),
                self.btn_mas.winfo_rooty() + self.btn_mas.winfo_height()
            ),
            tam=16, fondo=bg
        )
        self.btn_mas.pack(side="left")
        self.btn_orden = BotonOrden(
            acciones, fondo=bg, al_elegir=self.elegir_orden
        )
        self.btn_orden.pack(side="right")
        self.pildora = Pildora(
            acciones, fondo=bg, relleno=PANEL, ancho=260,
            al_cambiar=self.aplicar_vista
        )
        self.pildora.pack(side="right", padx=(0, 10))

        # Todo lo que cambia de color con la portada.
        self._tintables = [
            self.cab, self.portada, info, lbl_tipo, self.lbl_nombre,
            self.lbl_resumen, acciones, self.btn_play_cab,
            self.btn_aleatorio_cab, self.btn_mas, self.pildora,
            self.btn_orden
        ]
        self.color_cab = bg

        self.canvas_deg = tk.Canvas(
            self.panel_lista, height=ALTO_DEGRADADO, bg=FONDO,
            highlightthickness=0, bd=0
        )
        self.canvas_deg.pack(fill="x")
        self.canvas_deg.bind("<Configure>", lambda e: self._dibujar_degradado())

        self.lista = ListaCanciones(
            self.panel_lista, self.reproducir_fila, self.ordenar_por,
            cache=self.cache_miniaturas,
            al_favorito=self.alternar_favorito,
            es_favorito=self.es_favorito
        )
        self.lista.pack(fill="both", expand=True, padx=(16, 8), pady=(0, 8))
        self.lista.al_menu_cancion = self.mostrar_menu_cancion

    def _construir_barra(self):
        self._fondo_enganchar()
        barra = tk.Frame(self.root, bg=PANEL, height=ALTO_BARRA)
        self.barra = barra
        self.root.grid_rowconfigure(1, minsize=ALTO_BARRA)
        barra.grid(row=1, column=0, columnspan=2, sticky="nsew")
        barra.grid_propagate(False)
        barra.grid_rowconfigure(0, weight=1)
        barra.grid_columnconfigure(0, weight=1, uniform="lados")
        barra.grid_columnconfigure(1, minsize=460)
        barra.grid_columnconfigure(2, weight=1, uniform="lados")
        tk.Frame(barra, bg=PANEL_HOVER, height=1).place(x=0, y=0, relwidth=1)

        # --- Izquierda: portada + título ---
        izq = tk.Frame(barra, bg=PANEL)
        izq.grid(row=0, column=0, sticky="w", padx=(18, 0))
        con_info = bool(self.ajustes.get("info_en_barra", True))
        con_album = (
            self.ajustes.get("info_barra") == "titulo_artista_album"
        )
        self.lbl_caratula = tk.Label(
            izq, image=self.img_caratula, bg=PANEL, bd=0
        )
        if con_info:
            self.lbl_caratula.pack(side="left")
        textos = tk.Frame(izq, bg=PANEL)
        textos.pack(side="left", padx=(12 if con_info else 0, 0))
        self.lbl_titulo = etiqueta(
            textos, text="Ninguna canción", bg=PANEL, fg=TEXTO,
            font=self.f_barra_titulo, anchor="w"
        )
        self.lbl_artista = etiqueta(
            textos, text="", bg=PANEL, fg=TEXTO_SUAVE,
            font=self.f_barra_texto, anchor="w"
        )
        self.lbl_album = etiqueta(
            textos, text="", bg=PANEL, fg=TEXTO_SUAVE,
            font=(FUENTE, 8), anchor="w"
        )
        if con_info:
            self.lbl_titulo.pack(fill="x")
            self.lbl_artista.pack(fill="x")
            if con_album:
                self.lbl_album.pack(fill="x")
        self.estado = etiqueta(
            textos, text="", bg=PANEL, fg=ACENTO_HOVER,
            font=(FUENTE, 8), anchor="w"
        )
        self.estado.pack(fill="x")

        # --- Centro: controles + progreso ---
        centro = tk.Frame(barra, bg=PANEL)
        centro.grid(row=0, column=1, sticky="nsew", pady=(10, 8))

        controles = tk.Frame(centro, bg=PANEL)
        controles.pack(pady=(0, 2))
        m = medidas_controles(self.ajustes.get("controles_estilo", "clasicos"))
        sep = m["sep"]
        self.btn_corazon = boton_icono(
            controles, "corazon", self.alternar_favorito_actual,
            tam=m["chico"], fondo=PANEL
        )
        self.btn_corazon.pack(side="left", padx=sep)
        self.btn_aleatorio = boton_icono(
            controles, "aleatorio", self.alternar_aleatorio,
            tam=m["chico"], fondo=PANEL
        )
        self.btn_aleatorio.pack(side="left", padx=sep)
        boton_icono(
            controles, "anterior", self.anterior, tam=m["medio"],
            fondo=PANEL, color=TEXTO
        ).pack(side="left", padx=sep)
        if m["relleno"]:
            self.btn_play = BotonCircular(
                controles, m["play"], PANEL, TEXTO,
                mezclar_hex(TEXTO, FONDO, 0.82),
                FONDO, self.play_pausa, tam_icono=m["ipl"]
            )
        else:
            # Minimalista: sin círculo; solo se marca al pasar el ratón.
            self.btn_play = BotonCircular(
                controles, m["play"], PANEL, "", PANEL_HOVER,
                TEXTO, self.play_pausa, tam_icono=m["ipl"]
            )
        self.btn_play.pack(side="left", padx=sep + 2)
        boton_icono(
            controles, "siguiente", self.siguiente, tam=m["medio"],
            fondo=PANEL, color=TEXTO
        ).pack(side="left", padx=sep)
        self.btn_repetir = boton_icono(
            controles, "repetir", self.alternar_repetir,
            tam=m["chico"], fondo=PANEL
        )
        self.btn_repetir.pack(side="left", padx=sep)
        etiqueta(
            controles, text=glifo("corazon"), font=(FUENTE_ICO, m["chico"]),
            bg=PANEL, fg=PANEL, padx=8, pady=4
        ).pack(side="left", padx=sep)

        fila = tk.Frame(centro, bg=PANEL)
        fila.pack(fill="x", padx=8)
        self.lbl_t_act = etiqueta(
            fila, text="0:00", width=5, anchor="e",
            bg=PANEL, fg=TEXTO_SUAVE, font=(FUENTE, 9)
        )
        self.lbl_t_act.pack(side="left")
        self.lbl_t_tot = etiqueta(
            fila, text="0:00", width=5, anchor="w",
            bg=PANEL, fg=TEXTO_SUAVE, font=(FUENTE, 9)
        )
        self.lbl_t_tot.pack(side="right")
        self.progreso = Slider(
            fila, desde=0, hasta=1000, fondo=PANEL,
            al_presionar=lambda: setattr(self, "arrastrando", True),
            al_soltar=self.saltar
        )
        self.progreso.pack(side="left", fill="x", expand=True)

        # --- Derecha: volumen ---
        der = tk.Frame(barra, bg=PANEL)
        der.grid(row=0, column=2, sticky="e", padx=(0, 24))
        self.btn_volumen = boton_icono(
            der, "volumen", self.alternar_mudo, tam=14, fondo=PANEL
        )
        self.btn_volumen.pack(side="left")
        self.volumen = Slider(
            der, desde=0, hasta=100, valor=self.volumen_guardado, ancho=110,
            fondo=PANEL, al_mover=self.cambiar_volumen,
            al_soltar=self.guardar_estado
        )
        self.volumen.pack(side="left")
        if self.volumen_guardado == 0:
            self.btn_volumen.set_icono("mudo")

    def configurar_estilos(self):
        estilo = ttk.Style()
        estilo.theme_use("clam")

        # Barra de scroll fina y sin flechas.
        estilo.configure(
            "Musica.Vertical.TScrollbar",
            background=PANEL_HOVER,
            troughcolor=FONDO,
            bordercolor=FONDO,
            arrowcolor=TEXTO_SUAVE,
            lightcolor=PANEL_HOVER,
            darkcolor=PANEL_HOVER,
            borderwidth=0
        )
        estilo.map(
            "Musica.Vertical.TScrollbar",
            background=[("active", ACENTO)]
        )
        estilo.layout("Musica.Vertical.TScrollbar", [
            ("Vertical.Scrollbar.trough", {
                "sticky": "ns",
                "children": [
                    ("Vertical.Scrollbar.thumb",
                    {"expand": "1", "sticky": "nswe"})
                ],
            })
        ])

    def boton(
        self, padre, texto, comando,
        ancho=None, acento=False
    ):
        """Botón plano de texto (para los cuadros de diálogo)."""
        color = ACENTO_BOTON if acento else PANEL
        hover = ACENTO_BOTON_HOVER if acento else PANEL_HOVER
        b = tk.Button(
            padre, text=texto, command=comando,
            width=ancho,
            bg=color, fg=color_sobre(color) if acento else TEXTO,
            activebackground=hover,
            activeforeground=color_sobre(hover) if acento else TEXTO,
            relief="flat", bd=0, cursor="hand2",
            font=(FUENTE, 10, "bold"), pady=5
        )
        b.bind("<Enter>", lambda e: b.config(bg=hover))
        b.bind("<Leave>", lambda e: b.config(bg=color))
        return b

    # ==========================================================
    # APARIENCIA (paletas de colores)
    # ==========================================================
    def _reconstruir(self):
        """Reconstruye la interfaz con la paleta actual sin detener la música."""
        aplicar_reproductor(self.ajustes)
        self._ajustar_tamano_imagenes()
        # Guardar el estado visual antes de destruir los widgets.
        playlist = self.playlist_actual
        orden_col = self.orden_col
        orden_desc = self.orden_desc
        busqueda = self.pildora.texto() if hasattr(self, "pildora") else ""

        video_actual = self.video_actual
        info_actual = self.info_actual
        dur_actual = self.dur_actual
        inicio_ms = self._posicion_ms() if video_actual else 0
        reproduciendo = bool(self.player.is_playing())
        pausado = self.pausado
        caratula_ok = self.caratula_ok
        img_caratula = self.img_caratula

        self._fondo_vivo = False
        # Los widgets anteriores ya no sirven con los colores nuevos.
        for nombre in ("lateral", "contenido", "barra"):
            widget = getattr(self, nombre, None)
            if widget is not None:
                try:
                    widget.destroy()
                except tk.TclError:
                    pass

        # Regenerar imágenes y estilos que dependen de la paleta.
        self.root.configure(bg=FONDO)
        self.configurar_estilos()
        self._crear_imagenes_tema()

        self._construir_lateral()
        self._construir_contenido()
        self._construir_barra()

        # Restaurar la playlist que estaba abierta.
        if playlist is not None:
            self._reconstruyendo = True
            try:
                self.abrir_playlist(playlist)
            finally:
                self._reconstruyendo = False
            self.orden_col = orden_col
            self.orden_desc = orden_desc
            if busqueda:
                self.pildora.poner_texto(busqueda)
            else:
                self.pildora.vaciar()
            self.aplicar_vista()
        else:
            self.panel_vacio.tkraise()

        # Si estábamos dentro de Apariencia, volver a mostrar esa pantalla.
        if self.apariencia_abierta:
            self._mostrar_pantalla_apariencia()

        # Restaurar la canción actual sin volver a cargar/reproducir el audio.
        self.video_actual = video_actual
        self.info_actual = info_actual
        self.dur_actual = dur_actual
        self.pausado = pausado
        self._inicio_ms = inicio_ms
        self.caratula_ok = caratula_ok
        self.img_caratula = img_caratula if caratula_ok else self.img_caratula_vacia

        if video_actual and info_actual:
            titulo, artista = info_actual
            self.lbl_titulo.config(
                text=ajustar(titulo, self.f_barra_titulo, ancho_texto_barra())
            )
            self.lbl_artista.config(
                text=ajustar(artista or "Artista desconocido", self.f_barra_texto, ancho_texto_barra())
            )
            self.lbl_t_act.config(text=self.formato(inicio_ms))
            if dur_actual:
                total_ms = int(dur_actual * 1000)
                self.lbl_t_tot.config(text=self.formato(total_ms))
                self.progreso.set(min(inicio_ms / total_ms, 1) * 1000)
            if caratula_ok:
                self.lbl_caratula.config(image=self.img_caratula)
        else:
            self.lbl_caratula.config(image=self.img_caratula_vacia)

        self._aplicar_estado_botones()
        self.player.audio_set_volume(self.volumen_guardado)
        self._refrescar_play(reproduciendo)
        colorear_barra_titulo(self.root, FONDO, TEXTO)
        self._refrescar_info_barra()
        self._refrescar_resplandor()
        self._fondo_reaplicar(80)

    CLAVES_APARIENCIA = [
    "tema",
    "acento_personalizado",
    "modo_personalizado",
    "intensidad_personalizado",
    "botones_propios",
    "color_botones",

    # --- Fondo y efectos ---
    "fondo_tipo",
    "fondo_imagen",
    "fondo_color",
    "fondo_color_elegido",
    "fondo_paleta_imagen",
    "fondo_estilo",
    "fondo_transparencia",
    "fondo_difuminado",
    "fondo_dinamico",
    "cambio_fondo_cancion",
    "adaptar_colores_portada",
    "efecto_vidrio",
    "resplandor_portada",
    "fondo_aleatorio",
    "color_interfaz",
    "modo_ambiente",
    "ambiente_previo",
    "fondo_dinamico_origen",
    "resplandor_intensidad",
    "brillo_ambiental",
    "brillo_intensidad",
    "fondo_animacion",
    "portada_tam",
    "controles_estilo",
    "info_en_barra",
    "info_barra",
]

    def dialogo_apariencia(self, pos=None):
        """Abre la pantalla de Apariencia en el área principal."""
        if self.apariencia_abierta:
            return
        self._ajustes_previos = {
            k: self.ajustes.get(k) for k in self.CLAVES_APARIENCIA
        }
        self._tema_previo = self.tema_nombre
        self.apariencia_abierta = True
        self._mostrar_pantalla_apariencia()

    def _mostrar_pantalla_apariencia(self):
        if self.pantalla_apariencia is not None:
            try:
                self.pantalla_apariencia.destroy()
            except tk.TclError:
                pass
        self.pantalla_apariencia = PantallaApariencia(self.contenido, self)
        self.pantalla_apariencia.grid(row=0, column=0, sticky="nsew")
        self.pantalla_apariencia.tkraise()

    def _ocultar_pantalla_apariencia(self):
        if self.pantalla_apariencia is not None:
            try:
                self.pantalla_apariencia.destroy()
            except tk.TclError:
                pass
            self.pantalla_apariencia = None
        if self.playlist_actual is not None:
            self.panel_lista.tkraise()
        else:
            self.panel_vacio.tkraise()

    def _aplicar_tema_actual(self):
        aplicar_tema(resolver_tema(self.tema_nombre, self.ajustes))
        self._reconstruir()

    def elegir_paleta(self, nombre):
        """Aplica una paleta (vista previa; se confirma con Guardar)."""
        if self.ajustes.get("fondo_tipo") == "color":
            self.ajustes["fondo_tipo"] = "ninguno"
        self.ajustes["fondo_paleta_imagen"] = False
        self.ajustes["color_interfaz"] = "personalizado"
        self.ajustes["modo_ambiente"] = False
        self.tema_nombre = nombre
        self._aplicar_tema_actual()

    def previsualizar_tema(self, nombre):
        self.elegir_paleta(nombre)

    def cambiar_personalizado(
            self, acento=None, modo=None, intensidad=None,
            botones_propios=None, color_botones=None,
            fondo_tipo=None, fondo_imagen=None, fondo_color=None,
            fondo_transparencia=None, fondo_difuminado=None,
            fondo_dinamico=None, cambio_fondo_cancion=None,
            adaptar_colores_portada=None, efecto_vidrio=None,
            resplandor_portada=None, fondo_aleatorio=None,
            fondo_dinamico_origen=None, color_interfaz=None,
            modo_ambiente=None, brillo_ambiental=None,
            fondo_animacion=None
        ):
        """Cambios de la pestaña Personalizado (vista previa en vivo).

        Los de color/paleta reconstruyen la interfaz; los de fondo solo
        vuelven a pintar el fondo (no tocan la pantalla de Apariencia).
        """
        a = self.ajustes
        a.setdefault("acento_personalizado", ACENTO)

        # --- Color principal y botones (reconstruyen la interfaz) ---
        tema_cambia = False
        if acento:
            a["acento_personalizado"] = acento
            tema_cambia = True
        if modo:
            a["modo_personalizado"] = modo
            tema_cambia = True
        if intensidad is not None:
            a["intensidad_personalizado"] = int(intensidad)
            tema_cambia = True
        if botones_propios is not None:
            a["botones_propios"] = bool(botones_propios)
            if botones_propios and not a.get("color_botones"):
                a["color_botones"] = a["acento_personalizado"]
            tema_cambia = True
        if color_botones:
            a["color_botones"] = color_botones
            tema_cambia = True
        if color_interfaz:
            a["color_interfaz"] = color_interfaz
            tema_cambia = True
        if acento or modo or intensidad is not None:
            a["color_interfaz"] = "personalizado"
            a["modo_ambiente"] = False
            self.tema_nombre = TEMA_PERSONALIZADO
            if fondo_tipo is None and a.get("fondo_tipo") == "color":
                a["fondo_tipo"] = "ninguno"   # gana lo último que elijas
            a["fondo_paleta_imagen"] = False

        # --- Fondo y efectos (no cambian la paleta) ---
        antes_activo = a.get("fondo_tipo", "ninguno") != "ninguno"
        antes_color = firma_paleta_fondo(a)
        antes_lienzo = a.get("fondo_tipo") in TIPOS_LIENZO
        hubo_fondo = False
        for clave, valor, conv in (
            ("fondo_tipo", fondo_tipo, str),
            ("fondo_imagen", fondo_imagen, str),
            ("fondo_color", fondo_color, str),
            ("fondo_transparencia", fondo_transparencia, int),
            ("fondo_difuminado", fondo_difuminado, int),
            ("fondo_dinamico", fondo_dinamico, bool),
            ("cambio_fondo_cancion", cambio_fondo_cancion, str),
            ("adaptar_colores_portada", adaptar_colores_portada, bool),
            ("efecto_vidrio", efecto_vidrio, bool),
            ("resplandor_portada", resplandor_portada, bool),
            ("fondo_aleatorio", fondo_aleatorio, bool),
            ("fondo_dinamico_origen", fondo_dinamico_origen, str),
            ("modo_ambiente", modo_ambiente, bool),
            ("brillo_ambiental", brillo_ambiental, bool),
            ("fondo_animacion", fondo_animacion, bool),
        ):
            if valor is not None:
                a[clave] = conv(valor)
                hubo_fondo = True
        if fondo_tipo == "imagen" or fondo_imagen is not None:
            a["fondo_paleta_imagen"] = True   # vuelve la paleta de la imagen
        if a.get("brillo_ambiental") and a.get("fondo_tipo", "ninguno") == "ninguno":
            a["fondo_tipo"] = "ambiente"      # solo brillo, sin imagen
        elif not a.get("brillo_ambiental") and a.get("fondo_tipo") == "ambiente":
            a["fondo_tipo"] = "ninguno"
        ahora_activo = a.get("fondo_tipo", "ninguno") != "ninguno"

        ahora_color = firma_paleta_fondo(a)
        cambia_paleta_color = antes_color != ahora_color
        cambia_lienzo = antes_lienzo != (a.get("fondo_tipo") in TIPOS_LIENZO)
        if (tema_cambia or cambia_paleta_color or cambia_lienzo
                or (antes_activo and not ahora_activo)):
            # Reconstruye (y _reconstruir vuelve a pintar el fondo).
            self._aplicar_tema_actual()
        elif hubo_fondo:
            self._fondo_reaplicar(0)

    def fondo_al_azar(self):
        # Pone un fondo al azar (por defecto o de Mis fondos).
        ruta = elegir_fondo_aleatorio(self.ajustes)
        if ruta:
            self.cambiar_personalizado(
                fondo_tipo="imagen", fondo_imagen=ruta
            )

    # ==========================================================
    # COLORES Y FONDO DINÁMICOS (siguen la canción que suena)
    # ==========================================================
    def _portada_para_dinamico(self, video_id, img):
        """Se llama al cargar la portada de la canción actual."""
        a = self.ajustes
        try:
            ancho, alto = img.size
            pal = paleta_desde_pil(
                img.crop((5, 5, max(6, ancho - 5), max(6, alto - 5)))
            )
        except Exception:
            pal = None
        self._paleta_portada = pal

        modo = a.get("color_interfaz", "personalizado")
        if pal and modo in ("portada", "automatico"):
            anterior = PALETA_PORTADA
            poner_paleta_portada(pal)
            if paletas_distintas(pal, anterior):
                self._programar_tema_portada()

        if (
            a.get("fondo_dinamico")
            and a.get("fondo_dinamico_origen") == "aleatorio"
            and video_id != getattr(self, "_ultimo_fondo_azar", None)
        ):
            self._ultimo_fondo_azar = video_id
            self.root.after(10, self.fondo_al_azar)

    def _programar_tema_portada(self):
        job = getattr(self, "_job_tema_portada", None)
        if job:
            try:
                self.root.after_cancel(job)
            except Exception:
                pass
        self._job_tema_portada = self.root.after(60, self._aplicar_tema_actual)

    def cambiar_dinamico(self, fondo_dinamico=None, origen=None,
                         color_interfaz=None, modo_ambiente=None):
        """Opciones de la sección Dinámico de Apariencia."""
        a = self.ajustes

        if modo_ambiente is not None:
            if modo_ambiente and not a.get("modo_ambiente"):
                a["ambiente_previo"] = {
                    k: a.get(k)
                    for k in ("fondo_tipo", "fondo_dinamico", "color_interfaz")
                }
                if getattr(self, "_paleta_portada", None):
                    poner_paleta_portada(self._paleta_portada)
                self.cambiar_personalizado(
                    fondo_tipo="portada_cancion", fondo_dinamico=False,
                    color_interfaz="portada", modo_ambiente=True
                )
            elif not modo_ambiente and a.get("modo_ambiente"):
                prev = a.pop("ambiente_previo", None) or {}
                self.cambiar_personalizado(
                    fondo_tipo=prev.get("fondo_tipo") or "ninguno",
                    fondo_dinamico=bool(prev.get("fondo_dinamico")),
                    color_interfaz=prev.get("color_interfaz") or "personalizado",
                    modo_ambiente=False
                )
            return

        cambios = {}
        if origen is not None:
            cambios["fondo_dinamico_origen"] = origen
        if fondo_dinamico is not None:
            cambios["fondo_dinamico"] = bool(fondo_dinamico)
        if color_interfaz is not None:
            cambios["color_interfaz"] = color_interfaz
            if (color_interfaz in ("portada", "automatico")
                    and getattr(self, "_paleta_portada", None)):
                poner_paleta_portada(self._paleta_portada)

        activo = cambios.get("fondo_dinamico", a.get("fondo_dinamico"))
        org = cambios.get(
            "fondo_dinamico_origen", a.get("fondo_dinamico_origen", "portada")
        )
        if activo and (fondo_dinamico is not None or origen is not None):
            if org == "aleatorio":
                ruta = elegir_fondo_aleatorio(a)
                if ruta:
                    cambios["fondo_tipo"] = "imagen"
                    cambios["fondo_imagen"] = ruta
            elif a.get("fondo_tipo") not in TIPOS_LIENZO:
                cambios["fondo_tipo"] = "portada_cancion"

        if cambios:
            self.cambiar_personalizado(**cambios)

    # ==========================================================
    # EFECTOS: resplandor, brillo ambiental y animación
    # ==========================================================
    def _con_resplandor(self, img, pad):
        """Devuelve la carátula con halo si el efecto está activado."""
        a = self.ajustes
        if not a.get("resplandor_portada"):
            return img
        try:
            cache = self.__dict__.setdefault("_vivo_resplandor", {})
            clave = id(img)
            if clave not in cache:
                if len(cache) > 8:
                    cache.clear()
                cache[clave] = (img, paleta_desde_pil(img)[1])
            color = cache[clave][1]
            return con_resplandor(
                img, pad, color, a.get("resplandor_intensidad", 60) / 100
            )
        except Exception:
            return img

    def _refrescar_resplandor(self):
        """Vuelve a dibujar las carátulas con o sin resplandor."""
        try:
            base = getattr(self, "_caratula_pil", None)
            if (base is not None and getattr(self, "caratula_ok", False)
                    and getattr(self, "lbl_caratula", None) is not None):
                self.img_caratula = ImageTk.PhotoImage(
                    self._con_resplandor(base, 6)
                )
                self.lbl_caratula.config(image=self.img_caratula)
            pb = getattr(self, "_portada_base", None)
            if pb is not None and pb[0] is self.playlist_actual:
                self.img_portada = ImageTk.PhotoImage(
                    self._con_resplandor(pb[1], 14)
                )
                self.portada.config(image=self.img_portada)
        except Exception:
            pass

    def cambiar_efecto(self, clave, valor):
        """Interruptores de Apariencia > Efectos."""
        self.cambiar_personalizado(**{clave: bool(valor)})
        self._refrescar_resplandor()

    def programar_efecto(self, clave, valor):
        """Barras de intensidad (guarda y pinta al hacer una pausa)."""
        self.ajustes[clave] = int(float(valor))
        job = getattr(self, "_job_efecto", None)
        if job:
            try:
                self.root.after_cancel(job)
            except Exception:
                pass
        self._job_efecto = self.root.after(140, self._aplicar_efectos)

    def _aplicar_efectos(self):
        self._job_efecto = None
        self._refrescar_resplandor()
        self._fondo_reaplicar(0)

    def _fondo_animar(self, viejo, nuevo):
        """Funde el fondo anterior con el nuevo en unos pasos cortos."""
        ident = self._anim_id
        pasos = 7

        def paso(i):
            if ident != self._anim_id:
                return
            frame = nuevo if i >= pasos else Image.blend(viejo, nuevo, i / pasos)
            self._fondo_comp = frame
            t0 = time.time()
            try:
                self._fondo_pintar(frame)
            except Exception:
                return
            if i < pasos:
                lento = (time.time() - t0) > 0.12     # equipo lento: sin pasos
                self.root.after(
                    30, lambda: paso(pasos if lento else i + 1)
                )

        paso(1)

    # ---- Reproductor: tamaño de portada, controles e información ----
    def _ajustar_tamano_imagenes(self):
        """Si cambió el tamaño de las portadas, reescala las que ya hay."""
        actual = (TAM_PORTADA, TAM_CARATULA_BARRA)
        previo = getattr(self, "_tam_imgs", None)
        self._tam_imgs = actual
        if previo is None or previo == actual:
            return

        def esc(img, n):
            if img is None or img.size == (n, n):
                return img
            return img.resize((n, n), Image.LANCZOS)

        for k, v in list(self.cache_portadas.items()):
            self.cache_portadas[k] = (esc(v[0], TAM_PORTADA),) + tuple(v[1:])
        pb = getattr(self, "_portada_base", None)
        if pb is not None:
            self._portada_base = (pb[0], esc(pb[1], TAM_PORTADA))
        cp = getattr(self, "_caratula_pil", None)
        if cp is not None:
            self._caratula_pil = esc(cp, TAM_CARATULA_BARRA)
            if self.caratula_ok:
                self.img_caratula = ImageTk.PhotoImage(
                    self._con_resplandor(self._caratula_pil, 6)
                )

    def cambiar_reproductor(self, clave, valor):
        """Opciones de Apariencia > Reproductor (se ven al instante)."""
        self.ajustes[clave] = valor
        self._reconstruir()

    def _texto_album(self):
        if not self.video_actual:
            return ""
        album = ALBUMES.get(self.video_actual, "")
        if not album:
            # YouTube no dio álbum: se muestra la playlist.
            lista = self.playlist_sonando or self.playlist_actual or {}
            album = lista.get("nombre", "")
        return album

    def _refrescar_info_barra(self):
        """Pone el álbum bajo el artista (si esa opción está activada)."""
        lbl = getattr(self, "lbl_album", None)
        if lbl is None:
            return
        try:
            lbl.config(text=ajustar(
                self._texto_album(), self.f_barra_texto, ancho_texto_barra()
            ))
        except tk.TclError:
            pass

    def cambiar_estilo_fondo(self, estilo):
        self.ajustes["fondo_estilo"] = estilo
        self._fondo_reaplicar(0)

    def programar_fondo(self, **cambios):
        """Para los deslizadores: guarda el valor y pinta cuando el
        arrastre hace una pausa (sin reconstruir nada)."""
        for clave, valor in cambios.items():
            self.ajustes[clave] = int(float(valor))
        self._fondo_reaplicar(160)

    def restablecer_apariencia(self):
        """Restablece toda la personalización visual."""

        for k in self.CLAVES_APARIENCIA:
            if k != "tema":
                self.ajustes.pop(k, None)

        self.ajustes.update({
            "fondo_tipo": "ninguno",
            "fondo_imagen": "",
            "fondo_color": FONDO,
            "fondo_transparencia": FONDO_TRANSP_DEF,
            "fondo_difuminado": 0,
            "fondo_dinamico": False,
            "cambio_fondo_cancion": "cada_cancion",
            "adaptar_colores_portada": False,
            "efecto_vidrio": False,
            "resplandor_portada": False,
        })

        self.tema_nombre = TEMA_POR_DEFECTO

        self._aplicar_tema_actual()

        try:
            self._actualizar_fondo_reproductor()
        except Exception:
            pass

    # ==========================================================
    # FONDO: cabecera, barra lateral y barra inferior
    # ==========================================================
    def _actualizar_fondo_reproductor(self):
        """Compatibilidad con llamadas antiguas."""
        self._fondo_reaplicar(0)

    def _fondo_enganchar(self):
        """Repinta el fondo cuando cambia el tamaño de la ventana."""
        if getattr(self, "_fondo_enganchado", False):
            return
        self._fondo_enganchado = True
        self._fondo_tam = None
        self.root.bind("<Configure>", self._fondo_configure, add="+")
        self._fondo_reaplicar(200)

    def _fondo_configure(self, e):
        if e.widget is not self.root:
            return
        tam = (e.width, e.height)
        if tam == getattr(self, "_fondo_tam", None):
            return
        self._fondo_tam = tam
        self._fondo_reaplicar(250)

    def _fondo_reaplicar(self, ms=60):
        if self.ajustes.get("fondo_tipo", "ninguno") in ("ninguno", "color"):
            return
        job = getattr(self, "_fondo_job", None)
        if job:
            try:
                self.root.after_cancel(job)
            except Exception:
                pass
        self._fondo_job = self.root.after(ms, self._aplicar_fondo)

    # ---------------------------------------------------- imagen de origen
    def _fondo_fuente(self):
        """Devuelve (clave, imagen PIL) o None si aún no hay imagen."""
        a = self.ajustes
        tipo = a.get("fondo_tipo", "ninguno")
        if tipo == "color":
            return ("color", None)

        # Fondo dinámico: sigue la portada de la canción que suena.
        origen_din = a.get("fondo_dinamico_origen", "portada")
        if (a.get("fondo_dinamico") and self.video_actual
                and origen_din == "colores"
                and getattr(self, "_paleta_portada", None)):
            dom, vivo = self._paleta_portada
            clave = ("colores", dom, vivo)
            guardado = getattr(self, "_fondo_colores", None)
            if guardado is None or guardado[0] != clave:
                self._fondo_colores = (clave, fondo_desde_colores(dom, vivo))
            return (clave, self._fondo_colores[1])
        if (a.get("fondo_dinamico") and self.video_actual
                and origen_din == "portada"):
            tipo = "portada_cancion"

        if tipo == "ambiente":
            return (("ambiente", FONDO), Image.new("RGB", (64, 64), FONDO))

        if tipo == "imagen":
            ruta = a.get("fondo_imagen", "")
            if not ruta or not os.path.exists(ruta):
                return None
            try:
                clave = ("imagen", ruta, os.path.getmtime(ruta))
                cache = getattr(self, "_fondo_img_archivo", None)
                if cache is None or cache[0] != clave:
                    img = Image.open(ruta).convert("RGB")
                    img.thumbnail((2400, 2400))
                    self._fondo_img_archivo = (clave, img)
                return (clave, self._fondo_img_archivo[1])
            except Exception:
                return None

        video_id = None
        if tipo == "portada_cancion":
            video_id = self.video_actual
        elif tipo == "portada_playlist" and self.playlist_actual is not None:
            pistas = self.pistas_disponibles_de_playlist(self.playlist_actual)
            if pistas:
                video_id = pistas[0][1]
        if not video_id:
            return None

        cache = self.__dict__.setdefault("_cache_fondo", {})
        if video_id in cache:
            return (("portada", video_id), cache[video_id])
        self._fondo_pedir(video_id)
        return None

    def _fondo_pedir(self, video_id):
        pendientes = self.__dict__.setdefault("_fondo_pendientes", set())
        if video_id in pendientes:
            return
        pendientes.add(video_id)

        def tarea():
            try:
                img = descargar_portada_fondo(video_id)
            except Exception:
                img = None

            def fin():
                pendientes.discard(video_id)
                if img is not None:
                    cache = self.__dict__.setdefault("_cache_fondo", {})
                    if len(cache) > 12:
                        cache.pop(next(iter(cache)))
                    cache[video_id] = img
                    self._fondo_reaplicar(0)
            self.root.after(0, fin)

        self.pool.submit(tarea)

    # ------------------------------------------------------------ pintar
    def _aplicar_fondo(self):
        self._fondo_job = None
        try:
            self._aplicar_fondo_interno()
        except Exception:
            import traceback
            traceback.print_exc()
        # La vista previa de Apariencia sigue al fondo real.
        p = getattr(self, "pantalla_apariencia", None)
        if p is not None and getattr(self, "apariencia_abierta", False):
            try:
                p.refrescar_previa()
            except Exception:
                pass

    def _aplicar_fondo_interno(self):
        a = self.ajustes
        if a.get("fondo_tipo", "ninguno") in ("ninguno", "color"):
            self._fondo_vivo = False
            return
        root = self.root
        root.update_idletasks()
        ancho, alto = root.winfo_width(), root.winfo_height()
        if ancho < 200 or alto < 200:
            return
        fuente = self._fondo_fuente()
        if fuente is None:
            return                      # la portada aún se está descargando
        clave, src = fuente

        transp = a.get("fondo_transparencia", FONDO_TRANSP_DEF)
        dif = a.get("fondo_difuminado", 0)
        vidrio = bool(a.get("efecto_vidrio"))
        color = a.get("fondo_color") or FONDO
        estilo = "nitida"   # lo controlan las barras Nitidez y Transparencia
        brillo = bool(a.get("brillo_ambiental"))
        pal_b = getattr(self, "_paleta_portada", None)
        col_b = pal_b[1] if pal_b else ACENTO
        f_b = int(a.get("brillo_intensidad", 50))
        llave = (
            clave, ancho, alto, transp, dif, vidrio, color, FONDO, estilo,
            brillo, col_b if brillo else None, f_b if brillo else None
        )
        previo = getattr(self, "_fondo_comp_cache", None)
        if previo is not None and previo[0] == llave:
            comp = previo[1]
        else:
            comp = componer_fondo(
                src, ancho, alto,
                "color" if clave == "color" else "imagen",
                color, dif, transp, vidrio, FONDO, estilo
            )
            if brillo:
                comp = aplicar_brillo_ambiental(comp, col_b, f_b / 100)
            self._fondo_comp_cache = (llave, comp)
        self._anim_id = getattr(self, "_anim_id", 0) + 1   # corta animaciones viejas
        self._fondo_vivo = True

        # Animación suave: si cambió la fuente (o el color del brillo),
        # se funde con el fondo anterior.
        viejo = previo[1] if previo is not None else None
        if (
            a.get("fondo_animacion") and viejo is not None
            and viejo is not comp and viejo.size == comp.size
            and (previo[0][0] != llave[0]
                 or (brillo and previo[0][10] != llave[10]))
        ):
            self._fondo_animar(viejo, comp)
            return

        self._fondo_comp = comp
        self._fondo_pintar(comp)

    def _fondo_pintar(self, comp):
        root = self.root
        ox, oy = root.winfo_rootx(), root.winfo_rooty()
        ok_bgs = {
            c.lower() for c in (
                FONDO, PANEL, getattr(self, "color_cab", FONDO)
            )
        }
        lat = getattr(self, "lateral", None)
        opacos = set()
        no_bajar = set()
        if lat is not None:
            for nombre in ("flotante",):
                w = getattr(lat, nombre, None)
                if w is not None:
                    opacos.add(w)
            for nombre in ("interior", "pie"):
                w = getattr(lat, nombre, None)
                if w is not None:
                    no_bajar.add(w)
            cv = getattr(lat, "canvas", None)
            if cv is not None:
                self._fondo_envolver_scroll(cv)

        for region in (
            getattr(self, "lateral", None),
            getattr(self, "cab", None),
            getattr(self, "barra", None),
        ):
            if region is not None:
                self._fondo_recorrer(
                    region, comp, ox, oy, ok_bgs, opacos, no_bajar
                )
        if getattr(self, "canvas_deg", None) is not None:
            self._pintar_degradado_fondo()

    def _fondo_recorrer(self, w, comp, ox, oy, ok_bgs, opacos, no_bajar):
        if w in opacos:
            return
        try:
            clase = w.winfo_class()
            hijos = w.winfo_children()
            mapeado = w.winfo_ismapped()
        except tk.TclError:
            return
        if w is getattr(self, "canvas_deg", None):
            return
        if clase in ("Frame", "Label", "Canvas") and mapeado:
            try:
                self._fondo_widget(w, clase, comp, ox, oy, ok_bgs)
            except Exception:
                import traceback
                traceback.print_exc()
        if w in no_bajar:
            return
        for h in hijos:
            if getattr(h, "_es_fondo_lbl", False):
                continue
            self._fondo_recorrer(h, comp, ox, oy, ok_bgs, opacos, no_bajar)

    def _fondo_widget(self, w, clase, comp, ox, oy, ok_bgs):
        ww, hh = w.winfo_width(), w.winfo_height()
        if ww < 2 or hh < 2:
            return
        x, y = w.winfo_rootx() - ox, w.winfo_rooty() - oy

        # Color original del widget (por si otro código lo cambió).
        bg = str(w.cget("bg")).lower()
        if (
            getattr(w, "_fondo_bg0", None) is None
            or bg != getattr(w, "_fondo_bg_puesto", None)
        ):
            w._fondo_bg0 = bg
        if w._fondo_bg0 not in ok_bgs:
            return                       # botones, separadores, etc.

        recorte = comp.crop((x, y, x + ww, y + hh))
        medio = color_medio(recorte)

        if clase == "Frame":
            foto = ImageTk.PhotoImage(recorte)
            lbl = getattr(w, "_fondo_lbl", None)
            if lbl is None or not lbl.winfo_exists():
                lbl = tk.Label(
                    w, image=foto, bd=0, highlightthickness=0, bg=medio
                )
                lbl._es_fondo_lbl = True
                w._fondo_lbl = lbl
            else:
                lbl.config(image=foto, bg=medio)
            lbl.image = foto
            lbl.place(x=0, y=0, relwidth=1, relheight=1)
            lbl.lower()

        elif clase == "Label":
            # Siempre color liso (el promedio de su zona): con el fondo
            # difuminado casi no se nota y no hay recuadros ni bordes.
            w.config(bg=medio)
            w._fondo_bg_puesto = medio

        elif clase == "Canvas":
            foto = ImageTk.PhotoImage(recorte)
            w._fondo_foto = foto
            self._fondo_envolver(w)
            self._fondo_reponer(w)
            w._fondo_bg_puesto = str(w.cget("bg")).lower()

    # ---- Canvas: el fondo se vuelve a poner si el widget se redibuja ----
    def _fondo_envolver(self, c):
        if getattr(c, "_fondo_env", False):
            return
        c._fondo_env = True
        borrar = c.delete
        bajar = c.tag_lower

        def delete(*args, **kw):
            r = borrar(*args, **kw)
            if args and args[0] == "all":
                self._fondo_reponer(c)
            return r

        def tag_lower(*args, **kw):
            r = bajar(*args, **kw)
            try:
                tk.Canvas.tag_lower(c, "bgfoto")
            except tk.TclError:
                pass
            return r

        c.delete = delete
        c.tag_lower = tag_lower

    def _fondo_reponer(self, c):
        foto = getattr(c, "_fondo_foto", None)
        if foto is None:
            return
        try:
            tk.Canvas.delete(c, "bgfoto")
            c.create_image(
                c.canvasx(0), c.canvasy(0), image=foto, anchor="nw",
                tags="bgfoto"
            )
            tk.Canvas.tag_lower(c, "bgfoto")
        except tk.TclError:
            pass

    def _fondo_envolver_scroll(self, c):
        """La lista de playlists se desplaza: el fondo debe quedarse quieto."""
        if getattr(c, "_fondo_scroll", False):
            return
        c._fondo_scroll = True
        for nombre in ("yview", "yview_moveto", "yview_scroll"):
            original = getattr(c, nombre)

            def nuevo(*args, _o=original, **kw):
                r = _o(*args, **kw)
                if args:     # sin argumentos solo consulta la posición
                    try:
                        tk.Canvas.coords(
                            c, "bgfoto", c.canvasx(0), c.canvasy(0)
                        )
                    except tk.TclError:
                        pass
                    self._fondo_reaplicar(40)
                return r
            setattr(c, nombre, nuevo)

    def _pintar_degradado_fondo(self):
        """El degradado bajo la cabecera pasa de la imagen al color liso."""
        c = getattr(self, "canvas_deg", None)
        comp = getattr(self, "_fondo_comp", None)
        if c is None or comp is None or not getattr(self, "_fondo_vivo", False):
            return False
        w, h = c.winfo_width(), c.winfo_height()
        if w < 2 or h < 2:
            return True
        x = c.winfo_rootx() - self.root.winfo_rootx()
        y = c.winfo_rooty() - self.root.winfo_rooty()
        recorte = comp.crop((x, y, x + w, y + h))
        liso = Image.new("RGB", (w, h), FONDO)
        mascara = Image.linear_gradient("L").resize((w, h))
        recorte = Image.composite(liso, recorte, mascara)
        foto = ImageTk.PhotoImage(recorte)
        c.image_fondo = foto
        tk.Canvas.delete(c, "all")
        c.create_image(0, 0, image=foto, anchor="nw")
        return True

    def cancelar_apariencia(self):
        """Flecha de volver: descarta lo que no se guardó."""
        self._cerrar_apariencia(guardar=False)

    def guardar_apariencia(self):
        """Confirma todos los cambios de apariencia."""

        self.ajustes["tema"] = self.tema_nombre

        # Valores por defecto para evitar claves inexistentes.
        self.ajustes.setdefault("fondo_tipo", "ninguno")
        self.ajustes.setdefault("fondo_transparencia", FONDO_TRANSP_DEF)
        self.ajustes.setdefault("fondo_difuminado", 0)
        self.ajustes.setdefault("fondo_dinamico", False)
        self.ajustes.setdefault("cambio_fondo_cancion", "cada_cancion")
        self.ajustes.setdefault("adaptar_colores_portada", False)
        self.ajustes.setdefault("efecto_vidrio", False)
        self.ajustes.setdefault("resplandor_portada", False)

        guardar_ajustes(self.ajustes)

        self._cerrar_apariencia(guardar=True)

        try:
            self._actualizar_fondo_reproductor()
        except Exception:
            pass

    def _cerrar_apariencia(self, guardar):
        if not self.apariencia_abierta:
            return
        self.apariencia_abierta = False
        if guardar:
            self._ocultar_pantalla_apariencia()
            colorear_barra_titulo(self.root, FONDO, TEXTO)
            return

        previos = getattr(self, "_ajustes_previos", {})
        cambio = (
            self.tema_nombre != getattr(self, "_tema_previo", self.tema_nombre)
            or any(
                self.ajustes.get(k) != previos.get(k)
                for k in self.CLAVES_APARIENCIA if k != "tema"
            )
        )
        for k, v in previos.items():
            if k == "tema":
                continue
            if v is None:
                self.ajustes.pop(k, None)
            else:
                self.ajustes[k] = v
        self.tema_nombre = getattr(self, "_tema_previo", self.tema_nombre)
        if cambio:
            self._aplicar_tema_actual()      # reconstruye y deja la playlist
        else:
            self._ocultar_pantalla_apariencia()

    # ==========================================================
    # CABECERA: COLOR Y PORTADA
    # ==========================================================
    # CABECERA: COLOR Y PORTADA
    # ==========================================================
    def _tintar(self, color):
        self.color_cab = color
        for w in self._tintables:
            w.config(bg=color)
        self._dibujar_degradado()
        self._fondo_reaplicar()   # la tinta de la portada no tapa el fondo

    def _dibujar_degradado(self):
        if self._pintar_degradado_fondo():
            return
        c = self.canvas_deg
        w = c.winfo_width()
        c.delete("all")
        if w < 2:
            return
        for y in range(ALTO_DEGRADADO):
            t = 1 - y / ALTO_DEGRADADO
            c.create_line(
                0, y, w, y, fill=mezclar_hex(self.color_cab, FONDO, t)
            )

    def _poner_portada_inicial(self, playlist):
        self._tintar(mezclar_hex(color_playlist(playlist), FONDO, 0.30))
        self.portada.config(image=self.img_portada_vacia)

        pistas = self.pistas_disponibles_de_playlist(playlist)
        if not pistas:
            return

        video_id = pistas[0][1]
        if video_id in self.cache_portadas:
            self._aplicar_portada(playlist, *self.cache_portadas[video_id])
        else:
            self.pool.submit(self._portada_hilo, playlist, video_id)

    def _portada_hilo(self, playlist, video_id):
        try:
            img, color = descargar_cuadrada(video_id, TAM_PORTADA)
            portada = redondear(img, 12)
        except Exception:
            return
        self.root.after(
            0, lambda: self._guardar_portada(playlist, video_id, portada, color)
        )

    def _guardar_portada(self, playlist, video_id, portada, color):
        self.cache_portadas[video_id] = (portada, color)
        self._aplicar_portada(playlist, portada, color)

    def _aplicar_portada(self, playlist, portada, color):
        if playlist is not self.playlist_actual:
            return
        self._portada_base = (playlist, portada)
        self.img_portada = ImageTk.PhotoImage(self._con_resplandor(portada, 14))
        self.portada.config(image=self.img_portada)
        self._tintar(tinte(color))

    # ==========================================================
    # PLAYLISTS GUARDADAS
    # ==========================================================
    def cargar_playlists_guardadas(self):
        self.playlists = []

        if not ARCHIVO_PLAYLISTS.exists():
            return

        try:
            datos = json.loads(
                ARCHIVO_PLAYLISTS.read_text(encoding="utf-8")
            )

            if not isinstance(datos, list):
                return

            for p in datos:
                if not isinstance(p, dict):
                    continue

                nombre = str(p.get("nombre") or "Playlist")
                url = str(p.get("url") or "")
                pistas = []

                for pista in p.get("pistas", []):
                    if (
                        isinstance(pista, list)
                        and len(pista) >= 4
                        and pista[0]
                        and pista[1]
                    ):
                        pistas.append((
                            str(pista[0]),
                            str(pista[1]),
                            str(pista[2] or ""),
                            pista[3]
                        ))

                no_disponibles = set(
                    str(x)
                    for x in p.get("no_disponibles", [])
                )

                self.playlists.append({
                    "nombre": nombre,
                    "url": url,
                    "pistas": pistas,
                    "no_disponibles": no_disponibles,
                    "propia": bool(p.get("propia"))
                })
        except Exception:
            self.playlists = []

    def guardar_playlists(self):
        datos = []

        for p in self.playlists:
            datos.append({
                "nombre": p["nombre"],
                "url": p["url"],
                "propia": bool(p.get("propia")),
                "pistas": [
                    list(pista) for pista in p["pistas"]
                ],
                "no_disponibles": list(
                    p.get("no_disponibles", set())
                )
            })

        try:
            ARCHIVO_PLAYLISTS.write_text(
                json.dumps(
                    datos,
                    ensure_ascii=False,
                    indent=2
                ),
                encoding="utf-8"
            )
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"No se pudieron guardar las playlists:\n{e}"
            )

    # ==========================================================
    # FAVORITOS («Mis favoritos»)
    # ==========================================================
    def cargar_favoritos(self):
        self.favoritos = []
        try:
            datos = json.loads(ARCHIVO_FAVORITOS.read_text(encoding="utf-8"))
        except FileNotFoundError:
            datos = []
        except Exception:
            # Archivo dañado: se guarda una copia antes de empezar de cero.
            try:
                ARCHIVO_FAVORITOS.replace(ARCHIVO_FAVORITOS.with_suffix(".bak"))
            except OSError:
                pass
            datos = []
        if not isinstance(datos, list):
            datos = []

        vistos = set()
        for p in datos:
            if (
                isinstance(p, list) and len(p) >= 4
                and p[0] and p[1] and str(p[1]) not in vistos
            ):
                vistos.add(str(p[1]))
                self.favoritos.append(
                    (str(p[0]), str(p[1]), str(p[2] or ""), p[3])
                )
        self.ids_favoritos = vistos

    def guardar_favoritos(self):
        try:
            ARCHIVO_FAVORITOS.write_text(
                json.dumps(
                    [list(p) for p in self.favoritos],
                    ensure_ascii=False, indent=2
                ),
                encoding="utf-8"
            )
        except Exception as e:
            messagebox.showerror(
                "Error", f"No se pudieron guardar los favoritos:\n{e}"
            )

    def es_favorito(self, video_id):
        return video_id in self.ids_favoritos

    def _ids_no_disponibles(self):
        """Canciones que no se pueden reproducir, en cualquier playlist."""
        ids = set(self.me_gusta.get("no_disponibles", set()))
        for p in self.playlists:
            ids |= set(p.get("no_disponibles", set()))
        return ids

    def _pistas_me_gusta(self):
        ocultas = self._ids_no_disponibles()
        return [p for p in self.favoritos if p[1] not in ocultas]

    def alternar_favorito(self, pista):
        """Marca o desmarca una canción como «Mis favoritos»."""
        video_id = pista[1]
        if video_id in self.ids_favoritos:
            self.favoritos = [p for p in self.favoritos if p[1] != video_id]
            self.ids_favoritos.discard(video_id)
            self.mensaje("Quitada de Mis favoritos")
        else:
            self.favoritos.insert(0, tuple(pista[:4]))
            self.ids_favoritos.add(video_id)
            self.mensaje("Añadida a Mis favoritos")
        self.guardar_favoritos()
        # Dentro de «Mis favoritos» la fila no desaparece al instante (así la
        # lista no salta); se actualiza al volver a abrirla.
        self.lista.repintar_filas()
        self._refrescar_corazon_barra()

    def alternar_favorito_actual(self):
        """Corazón de la barra inferior: la canción que suena."""
        if not self.video_actual:
            return
        pista = next((p for p in self.cola if p[1] == self.video_actual), None)
        if pista is not None:
            self.alternar_favorito(pista)

    def _refrescar_corazon_barra(self):
        activo = bool(self.video_actual) and self.es_favorito(self.video_actual)
        self.btn_corazon.set_icono("corazon_lleno" if activo else "corazon")
        self.btn_corazon.set_activo(activo)


    def _indice_de(self, playlist):
        """Posición de la playlist en la lista (compara por identidad)."""
        for i, p in enumerate(self.playlists):
            if p is playlist:
                return i
        return None

    def pistas_disponibles_de_playlist(self, playlist):
        if playlist.get("virtual"):
            return self._pistas_me_gusta()
        no_disp = playlist.get("no_disponibles", set())
        return [
            pista for pista in playlist.get("pistas", [])
            if pista[1] not in no_disp
        ]

    def _refrescar_lateral(self):
        self.lateral.refrescar(
            [self.me_gusta] + self.playlists,
            self.playlist_actual, self.playlist_sonando
        )
        self._fondo_reaplicar(30)

    # ==========================================================
    # ABRIR / CREAR / EDITAR PLAYLISTS
    # ==========================================================
    def abrir_playlist(self, playlist):
        """Muestra una playlist SIN interrumpir la música que suena."""
        if playlist is None:
            return

        # Salir de Apariencia (sin guardar) al abrir otra playlist.
        if self.apariencia_abierta and not getattr(self, "_reconstruyendo", False):
            self._cerrar_apariencia(guardar=False)

        self.playlist_actual = playlist
        self.pistas_originales = self.pistas_disponibles_de_playlist(playlist)
        self.orden_col = None
        self.orden_desc = False
        self.pildora.vaciar()

        self.lbl_nombre.config(text=cortar(playlist["nombre"], 30))
        if playlist.get("virtual"):
            self.btn_mas.pack_forget()   # «Mis favoritos» no se renombra ni se borra
        else:
            self.btn_mas.pack(side="left")
        self.panel_lista.tkraise()
        self._poner_portada_inicial(playlist)
        self.aplicar_vista()
        self._refrescar_lateral()
        self._refrescar_play()

    # ==========================================================
    # CUADROS DE DIÁLOGO DENTRO DE LA MISMA VENTANA
    # ==========================================================
    def _dialogo(self, titulo, ancho=440):
        """Tarjeta flotante dentro de la ventana de Otium (sin ventanas
        aparte). Devuelve (contenedor, tarjeta): destruir el contenedor la
        cierra y suelta el bloqueo del resto de la app."""
        previo = getattr(self, "_dialogo_actual", None)
        try:
            if previo is not None and previo.winfo_exists():
                previo.destroy()
        except Exception:
            pass

        fondo_tarjeta = PANEL_HOVER
        sombra = mezclar_hex(FONDO, "#000000", 0.45)
        contenedor = tk.Frame(self.root, bg=sombra)
        tarjeta = tk.Frame(
            contenedor, bg=fondo_tarjeta, highlightthickness=1,
            highlightbackground=mezclar_hex(ACENTO, fondo_tarjeta, 0.45)
        )
        tarjeta.pack(padx=(0, 5), pady=(0, 5))
        tk.Frame(tarjeta, bg=fondo_tarjeta, width=ancho, height=1).pack()
        tk.Label(
            tarjeta, text=titulo, bg=fondo_tarjeta, fg=TEXTO,
            font=(FUENTE, 12, "bold"), anchor="w"
        ).pack(fill="x", padx=24, pady=(20, 12))

        contenedor.place(relx=0.5, rely=0.4, anchor="center")
        contenedor.lift()
        self._dialogo_actual = contenedor
        try:
            tarjeta.grab_set()   # el resto de la app no recibe clics
        except tk.TclError:
            pass
        return contenedor, tarjeta

    def _dialogo_texto(self, tarjeta, texto):
        tk.Label(
            tarjeta, text=texto, bg=PANEL_HOVER, fg=TEXTO_SUAVE,
            font=(FUENTE, 9), anchor="w"
        ).pack(fill="x", padx=24, pady=(0, 6))

    def _dialogo_campo(self, tarjeta, valor=""):
        entrada = tk.Entry(
            tarjeta, bg=FONDO, fg=TEXTO, insertbackground=TEXTO,
            relief="flat", font=(FUENTE, 11), highlightthickness=1,
            highlightbackground=PANEL, highlightcolor=ACENTO
        )
        entrada.pack(fill="x", padx=24, ipady=8)
        if valor:
            entrada.insert(0, valor)
            entrada.select_range(0, "end")
        return entrada

    def _dialogo_botones(self, tarjeta, cancelar, aceptar, texto_aceptar):
        fila = tk.Frame(tarjeta, bg=PANEL_HOVER)
        fila.pack(fill="x", padx=24, pady=(16, 20))
        self.boton(
            fila, texto_aceptar, aceptar, ancho=10, acento=True
        ).pack(side="right")
        if cancelar is not None:
            self.boton(fila, "Cancelar", cancelar, ancho=10).pack(
                side="right", padx=(0, 8)
            )

    def nueva_playlist(self):
        ventana, cuerpo = self._dialogo("Añadir playlist de YouTube")
        self._dialogo_texto(cuerpo, "Pega el link de la playlist")
        entrada = self._dialogo_campo(cuerpo)

        lbl_estado = tk.Label(
            cuerpo, text="", bg=PANEL_HOVER, fg=TEXTO_SUAVE,
            font=(FUENTE, 9), anchor="w"
        )
        lbl_estado.pack(fill="x", padx=24, pady=(8, 0))

        def aceptar():
            url = entrada.get().strip()
            if not url:
                return
            lbl_estado.config(text="Leyendo playlist...", fg=TEXTO_SUAVE)
            threading.Thread(
                target=self._cargar_hilo,
                args=(url, ventana, lbl_estado),
                daemon=True
            ).start()

        self._dialogo_botones(cuerpo, ventana.destroy, aceptar, "Añadir")
        entrada.focus_set()
        entrada.bind("<Return>", lambda e: aceptar())
        entrada.bind("<Escape>", lambda e: ventana.destroy())

    def _cargar_hilo(self, url, ventana, lbl_estado):
        try:
            nombre, pistas = leer_playlist(url)
        except Exception as e:
            mensaje = mensaje_error_playlist(e, "cargar")
            self.root.after(
                0, lambda: self._error_carga(mensaje, ventana, lbl_estado)
            )
            return

        self.root.after(
            0, lambda: self._carga_ok(url, pistas, nombre, ventana)
        )

    def _error_carga(self, mensaje, ventana, lbl_estado):
        try:
            if ventana.winfo_exists():
                lbl_estado.config(
                    text="No se pudo leer la playlist", fg="#ff7b7b"
                )
        except Exception:
            pass
        messagebox.showerror(
            "No se puede añadir la playlist", mensaje,
            parent=ventana if ventana.winfo_exists() else self.root
        )

    def _carga_ok(self, url, pistas, nombre, ventana):
        if not pistas:
            messagebox.showwarning(
                "Playlist no disponible",
                "No se encontraron canciones disponibles.\n\n"
                "Comprueba que la playlist sea pública o no listada "
                "en YouTube y que el enlace sea correcto.",
                parent=ventana if ventana.winfo_exists() else self.root
            )
            return

        existente = next(
            (p for p in self.playlists if p.get("url") == url), None
        )

        if existente:
            existente["pistas"] = pistas
            existente["no_disponibles"] = set()
            playlist = existente
        else:
            playlist = {
                "nombre": nombre,
                "url": url,
                "pistas": pistas,
                "no_disponibles": set()
            }
            self.playlists.append(playlist)

        self.guardar_playlists()

        if ventana.winfo_exists():
            ventana.destroy()

        self.abrir_playlist(playlist)

    # ==========================================================
    # PLAYLISTS PROPIAS
    # ==========================================================
    def _menu_estilo(self, padre=None):
        return tk.Menu(
            padre or self.root, tearoff=0, bg=PANEL, fg=TEXTO,
            activebackground=ACENTO, activeforeground=color_sobre(ACENTO),
            bd=0, relief="flat", font=(FUENTE, 10)
        )

    def menu_nueva_playlist(self):
        """Botón «Nueva playlist» de la barra lateral."""
        x = self.root.winfo_pointerx()
        y = self.root.winfo_pointery()
        menu = self._menu_estilo()
        menu.add_command(
            label="Playlist propia (vacía)",
            command=self.nueva_playlist_propia
        )
        menu.add_command(
            label="Desde un link de YouTube",
            command=self.nueva_playlist
        )
        try:
            menu.tk_popup(x, y)
        finally:
            menu.grab_release()

    def _propias(self):
        return [p for p in self.playlists if p.get("propia")]

    def nueva_playlist_propia(self, con_pista=None):
        """Pide un nombre y crea una playlist propia (opcionalmente con una
        primera canción)."""
        ventana, cuerpo = self._dialogo("Nueva playlist propia", ancho=380)
        self._dialogo_texto(cuerpo, "Nombre de la playlist")
        entrada = self._dialogo_campo(cuerpo, "Mi playlist")

        def crear():
            nombre = entrada.get().strip()
            if not nombre:
                return
            playlist = {
                "nombre": nombre,
                "url": "",
                "pistas": [],
                "no_disponibles": set(),
                "propia": True
            }
            if con_pista is not None:
                playlist["pistas"].append(tuple(con_pista[:4]))
            self.playlists.append(playlist)
            self.guardar_playlists()
            ventana.destroy()
            self.abrir_playlist(playlist)
            if con_pista is not None:
                self.mensaje(f"Añadida a {cortar(nombre, 24)}")

        self._dialogo_botones(cuerpo, ventana.destroy, crear, "Crear")
        entrada.focus_set()
        entrada.bind("<Return>", lambda e: crear())
        entrada.bind("<Escape>", lambda e: ventana.destroy())

    def agregar_a_playlist_propia(self, playlist, pista):
        if any(p[1] == pista[1] for p in playlist["pistas"]):
            self.mensaje(f"Ya estaba en {cortar(playlist['nombre'], 24)}")
            return
        playlist["pistas"].append(tuple(pista[:4]))
        self.guardar_playlists()
        self.mensaje(f"Añadida a {cortar(playlist['nombre'], 24)}")
        self._refrescar_si_abierta(playlist)

    def quitar_de_playlist_propia(self, playlist, pista):
        playlist["pistas"] = [
            p for p in playlist["pistas"] if p[1] != pista[1]
        ]
        self.guardar_playlists()
        self.mensaje(f"Quitada de {cortar(playlist['nombre'], 24)}")
        self._refrescar_si_abierta(playlist)

    def _refrescar_si_abierta(self, playlist):
        if playlist is self.playlist_actual:
            self.pistas_originales = self.pistas_disponibles_de_playlist(
                playlist
            )
            self.aplicar_vista()
    
    def copiar_link(self, pista):
        """Copia al portapapeles el link de YouTube de la canción."""
        self.root.clipboard_clear()
        self.root.clipboard_append(f"https://www.youtube.com/watch?v={pista[1]}")
        self.mensaje("Link copiado")

    def abrir_en_navegador(self, pista):
        """Abre la canción en YouTube, en tu navegador."""
        webbrowser.open(f"https://www.youtube.com/watch?v={pista[1]}")

    def mostrar_menu_cancion(self, indice, x, y):
        """Clic derecho sobre una canción de la lista."""
        if not (0 <= indice < len(self.lista.pistas)):
            return
        pista = self.lista.pistas[indice]
        actual = self.playlist_actual

        menu = self._menu_estilo()
        sub = self._menu_estilo(menu)
        for p in self._propias():
            if p is actual:
                continue
            sub.add_command(
                label=cortar(p["nombre"], 28),
                command=lambda p=p: self.agregar_a_playlist_propia(p, pista)
            )
        if sub.index("end") is not None:
            sub.add_separator()
        sub.add_command(
            label="Nueva playlist propia…",
            command=lambda: self.nueva_playlist_propia(con_pista=pista)
        )
        menu.add_cascade(label="Añadir a playlist", menu=sub)

        if self.es_favorito(pista[1]):
            menu.add_command(
                label="Quitar de Mis favoritos",
                command=lambda: self.alternar_favorito(pista)
            )
        else:
            menu.add_command(
                label="Añadir a Mis favoritos",
                command=lambda: self.alternar_favorito(pista)
            )
        menu.add_separator()                                              
        menu.add_command(
            label="Copiar link de YouTube",
            command=lambda: self.copiar_link(pista)
        )
        menu.add_command(
            label="Abrir en el navegador",
            command=lambda: self.abrir_en_navegador(pista)
        )

        if actual is not None and actual.get("propia"):
            menu.add_separator()
            menu.add_command(
                label="Quitar de esta playlist",
                command=lambda: self.quitar_de_playlist_propia(actual, pista)
            )
        try:
            menu.tk_popup(x, y)
        finally:
            menu.grab_release()

    def mostrar_menu(self, playlist, x, y):
        if playlist is not None and playlist.get("virtual"):
            return
        if playlist is None:
            return
        menu = tk.Menu(
            self.root, tearoff=0, bg=PANEL, fg=TEXTO,
            activebackground=ACENTO, activeforeground=color_sobre(ACENTO),
            bd=0, relief="flat", font=(FUENTE, 10)
        )
        menu.add_command(
            label="Renombrar",
            command=lambda: self.renombrar_playlist(playlist)
        )
        if not playlist.get("propia"):
            menu.add_command(
                label="Actualizar",
                command=lambda: self.actualizar_playlist(playlist)
            )
        menu.add_separator()
        menu.add_command(
            label="Eliminar",
            command=lambda: self.eliminar_playlist(playlist)
        )
        try:
            menu.tk_popup(x, y)
        finally:
            menu.grab_release()

    def renombrar_playlist(self, playlist):
        ventana, cuerpo = self._dialogo("Renombrar playlist", ancho=380)
        self._dialogo_texto(cuerpo, "Nuevo nombre")
        entrada = self._dialogo_campo(cuerpo, playlist["nombre"])

        def guardar():
            nombre = entrada.get().strip()
            if not nombre:
                return
            playlist["nombre"] = nombre
            self.guardar_playlists()
            if playlist is self.playlist_actual:
                self.lbl_nombre.config(text=cortar(nombre, 30))
            self._refrescar_lateral()
            ventana.destroy()

        self._dialogo_botones(cuerpo, ventana.destroy, guardar, "Guardar")
        entrada.focus_set()
        entrada.bind("<Return>", lambda e: guardar())
        entrada.bind("<Escape>", lambda e: ventana.destroy())

    def eliminar_playlist(self, playlist):
        if not messagebox.askyesno(
            "Eliminar playlist",
            f"¿Eliminar '{playlist['nombre']}' de Mis playlists?"
        ):
            return

        if playlist is self.playlist_sonando:
            self.detener_todo()

        indice = self._indice_de(playlist)
        if indice is not None:
            del self.playlists[indice]
        self.guardar_playlists()

        if playlist is self.playlist_actual:
            self.playlist_actual = None
            if self.playlists:
                self.abrir_playlist(
                    self.playlists[min(indice or 0, len(self.playlists) - 1)]
                )
            else:
                self.pistas_originales = []
                self.pistas_vista = []
                self.lista.cargar([])
                self.panel_vacio.tkraise()
                self._refrescar_lateral()
        else:
            self._refrescar_lateral()

    def actualizar_playlist(self, playlist):
        url = playlist.get("url", "").strip()
        if not url:
            return

        if playlist is self.playlist_actual:
            self.lbl_resumen.config(text="Actualizando playlist...")

        threading.Thread(
            target=self._actualizar_hilo,
            args=(playlist, url),
            daemon=True
        ).start()

    def _actualizar_hilo(self, playlist, url):
        try:
            _, pistas = leer_playlist(url)
        except Exception as e:
            mensaje = mensaje_error_playlist(e, "actualizar")
            self.root.after(0, lambda: self._error_actualizar(playlist, mensaje))
            return

        self.root.after(
            0, lambda: self._guardar_actualizacion(playlist, pistas)
        )

    def _error_actualizar(self, playlist, mensaje):
        if playlist is self.playlist_actual:
            self.actualizar_resumen()
        messagebox.showerror(
            "No se puede acceder a la playlist", mensaje, parent=self.root
        )

    def _guardar_actualizacion(self, playlist, pistas):
        playlist["pistas"] = pistas
        # Al actualizar de forma explícita se vuelve a intentar con
        # todas las canciones (puede que alguna ya funcione de nuevo).
        playlist["no_disponibles"] = set()
        self.guardar_playlists()

        if playlist is self.playlist_actual:
            self.pistas_originales = self.pistas_disponibles_de_playlist(playlist)
            self.aplicar_vista()

    # ==========================================================
    # VISTA: BÚSQUEDA Y ORDEN
    # ==========================================================
    def elegir_orden(self, columna, descendente):
        self.orden_col = columna
        self.orden_desc = descendente
        self.aplicar_vista()


    def ordenar_por(self, columna):
        if self.orden_col == columna:
            if not self.orden_desc:
                self.orden_desc = True
            else:
                self.orden_col = None
                self.orden_desc = False
        else:
            self.orden_col = columna
            self.orden_desc = False
        self.aplicar_vista()

    def aplicar_vista(self):
        termino = self.pildora.texto().lower()

        pistas = list(self.pistas_originales)

        if termino:
            pistas = [
                p for p in pistas
                if termino in p[0].lower()
                or termino in (p[2] or "").lower()
            ]

        if self.orden_col == "titulo":
            pistas.sort(key=lambda p: p[0].lower(), reverse=self.orden_desc)
        elif self.orden_col == "artista":
            pistas.sort(
                key=lambda p: ((p[2] or "").lower(), p[0].lower()),
                reverse=self.orden_desc
            )
        elif self.orden_col == "duracion":
            pistas.sort(key=lambda p: p[3] or 0, reverse=self.orden_desc)

        self.pistas_vista = pistas

        sonando = self._posicion_sonando_en_vista()
        self.lista.set_orden(self.orden_col, self.orden_desc)
        self.btn_orden.set_orden(self.orden_col, self.orden_desc)
        self.lista.cargar(pistas, sonando)
        self.actualizar_resumen()

    def _posicion_sonando_en_vista(self):
        """Dónde está la canción que suena dentro de la lista mostrada
        (solo si la lista mostrada es la playlist de la que suena)."""
        if self.video_actual and self.playlist_sonando is self.playlist_actual:
            for k, p in enumerate(self.pistas_vista):
                if p[1] == self.video_actual:
                    return k
        return None

    def _marcar_en_vista(self):
        self.lista.marcar_sonando(self._posicion_sonando_en_vista())
        self._refrescar_info_barra()

    def actualizar_resumen(self):
        n = len(self.pistas_vista)
        total = len(self.pistas_originales)

        if self.pildora.texto() and n != total:
            texto = f"{n} de {total} canciones"
        else:
            texto = f"{n} canción" if n == 1 else f"{n} canciones"

        segundos = sum(p[3] for p in self.pistas_vista if p[3])
        if segundos:
            texto += f"  ·  {formato_total(segundos)}"

        if self.playlist_actual is self.me_gusta and not self.pistas_originales:
            texto = "Aún no hay canciones. Pulsa el corazón de una canción para añadirla"
        if (
            self.playlist_actual is not None
            and self.playlist_actual.get("propia")
            and not self.pistas_originales
        ):
            texto = ("Playlist vacía. Clic derecho en una canción y elige "
                     "«Añadir a playlist»")
        self.lbl_resumen.config(text=texto)

    # ==========================================================
    # MODOS
    # ==========================================================
    def alternar_aleatorio(self):
        self.aleatorio = not self.aleatorio
        self.reproducidas = (
            {self.video_actual} if self.video_actual else set()
        )
        self.btn_aleatorio.set_activo(self.aleatorio)
        self.btn_aleatorio_cab.set_activo(self.aleatorio)
        self.mensaje(
            "Aleatorio: " + ("activado" if self.aleatorio else "desactivado")
        )
        if self.video_actual:
            self._preparar_proxima()
        self._guardar_pronto()

    def alternar_repetir(self):
        self.repetir = (self.repetir + 1) % 3

        textos = {
            REP_NO: ("repetir", "Repetir: desactivado"),
            REP_LISTA: ("repetir", "Repetir: toda la lista"),
            REP_UNA: ("repetir1", "Repetir: esta canción")
        }
        icono, mensaje = textos[self.repetir]
        self.btn_repetir.set_icono(icono)
        self.btn_repetir.set_activo(self.repetir != REP_NO)
        self.mensaje(mensaje)
        if self.video_actual:
            self._preparar_proxima()
        self._guardar_pronto()

    def mensaje(self, texto, ms=2500):
        if self._msg_job:
            self.root.after_cancel(self._msg_job)
            self._msg_job = None
        self.estado.config(text=texto)
        if ms and texto:
            self._msg_job = self.root.after(
                ms, lambda: self.estado.config(text="")
            )

    # ==========================================================
    # REPRODUCCIÓN
    # ==========================================================
    def _fijar_cola(self):
        """La cola de reproducción es una copia de la lista que se ve ahora."""
        if self.playlist_sonando is not self.playlist_actual:
            self.historial.clear()
            self.reproducidas.clear()
            self.playlist_sonando = self.playlist_actual
            self._refrescar_lateral()
        self.cola = list(self.pistas_vista)

    def iniciar_contexto(self, i=None):
        if not self.pistas_vista:
            return
        self._fijar_cola()
        if i is None:
            i = random.randrange(len(self.cola)) if self.aleatorio else 0
        self.reproducir(i)

    def reproducir_fila(self, i):
        if i >= len(self.pistas_vista):
            return

        video_id = self.pistas_vista[i][1]

        if (
            video_id == self.video_actual
            and self.playlist_sonando is self.playlist_actual
            and (self.player.is_playing() or self.pausado)
        ):
            return

        self._fijar_cola()
        if self.video_actual and video_id != self.video_actual:
            self.historial.append(self.video_actual)
        self.reproducir(i)

    def reproducir(self, i, inicio_ms=0):
        if not self.cola:
            return

        self.indice = i % len(self.cola)

        titulo, video_id, artista, duracion = self.cola[self.indice]
        self.video_actual = video_id
        self.dur_actual = duracion
        self._inicio_ms = inicio_ms
        self._reanudando = False
        self.info_actual = (titulo, artista)
        self.caratula_ok = False
        self._proxima_id = None
        self.reproducidas.add(video_id)

        self.lbl_titulo.config(text=ajustar(titulo, self.f_barra_titulo, ancho_texto_barra()))
        self.lbl_artista.config(
            text=ajustar(artista or "Artista desconocido", self.f_barra_texto, ancho_texto_barra())
        )
        self.mensaje("Cargando...", 0)
        self.lbl_caratula.config(image=self.img_caratula_vacia)
        self.img_caratula = self.img_caratula_vacia

        self._marcar_en_vista()
        self._refrescar_play()

        threading.Thread(
            target=self._caratula_hilo, args=(video_id,), daemon=True
        ).start()
        self._guardar_pronto()
        self._pedir_audio(video_id)

    # ----------------------------------------------------------
    # Audio: resolución y precarga
    # ----------------------------------------------------------
    def _audio_fresco(self, video_id):
        """Enlace de audio ya resuelto (y todavía válido), o None."""
        dato = self.cache_audio.get(video_id)
        if dato and time.time() - dato[1] < TTL_AUDIO:
            return dato[0]
        return None

    def _guardar_audio(self, video_id, url):
        self.cache_audio[video_id] = (url, time.time())
        # Se guardan pocos: se descartan los más antiguos.
        while len(self.cache_audio) > 8:
            mas_viejo = min(self.cache_audio, key=lambda k: self.cache_audio[k][1])
            del self.cache_audio[mas_viejo]

    def _pedir_audio(self, video_id):
        """Consigue el audio de la canción que se quiere oír ahora."""
        url = self._audio_fresco(video_id)
        if url:
            # Ya estaba precargado: arranca al instante.
            self._iniciar(video_id, url)
        elif video_id in self._precargando:
            # Se está resolviendo por adelantado: se espera ese resultado.
            self._esperando = video_id
        else:
            self._precargando.add(video_id)
            self._esperando = video_id
            threading.Thread(
                target=self._resolver_hilo, args=(video_id,), daemon=True
            ).start()

    def _precargar(self, video_id):
        """Resuelve el audio de una canción en segundo plano."""
        if self._audio_fresco(video_id) or video_id in self._precargando:
            return
        self._precargando.add(video_id)
        try:
            self.pool_audio.submit(self._resolver_hilo, video_id)
        except RuntimeError:
            self._precargando.discard(video_id)

    def _resolver_hilo(self, video_id):
        try:
            url = resolver_audio(video_id)
        except Exception as e:
            permanente = es_error_de_acceso(e)
            self.root.after(0, lambda: self._audio_fallo(video_id, permanente))
            return
        self.root.after(0, lambda: self._audio_listo(video_id, url))

    def _audio_listo(self, video_id, url):
        self._precargando.discard(video_id)
        self._guardar_audio(video_id, url)
        if video_id == self.video_actual:
            self._refrescar_info_barra()
        if self._esperando == video_id:
            self._esperando = None
            self._iniciar(video_id, url)

    def _audio_fallo(self, video_id, permanente):
        self._precargando.discard(video_id)
        esperaba = self._esperando == video_id
        if esperaba:
            self._esperando = None

        if permanente:
            # Esa canción nunca se podrá reproducir: se omite.
            self._omitir_no_disponible(video_id)
            if not esperaba and self.video_actual:
                # Era la siguiente prevista: se elige otra y se precarga.
                self._preparar_proxima()
        elif esperaba or (video_id == self.video_actual and not self._reanudando):
            self._fallo_temporal(video_id)

    def _preparar_proxima(self):
        """Decide cuál será la siguiente canción y deja su audio listo."""
        self._proxima_id = None
        i = self.elegir_siguiente(True)
        if i is None:
            return
        pista = self.cola[i]
        self._proxima_id = pista[1]
        self._precargar(pista[1])

    def _fallo_temporal(self, video_id):
        if video_id == self.video_actual:
            self.mensaje("No se pudo reproducir esta canción", 6000)

    def _omitir_no_disponible(self, video_id):
        playlist = self.playlist_sonando or self.playlist_actual
        if not playlist:
            return

        era_actual = video_id == self.video_actual
        pos = next(
            (k for k, p in enumerate(self.cola) if p[1] == video_id), 0
        )

        playlist.setdefault("no_disponibles", set()).add(video_id)

        if playlist.get("virtual"):
            # Una canción de «Mis favoritos» que no se puede reproducir también
            # se oculta en las playlists de donde viene.
            for otra in self.playlists:
                if any(p[1] == video_id for p in otra.get("pistas", [])):
                    otra.setdefault("no_disponibles", set()).add(video_id)
            if (
                self.playlist_actual is not None
                and self.playlist_actual is not playlist
            ):
                self.pistas_originales = self.pistas_disponibles_de_playlist(
                    self.playlist_actual
                )
                self.aplicar_vista()
        self.guardar_playlists()

        self.cola = [p for p in self.cola if p[1] != video_id]

        # La canción desaparece de la lista visual.
        if playlist is self.playlist_actual:
            self.pistas_originales = self.pistas_disponibles_de_playlist(playlist)
            self.aplicar_vista()

        if not era_actual:
            return

        if self._reanudando:
            # Era la canción dejada en pausa al abrir: no arrancar otra sola.
            self.detener_todo()
            return

        if not self.cola:
            self.detener_todo()
            self.mensaje("No hay canciones disponibles", 6000)
            return

        # La siguiente ocupa normalmente la misma posición.
        self.reproducir(min(pos, len(self.cola) - 1))

    def _iniciar(self, video_id, audio):
        if video_id != self.video_actual:
            return

        ms, self._inicio_ms = self._inicio_ms, 0
        media = self.instancia.media_new(audio)
        if ms > 0:
            media.add_option(f":start-time={ms / 1000:.1f}")
        self.player.set_media(media)
        self.player.play()
        self.player.audio_set_volume(int(float(self.volumen.get())))
        self.pausado = False
        self._media_id = video_id
        self._reanudando = False
        self.mensaje("", 0)
        self._refrescar_play(True)
        if ms > 0:
            self.root.after(1500, lambda: self._verificar_inicio(video_id, ms))
        self._preparar_proxima()

    # ----------------------------------------------------------
    # Estado guardado: recordar dónde te quedaste
    # ----------------------------------------------------------
    def _aplicar_estado_botones(self):
        self.btn_aleatorio.set_activo(self.aleatorio)
        self.btn_aleatorio_cab.set_activo(self.aleatorio)
        self.btn_repetir.set_icono(
            "repetir1" if self.repetir == REP_UNA else "repetir"
        )
        self.btn_repetir.set_activo(self.repetir != REP_NO)

    def _playlist_guardada(self):
        """La playlist de la última vez (o None si ya no existe)."""
        clave = self.ajustes.get("ultima_playlist")
        if clave == self.me_gusta["nombre"]:
            return self.me_gusta
        if not clave:
            return None
        for p in self.playlists:
            if (p.get("url") or p.get("nombre")) == clave:
                return p
        return None

    def _reanudar_guardada(self):
        """Deja cargada, en pausa, la canción que sonaba la última vez."""
        video_id = self.ajustes.get("ultima_cancion")
        if not video_id or self.playlist_actual is None:
            return
        if self._playlist_guardada() is not self.playlist_actual:
            return
        idx = next(
            (k for k, p in enumerate(self.pistas_vista) if p[1] == video_id),
            None
        )
        if idx is None:
            return

        self._fijar_cola()
        self.indice = idx
        titulo, video_id, artista, duracion = self.cola[idx]
        self.video_actual = video_id
        self.dur_actual = duracion
        self.info_actual = (titulo, artista)
        self.caratula_ok = False
        self.reproducidas.add(video_id)

        ms = entero_en_rango(self.ajustes.get("ultimo_ms"), 0, 0, 10 ** 9)
        # Si estaba al principio o casi al final, se empieza desde cero.
        if ms < 3000 or (duracion and ms > duracion * 1000 - 8000):
            ms = 0
        self._inicio_ms = ms
        self._reanudando = True

        self.lbl_titulo.config(text=ajustar(titulo, self.f_barra_titulo, ancho_texto_barra()))
        self.lbl_artista.config(
            text=ajustar(artista or "Artista desconocido", self.f_barra_texto, ancho_texto_barra())
        )
        self.lbl_t_act.config(text=self.formato(ms))
        if duracion:
            total_ms = int(duracion * 1000)
            self.lbl_t_tot.config(text=self.formato(total_ms))
            self.progreso.set(min(ms / total_ms, 1) * 1000)
        self.mensaje("Pulsa play para continuar", 8000)

        self._marcar_en_vista()
        self._refrescar_play(False)

        threading.Thread(
            target=self._caratula_hilo, args=(video_id,), daemon=True
        ).start()
        # El audio se resuelve por adelantado: al pulsar play suena al instante.
        self._precargar(video_id)
        self._preparar_proxima()

    def _posicion_ms(self):
        """Minuto actual de la canción (0 si no tiene sentido guardarlo)."""
        if not self.video_actual:
            return 0
        if self._media_id == self.video_actual:
            if self.player.is_playing() or self.pausado:
                ms = max(int(self.player.get_time()), 0)
            else:
                return 0
        else:
            ms = int(self._inicio_ms or 0)
        if self.dur_actual and ms > self.dur_actual * 1000 - 8000:
            return 0
        return ms

    def guardar_estado(self):
        a = self.ajustes
        a["volumen"] = int(self.volumen_guardado)
        a["aleatorio"] = bool(self.aleatorio)
        a["repetir"] = int(self.repetir)

        # Playlist, canción y minuto solo se tocan si hay una canción cargada;
        # si no, se conserva lo de la última vez.
        if self.video_actual:
            playlist = self.playlist_sonando or self.playlist_actual
            if playlist is not None:
                a["ultima_playlist"] = playlist.get("url") or playlist.get("nombre", "")
                a["ultima_cancion"] = self.video_actual
                a["ultimo_ms"] = self._posicion_ms()
        guardar_ajustes(a)

    def _guardar_pronto(self):
        """Guarda en un instante (agrupa cambios seguidos en una sola escritura)."""
        if self._guardar_job is not None:
            self.root.after_cancel(self._guardar_job)
        self._guardar_job = self.root.after(1500, self._ejecutar_guardado)

    def _ejecutar_guardado(self):
        self._guardar_job = None
        self.guardar_estado()

    def _verificar_inicio(self, video_id, ms, intentos=3):
        """Si VLC no respetó el minuto pedido, lo coloca a mano."""
        if video_id != self.video_actual or self._media_id != video_id:
            return
        t = int(self.player.get_time())
        if t < 0:
            if intentos > 1:
                self.root.after(
                    1500,
                    lambda: self._verificar_inicio(video_id, ms, intentos - 1)
                )
            return
        if t < ms - 5000:
            self.player.set_time(ms)

    def detener_todo(self):
        """Para la música y deja la barra inferior como nueva."""
        self.player.stop()
        self._media_id = None
        self._reanudando = False
        self._inicio_ms = 0
        self.dur_actual = None
        self.video_actual = None
        self.info_actual = None
        self.caratula_ok = False
        self.indice = -1
        self.cola = []
        self.pausado = False
        self.playlist_sonando = None
        self.historial.clear()
        self.reproducidas.clear()
        self._proxima_id = None
        self._esperando = None

        self.lbl_titulo.config(text="Ninguna canción")
        self.lbl_artista.config(text="")
        self._refrescar_info_barra()
        self.lbl_caratula.config(image=self.img_caratula_vacia)
        self.img_caratula = self.img_caratula_vacia
        self.lbl_t_act.config(text="0:00")
        self.lbl_t_tot.config(text="0:00")
        self.progreso.set(0)
        self.lista.marcar_sonando(None)
        self._refrescar_lateral()
        self._refrescar_play(False)

    # ==========================================================
    # CARÁTULA DE LA BARRA INFERIOR
    # ==========================================================
    def _caratula_hilo(self, video_id):
        try:
            img, _ = descargar_cuadrada(video_id, TAM_CARATULA_BARRA)
            img = redondear(img, 8)
        except Exception:
            return
        self.root.after(0, lambda: self._mostrar_caratula(video_id, img))

    def _mostrar_caratula(self, video_id, img):

        if video_id != self.video_actual:
            return

        self._caratula_pil = img
        self.img_caratula = ImageTk.PhotoImage(self._con_resplandor(img, 6))
        self.caratula_ok = True

        self.lbl_caratula.config(
            image=self.img_caratula
        )

        try:
            self._portada_para_dinamico(video_id, img)
        except Exception:
            pass

        # Actualizar automáticamente el fondo cuando
        # la portada pertenece a la canción actual.
        if (self.ajustes.get("fondo_tipo") == "portada_cancion"
                or self.ajustes.get("fondo_dinamico")):
            try:
                self._actualizar_fondo_reproductor()
            except Exception:
                pass

        # Si está activada la adaptación automática,
        # también refrescamos el fondo.
        if self.ajustes.get(
            "adaptar_colores_portada",
            False
        ):
            try:
                self._actualizar_fondo_reproductor()
            except Exception:
                pass

    # ==========================================================
    # CONTROLES
    # ==========================================================
    def _refrescar_play(self, reproduciendo=None):
        if reproduciendo is None:
            reproduciendo = bool(self.player.is_playing())

        mismo = (
            self.video_actual is not None
            and self.playlist_sonando is self.playlist_actual
        )
        estado = (reproduciendo, mismo)
        if estado == self._ultimo_play:
            return
        self._ultimo_play = estado

        self.btn_play.set_icono("pausa" if reproduciendo else "play")
        self.btn_play_cab.set_icono(
            "pausa" if (reproduciendo and mismo) else "play"
        )

    def play_cabecera(self):
        # Botón grande de la cabecera: si esta playlist ya suena,
        # pausa/continúa; si no, empieza a reproducirla.
        if self.video_actual and self.playlist_sonando is self.playlist_actual:
            self.play_pausa()
        else:
            self.iniciar_contexto(None)

    def play_pausa(self):
        if self.player.is_playing():
            self.player.pause()
            self.pausado = True
            self._refrescar_play(False)

        elif self.pausado:
            self.player.pause()
            self.pausado = False
            self._refrescar_play(True)

        elif self.cola and self.video_actual:
            # Canción cargada pero sin sonar: continúa donde se quedó.
            ms, self._inicio_ms = self._inicio_ms, 0
            self.reproducir(self.indice if self.indice >= 0 else 0, inicio_ms=ms)

        else:
            self.iniciar_contexto(None)

    def elegir_siguiente(self, auto):
        n = len(self.cola)

        if not n:
            return None

        if self.aleatorio:
            libres = [
                k for k, p in enumerate(self.cola)
                if p[1] not in self.reproducidas
            ]

            if not libres:
                if self.repetir == REP_LISTA or not auto:
                    self.reproducidas = (
                        {self.video_actual} if self.video_actual else set()
                    )
                    libres = [
                        k for k, p in enumerate(self.cola)
                        if p[1] != self.video_actual
                    ] or [max(self.indice, 0)]
                else:
                    return None

            return random.choice(libres)

        siguiente = self.indice + 1

        if siguiente >= n:
            if self.repetir == REP_LISTA or not auto:
                return 0
            return None

        return siguiente

    def siguiente(self, auto=False):
        if not self.cola:
            return

        destino = None
        if self._proxima_id:
            # La que ya se precargó (en aleatorio, la elegida al azar).
            destino = next(
                (k for k, p in enumerate(self.cola) if p[1] == self._proxima_id),
                None
            )
        if destino is None:
            destino = self.elegir_siguiente(auto)

        if destino is None:
            self.player.stop()
            self._refrescar_play(False)
            self.mensaje("Fin de la lista", 4000)
            return

        if self.video_actual:
            self.historial.append(self.video_actual)
        self.reproducir(destino)

    def anterior(self):
        if not self.cola:
            return

        if self.video_actual and self.player.get_time() > 3000:
            self.player.set_time(0)
            return

        # Busca en el historial la última canción que siga en la cola.
        while self.historial:
            video_id = self.historial.pop()
            for k, p in enumerate(self.cola):
                if p[1] == video_id:
                    self.reproducir(k)
                    return

        self.reproducir(max(self.indice, 0) - 1)

    # ==========================================================
    # VOLUMEN
    # ==========================================================
    def cambiar_volumen(self, valor):
        valor = int(float(valor))
        self.player.audio_set_volume(valor)
        self.btn_volumen.set_icono("mudo" if valor == 0 else "volumen")
        self.volumen_guardado = valor
        self._guardar_pronto()

    def alternar_mudo(self):
        actual = int(float(self.volumen.get()))
        if actual > 0:
            self.volumen_previo = actual
            nuevo = 0
        else:
            nuevo = self.volumen_previo or 70
        self.volumen.set(nuevo)
        self.cambiar_volumen(nuevo)

    def _ajustar_volumen(self, delta):
        nuevo = int(min(100, max(0, float(self.volumen.get()) + delta)))
        self.volumen.set(nuevo)
        self.cambiar_volumen(nuevo)

    # ==========================================================
    # PROGRESO
    # ==========================================================
    def vigilar(self):
        if self.player.get_state() == vlc.State.Ended:
            if self.repetir == REP_UNA:
                self.player.stop()
                self.player.play()
            else:
                self.player.stop()
                self.siguiente(auto=True)

        elif self.player.is_playing() and not self.arrastrando:
            self.progreso.set(int(self.player.get_position() * 1000))
            self.lbl_t_act.config(text=self.formato(self.player.get_time()))
            self.lbl_t_tot.config(text=self.formato(self.player.get_length()))

        self._refrescar_play()

        self._refrescar_corazon_barra()

        self._actualizar_discord()

        self._ticks += 1
        if self._ticks >= 10:
            self._ticks = 0
            if self.video_actual and self.player.is_playing():
                self.guardar_estado()

        self.root.after(500, self.vigilar)

    def saltar(self, event=None):
        self.player.set_position(float(self.progreso.get()) / 1000)
        self.arrastrando = False

    @staticmethod
    def formato(ms):
        s = max(ms, 0) // 1000
        return f"{s // 60}:{s % 60:02d}"

    # ==========================================================
    # ATAJOS DE TECLADO Y RUEDA DEL MOUSE
    # ==========================================================
    def _escribiendo(self):
        try:
            return isinstance(self.root.focus_get(), tk.Entry)
        except Exception:
            return False

    def _tecla_espacio(self, e=None):
        if not self._escribiendo():
            self.play_pausa()

    def _tecla(self, accion):
        if not self._escribiendo():
            accion()

    def _rueda_global(self, e):
        # Un solo manejador para toda la app: así no se acumulan al
        # reconstruir la interfaz (cambio de paleta).
        self.lista._rueda(e)
        self.lateral._rueda(e)
        p = getattr(self, "pantalla_apariencia", None)
        if p is not None and self.apariencia_abierta:
            p._rueda(e)

    def _clic_global(self, e):
        # Un clic fuera de un campo de texto le quita el foco, así
        # la barra espaciadora vuelve a pausar en lugar de escribir.
        try:
            if e.widget.winfo_toplevel() is not self.root:
                return
            if not isinstance(e.widget, tk.Entry):
                self.root.focus_set()
        except Exception:
            pass

    def _actualizar_discord(self):                    
        """Cuenta a Discord lo que suena (se llama desde vigilar)."""
        if not self.discord:
            return

        if not self.video_actual or self._reanudando:
            # Nada sonando, o canción dejada en pausa al abrir el programa.
            self.discord.actualizar(None)
            return
        if self._media_id != self.video_actual:
            return   # está cargando: se deja lo que ya se mostraba

        reproduciendo = bool(self.player.is_playing())
        if not reproduciendo and not self.pausado:
            self.discord.actualizar(None)   # terminó o se detuvo
            return

        titulo, artista = self.info_actual or ("", "")
        self.discord.actualizar({
            "id": self.video_actual,
            "titulo": titulo,
            "artista": artista,
            "duracion": self.dur_actual,
            "pos_ms": max(int(self.player.get_time()), 0),
            "reproduciendo": reproduciendo,
            "playlist": (self.playlist_sonando or {}).get("nombre", ""),
        }) 


        # ==========================================================
    # REVISIÓN AUTOMÁTICA DE PLAYLISTS DE YOUTUBE
    # ==========================================================
    # Cada playlist se revisa como máximo una vez cada tanto (en segundos).
    INTERVALO_REVISION = 30 * 60

    @staticmethod
    def _nuevas_canciones(actuales, de_youtube):
        """Canciones que YouTube tiene y la playlist guardada aún no."""
        conocidas = {p[1] for p in actuales}
        nuevas = []
        for p in de_youtube:
            if p[1] not in conocidas:
                conocidas.add(p[1])
                nuevas.append(p)
        return nuevas

    def _iniciar_revision_automatica(self):
        """Al abrir Otium: busca canciones nuevas en tus playlists de YouTube."""
        if not self.ajustes.get("auto_actualizar", True):
            return

        revisadas = self.ajustes.get("revision_playlists")
        if not isinstance(revisadas, dict):
            revisadas = self.ajustes["revision_playlists"] = {}
        ahora = time.time()

        pendientes = []
        for p in self.playlists:
            if not p.get("url") or p.get("propia"):
                continue   # las playlists propias no vienen de YouTube
            try:
                hace = ahora - float(revisadas.get(p["url"], 0))
            except (TypeError, ValueError):
                hace = self.INTERVALO_REVISION
            if hace < 0 or hace >= self.INTERVALO_REVISION:
                pendientes.append((p, p["url"]))

        if not pendientes:
            return
        self._rev_nuevas = 0
        self._rev_listas = []
        threading.Thread(
            target=self._revision_hilo, args=(pendientes,), daemon=True
        ).start()

    def _en_principal(self, funcion):
        """Pide a la ventana que ejecute algo (un hilo no puede tocar la interfaz)."""
        try:
            self.root.after(0, funcion)
        except Exception:
            pass   # la ventana ya se cerró

    def _revision_hilo(self, pendientes):
        fallos = 0
        for playlist, url in pendientes:
            if self._parar_revision.is_set():
                return
            try:
                _, pistas = leer_playlist(url)
            except Exception:
                fallos += 1
                if fallos >= 2:    # seguramente no hay internet: queda para la próxima
                    break
                self._parar_revision.wait(2.0)
                continue
            fallos = 0
            self._en_principal(
                lambda p=playlist, u=url, ps=pistas: self._revision_lista(p, u, ps)
            )
            self._parar_revision.wait(1.5)   # sin saturar a YouTube
        self._en_principal(self._revision_terminada)

    def _revision_lista(self, playlist, url, pistas):
        self.ajustes.setdefault("revision_playlists", {})[url] = time.time()
        if self._indice_de(playlist) is None:
            return   # la eliminaste mientras se revisaba

        nuevas = self._nuevas_canciones(playlist["pistas"], pistas)
        if not nuevas:
            return
        playlist["pistas"] = list(playlist["pistas"]) + nuevas
        self.guardar_playlists()
        self._rev_nuevas += len(nuevas)
        self._rev_listas.append(playlist["nombre"])
        if playlist is self.playlist_actual:
            self._refrescar_vista_conservando_posicion()

    def _refrescar_vista_conservando_posicion(self):
        """Actualiza la lista que se ve sin que salte al principio."""
        offset = self.lista.offset
        self.pistas_originales = self.pistas_disponibles_de_playlist(
            self.playlist_actual
        )
        self.aplicar_vista()
        self.lista.offset = offset
        self.lista._dibujar()

    def _revision_terminada(self):
        guardar_ajustes(self.ajustes)
        n = self._rev_nuevas
        if not n:
            return
        if len(self._rev_listas) == 1:
            donde = f"«{cortar(self._rev_listas[0], 28)}»"
        else:
            donde = f"{len(self._rev_listas)} playlists"
        self.mensaje(
            f"{n} canción nueva en {donde}" if n == 1
            else f"{n} canciones nuevas en {donde}",
            8000
        )

    

    def _cerrar(self):
        try:
            self.guardar_estado()
            self._parar_revision.set()
            self.player.stop()
            if self.discord:                         
                self.discord.cerrar()
            # Cancela lo que esté en cola para que el programa cierre rápido.
            # Cancela lo que esté en cola para que el programa cierre rápido.
            for pool in (self.pool_audio, self.pool, self.lista.pool):
                try:
                    pool.shutdown(wait=False, cancel_futures=True)
                except Exception:
                    pass
        finally:
            self.root.destroy()


ajustes = cargar_ajustes()
fondo_aleatorio_inicio(ajustes)
aplicar_tema(resolver_tema(nombre_tema_valido(ajustes), ajustes))

root = tk.Tk()
Reproductor(root, ajustes)
root.mainloop()