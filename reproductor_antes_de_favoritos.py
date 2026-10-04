import io
import json
import os
import random
import threading
import time
import tkinter as tk
import tkinter.font as tkfont
import urllib.request
import zlib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tkinter import colorchooser, messagebox, ttk

import vlc
import yt_dlp
from PIL import Image, ImageDraw, ImageFont, ImageTk


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
    global ACENTO, ACENTO_HOVER
    FONDO = tema["FONDO"]
    PANEL = tema["PANEL"]
    PANEL_HOVER = tema["PANEL_HOVER"]
    PISTA = tema["PISTA"]
    TEXTO = tema["TEXTO"]
    TEXTO_SUAVE = tema["TEXTO_SUAVE"]
    ACENTO = tema["ACENTO"]
    ACENTO_HOVER = tema["ACENTO_HOVER"]


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

# Si ya tenías un playlists.json junto al script, se copia una sola vez.
_ARCHIVO_ANTIGUO = Path(__file__).resolve().with_name("playlists.json")
if not ARCHIVO_PLAYLISTS.exists() and _ARCHIVO_ANTIGUO.exists():
    ARCHIVO_PLAYLISTS.write_bytes(_ARCHIVO_ANTIGUO.read_bytes())

REP_NO, REP_LISTA, REP_UNA = 0, 1, 2

# Cuánto tiempo se considera válido un enlace de audio ya resuelto
# (los enlaces de YouTube caducan a las pocas horas).
TTL_AUDIO = 2 * 3600

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
}
GLIFOS_SIMPLES = {
    "play": "▶", "pausa": "⏸",
    "anterior": "⏮", "siguiente": "⏭",
    "aleatorio": "🔀",
    "repetir": "🔁", "repetir1": "🔂",
    "volumen": "🔊", "mudo": "🔇",
    "buscar": "🔍", "reloj": "🕒",
    "mas": "⋯", "paleta": "🎨", "abajo": "▾",
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


def tema_desde_acento(acento):
    """Paleta oscura completa a partir de un solo color de acento."""
    if luminancia(acento) < 0.22:
        acento = mezclar_hex(acento, "#ffffff", 0.55)
    return {
        "FONDO": mezclar_hex(acento, "#0d0d12", 0.05),
        "PANEL": mezclar_hex(acento, "#15151c", 0.07),
        "PANEL_HOVER": mezclar_hex(acento, "#222230", 0.12),
        "PISTA": mezclar_hex(acento, "#38384d", 0.18),
        "TEXTO": "#f2f2f7",
        "TEXTO_SUAVE": "#8e8ea0",
        "ACENTO": acento,
        "ACENTO_HOVER": mezclar_hex(acento, "#ffffff", 0.78),
    }


def resolver_tema(nombre, ajustes):
    if nombre == TEMA_PERSONALIZADO and ajustes.get("acento_personalizado"):
        return tema_desde_acento(ajustes["acento_personalizado"])
    return TEMAS.get(nombre, TEMAS[TEMA_POR_DEFECTO])


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


def icono_nota(tam, color, radio=8, escala_nota=0.5, color_nota=(255, 255, 255, 235)):
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
                    (tam / 2, tam / 2), "♪", font=fuente,
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
        return ydl.extract_info(url, download=False)["url"]


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
    frame.grid_columnconfigure(4, minsize=COL_DUR)


class FilaCancion:
    """Una fila reutilizable: # | miniatura + título | artista | duración."""

    def __init__(self, padre, al_clic, f_titulo, f_texto):
        self.indice = None
        self.video_id = None
        self.numero = 0
        self.sonando = False
        self.hover = False
        self.al_clic = al_clic

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
        self.dur.grid(row=0, column=4, sticky="e", padx=(0, 16))

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

    def _entrar(self, e=None):
        self.hover = True
        self._pintar()

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

    def __init__(self, padre, al_reproducir, al_ordenar, cache=None):
        super().__init__(padre, bg=FONDO)
        self.al_reproducir = al_reproducir
        self.al_ordenar = al_ordenar
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
        self.h_dur.grid(row=0, column=4, sticky="e", padx=(0, 16))

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
                    self.f_titulo, self.f_texto
                )
            )

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
            ancho - COL_NUM - COL_MINI - COL_ARTISTA - COL_DUR - 28, 60
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

        self.cabecera = tk.Label(
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
        self.canvas.pack(fill="both", expand=True)
        self.interior = tk.Frame(self.canvas, bg=PANEL)
        self.ventana = self.canvas.create_window(
            (0, 0), window=self.interior, anchor="nw"
        )
        self.interior.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfig(self.ventana, width=e.width)
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

        # Espacio final para futuras categorías.
        tk.Frame(interior, bg=PANEL, height=8).pack(fill="x")

        canvas.bind_all("<MouseWheel>", lambda e: self._rueda_apariencia(e, canvas), add="+")
        canvas.bind_all("<Button-4>", lambda e: self._rueda_apariencia(e, canvas), add="+")
        canvas.bind_all("<Button-5>", lambda e: self._rueda_apariencia(e, canvas), add="+")

    def _rueda_apariencia(self, e, canvas):
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
        self._crear_nueva()
        self.canvas.yview_moveto(0)

    def _crear_item(self, playlist, seleccionada, sonando):
        bg = PANEL_HOVER if seleccionada else PANEL
        fila = tk.Frame(self.interior, bg=bg, height=52, cursor="hand2")
        fila.pack(fill="x", padx=10, pady=1)
        fila.pack_propagate(False)

        imagen = ImageTk.PhotoImage(
            icono_nota(36, color_playlist(playlist), 8, 0.5)
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

    def _crear_nueva(self):
        fila = tk.Frame(self.interior, bg=PANEL, height=52, cursor="hand2")
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

        self.configurar_estilos()

        self.f_barra_titulo = tkfont.Font(family=FUENTE, size=10, weight="bold")
        self.f_barra_texto = tkfont.Font(family=FUENTE, size=9)
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
        self.lateral.refrescar(
            self.playlists, self.playlist_actual, self.playlist_sonando
        )
        self._aplicar_estado_botones()
        self.player.audio_set_volume(self.volumen_guardado)

        if self.playlists:
            self.abrir_playlist(self._playlist_guardada() or self.playlists[0])
            self._reanudar_guardada()
        else:
            self.panel_vacio.tkraise()

        colorear_barra_titulo(self.root, FONDO, TEXTO)
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
        self.lateral = BarraLateral(
            self.root,
            al_abrir=self.abrir_playlist,
            al_nueva=self.nueva_playlist,
            al_menu=self.mostrar_menu,
            al_apariencia=self.dialogo_apariencia,
            al_guardar_apariencia=self.guardar_apariencia
        )
        self.lateral.grid(row=0, column=0, sticky="nsew")
        if self.apariencia_abierta:
            self.lateral.abrir_apariencia(
                self.tema_nombre, self.previsualizar_tema
            )

    def _construir_contenido(self):
        self.contenido = tk.Frame(self.root, bg=FONDO)
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
        lbl_tipo = tk.Label(
            info, text="Playlist", bg=bg, fg=TEXTO_SUAVE,
            font=(FUENTE, 9), anchor="w"
        )
        lbl_tipo.pack(fill="x")
        self.lbl_nombre = tk.Label(
            info, text="", bg=bg, fg=TEXTO,
            font=(FUENTE, 26, "bold"), anchor="w"
        )
        self.lbl_nombre.pack(fill="x")
        self.lbl_resumen = tk.Label(
            info, text="", bg=bg, fg=TEXTO_SUAVE,
            font=(FUENTE, 9), anchor="w"
        )
        self.lbl_resumen.pack(fill="x")

        acciones = tk.Frame(self.cab, bg=bg)
        acciones.grid(
            row=1, column=0, columnspan=2, sticky="ew", padx=24, pady=(0, 14)
        )
        self.btn_play_cab = BotonCircular(
            acciones, 52, bg, ACENTO, ACENTO_HOVER, color_sobre(ACENTO),
            self.play_cabecera, tam_icono=18
        )
        self.btn_play_cab.pack(side="left")
        self.btn_aleatorio_cab = BotonIcono(
            acciones, "aleatorio", self.alternar_aleatorio, tam=16, fondo=bg
        )
        self.btn_aleatorio_cab.pack(side="left", padx=(12, 0))
        self.btn_mas = BotonIcono(
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
            cache=self.cache_miniaturas
        )
        self.lista.pack(fill="both", expand=True, padx=(16, 8), pady=(0, 8))

    def _construir_barra(self):
        barra = tk.Frame(self.root, bg=PANEL, height=ALTO_BARRA)
        self.barra = barra
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
        self.lbl_caratula = tk.Label(
            izq, image=self.img_caratula, bg=PANEL, bd=0
        )
        self.lbl_caratula.pack(side="left")
        textos = tk.Frame(izq, bg=PANEL)
        textos.pack(side="left", padx=(12, 0))
        self.lbl_titulo = tk.Label(
            textos, text="Ninguna canción", bg=PANEL, fg=TEXTO,
            font=self.f_barra_titulo, anchor="w"
        )
        self.lbl_titulo.pack(fill="x")
        self.lbl_artista = tk.Label(
            textos, text="", bg=PANEL, fg=TEXTO_SUAVE,
            font=self.f_barra_texto, anchor="w"
        )
        self.lbl_artista.pack(fill="x")
        self.estado = tk.Label(
            textos, text="", bg=PANEL, fg=ACENTO_HOVER,
            font=(FUENTE, 8), anchor="w"
        )
        self.estado.pack(fill="x")

        # --- Centro: controles + progreso ---
        centro = tk.Frame(barra, bg=PANEL)
        centro.grid(row=0, column=1, sticky="nsew", pady=(10, 8))

        controles = tk.Frame(centro, bg=PANEL)
        controles.pack(pady=(0, 2))
        self.btn_aleatorio = BotonIcono(
            controles, "aleatorio", self.alternar_aleatorio, tam=14, fondo=PANEL
        )
        self.btn_aleatorio.pack(side="left", padx=6)
        BotonIcono(
            controles, "anterior", self.anterior, tam=16,
            fondo=PANEL, color=TEXTO
        ).pack(side="left", padx=6)
        self.btn_play = BotonCircular(
            controles, 40, PANEL, TEXTO, mezclar_hex(TEXTO, FONDO, 0.82),
            FONDO, self.play_pausa, tam_icono=14
        )
        self.btn_play.pack(side="left", padx=8)
        BotonIcono(
            controles, "siguiente", self.siguiente, tam=16,
            fondo=PANEL, color=TEXTO
        ).pack(side="left", padx=6)
        self.btn_repetir = BotonIcono(
            controles, "repetir", self.alternar_repetir, tam=14, fondo=PANEL
        )
        self.btn_repetir.pack(side="left", padx=6)

        fila = tk.Frame(centro, bg=PANEL)
        fila.pack(fill="x", padx=8)
        self.lbl_t_act = tk.Label(
            fila, text="0:00", width=5, anchor="e",
            bg=PANEL, fg=TEXTO_SUAVE, font=(FUENTE, 9)
        )
        self.lbl_t_act.pack(side="left")
        self.lbl_t_tot = tk.Label(
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
        self.btn_volumen = BotonIcono(
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
        color = ACENTO if acento else PANEL
        hover = ACENTO_HOVER if acento else PANEL_HOVER
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

        # Los widgets anteriores ya no sirven con los colores nuevos.
        for nombre in ("lateral", "contenido", "barra"):
            widget = getattr(self, nombre, None)
            if widget is not None:
                try:
                    widget.destroy()
                except tk.TclError:
                    pass

        # Regenerar imágenes y estilos que dependen de la paleta.
        self.configurar_estilos()
        self._crear_imagenes_tema()

        self._construir_lateral()
        self._construir_contenido()
        self._construir_barra()

        # Si estábamos dentro de Apariencia, mantener el panel abierto
        # después de cambiar de paleta.
        if self.apariencia_abierta:
            self.lateral.abrir_apariencia(
                self.tema_nombre, self.previsualizar_tema
            )

        # Restaurar la playlist que estaba abierta.
        if playlist is not None:
            self.abrir_playlist(playlist)
            self.orden_col = orden_col
            self.orden_desc = orden_desc
            if busqueda:
                self.pildora.poner_texto(busqueda)
            else:
                self.pildora.vaciar()
            self.aplicar_vista()
        else:
            self.panel_vacio.tkraise()

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
                text=ajustar(titulo, self.f_barra_titulo, 190)
            )
            self.lbl_artista.config(
                text=ajustar(artista or "Artista desconocido", self.f_barra_texto, 190)
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

    def dialogo_apariencia(self, pos=None):
        """Abre Apariencia dentro de la barra lateral, sin ventana aparte."""
        self.apariencia_abierta = True
        self.lateral.abrir_apariencia(
            self.tema_nombre, self.previsualizar_tema
        )

    def previsualizar_tema(self, nombre):
        """Aplica una paleta inmediatamente, pero todavía no la guarda."""
        if nombre not in TEMAS or nombre == self.tema_nombre:
            return
        tema = resolver_tema(nombre, self.ajustes)
        self.tema_nombre = nombre
        aplicar_tema(tema)
        self._reconstruir()

    def guardar_apariencia(self):
        """Confirma la paleta actual y vuelve a mostrar las playlists."""
        self.ajustes["tema"] = self.tema_nombre
        guardar_ajustes(self.ajustes)
        self.apariencia_abierta = False
        self.lateral.cerrar_apariencia()
        self._refrescar_lateral()
        colorear_barra_titulo(self.root, FONDO, TEXTO)

    # ==========================================================
    # CABECERA: COLOR Y PORTADA
    # ==========================================================
    def _tintar(self, color):
        self.color_cab = color
        for w in self._tintables:
            w.config(bg=color)
        self._dibujar_degradado()

    def _dibujar_degradado(self):
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
        self.img_portada = ImageTk.PhotoImage(portada)
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
                    "no_disponibles": no_disponibles
                })
        except Exception:
            self.playlists = []

    def guardar_playlists(self):
        datos = []

        for p in self.playlists:
            datos.append({
                "nombre": p["nombre"],
                "url": p["url"],
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

    def _indice_de(self, playlist):
        """Posición de la playlist en la lista (compara por identidad)."""
        for i, p in enumerate(self.playlists):
            if p is playlist:
                return i
        return None

    def pistas_disponibles_de_playlist(self, playlist):
        no_disp = playlist.get("no_disponibles", set())
        return [
            pista for pista in playlist.get("pistas", [])
            if pista[1] not in no_disp
        ]

    def _refrescar_lateral(self):
        self.lateral.refrescar(
            self.playlists, self.playlist_actual, self.playlist_sonando
        )

    # ==========================================================
    # ABRIR / CREAR / EDITAR PLAYLISTS
    # ==========================================================
    def abrir_playlist(self, playlist):
        """Muestra una playlist SIN interrumpir la música que suena."""
        if playlist is None:
            return

        self.playlist_actual = playlist
        self.pistas_originales = self.pistas_disponibles_de_playlist(playlist)
        self.orden_col = None
        self.orden_desc = False
        self.pildora.vaciar()

        self.lbl_nombre.config(text=cortar(playlist["nombre"], 30))
        self.panel_lista.tkraise()
        self._poner_portada_inicial(playlist)
        self.aplicar_vista()
        self._refrescar_lateral()
        self._refrescar_play()

    def nueva_playlist(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Nueva playlist")
        ventana.configure(bg=FONDO)
        ventana.resizable(False, False)
        ventana.transient(self.root)
        ventana.grab_set()

        tk.Label(
            ventana, text="Pega el link de la playlist de YouTube",
            bg=FONDO, fg=TEXTO, font=(FUENTE, 10, "bold"), anchor="w"
        ).pack(fill="x", padx=22, pady=(20, 8))

        entrada = tk.Entry(
            ventana, width=54, bg=PANEL, fg=TEXTO, insertbackground=TEXTO,
            relief="flat", font=(FUENTE, 10), highlightthickness=1,
            highlightbackground=PANEL, highlightcolor=ACENTO
        )
        entrada.pack(padx=22, ipady=7)

        lbl_estado = tk.Label(
            ventana, text="", bg=FONDO, fg=TEXTO_SUAVE,
            font=(FUENTE, 9), anchor="w"
        )
        lbl_estado.pack(fill="x", padx=22, pady=(8, 0))

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

        botones = tk.Frame(ventana, bg=FONDO)
        botones.pack(pady=14)
        self.boton(botones, "Cancelar", ventana.destroy, ancho=10).pack(
            side="left", padx=4
        )
        self.boton(botones, "Añadir", aceptar, ancho=10, acento=True).pack(
            side="left", padx=4
        )

        entrada.focus_set()
        ventana.bind("<Return>", lambda e: aceptar())
        ventana.bind("<Escape>", lambda e: ventana.destroy())

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

    def mostrar_menu(self, playlist, x, y):
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
        ventana = tk.Toplevel(self.root)
        ventana.title("Renombrar playlist")
        ventana.configure(bg=FONDO)
        ventana.resizable(False, False)
        ventana.transient(self.root)
        ventana.grab_set()

        tk.Label(
            ventana, text="Nuevo nombre:", bg=FONDO, fg=TEXTO,
            font=(FUENTE, 10, "bold")
        ).pack(padx=22, pady=(18, 6), anchor="w")

        entrada = tk.Entry(
            ventana, width=40, bg=PANEL, fg=TEXTO, insertbackground=TEXTO,
            relief="flat", font=(FUENTE, 10)
        )
        entrada.pack(padx=22, fill="x", ipady=6)
        entrada.insert(0, playlist["nombre"])
        entrada.select_range(0, "end")

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

        self.boton(
            ventana, "Guardar", guardar, ancho=10, acento=True
        ).pack(pady=14)

        entrada.focus_set()
        ventana.bind("<Return>", lambda e: guardar())
        ventana.bind("<Escape>", lambda e: ventana.destroy())

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

        self.lbl_titulo.config(text=ajustar(titulo, self.f_barra_titulo, 190))
        self.lbl_artista.config(
            text=ajustar(artista or "Artista desconocido", self.f_barra_texto, 190)
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

        self.lbl_titulo.config(text=ajustar(titulo, self.f_barra_titulo, 190))
        self.lbl_artista.config(
            text=ajustar(artista or "Artista desconocido", self.f_barra_texto, 190)
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
        self.img_caratula = ImageTk.PhotoImage(img)
        self.caratula_ok = True
        self.lbl_caratula.config(image=self.img_caratula)

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

    def _cerrar(self):
        try:
            self.guardar_estado()
            self.player.stop()
            # Cancela lo que esté en cola para que el programa cierre rápido.
            for pool in (self.pool_audio, self.pool, self.lista.pool):
                try:
                    pool.shutdown(wait=False, cancel_futures=True)
                except Exception:
                    pass
        finally:
            self.root.destroy()


ajustes = cargar_ajustes()
aplicar_tema(resolver_tema(nombre_tema_valido(ajustes), ajustes))

root = tk.Tk()
Reproductor(root, ajustes)
root.mainloop()