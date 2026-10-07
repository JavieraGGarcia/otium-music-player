"""
PASO 2: fondos por defecto, Mis fondos y fondo aleatorio.

En Apariencia > Fondos aparecen tres bloques nuevos (arriba de las opciones
que ya tenías):

  - Fondos por defecto: Nocturno, Atardecer, Bosque, Ciudad, Cielo
    estrellado, Auroras, Montañas, Mar y Luna. Los dibuja Otium con código
    (no hay que descargar nada). Al elegir uno funciona como una imagen
    personalizada: toda la interfaz adapta sus colores y puedes ajustar
    Nitidez y Transparencia.
  - Mis fondos: tu biblioteca de imágenes. «Añadir imagen» copia las que
    elijas (puedes elegir varias) a la carpeta de datos de Otium
    (%APPDATA%\\Otium\\fondos\\mis). La ✕ de cada miniatura la quita de la
    biblioteca (no borra tu archivo original).
  - Fondo aleatorio: el botón «Sorprenderme» elige uno al azar (por
    defecto o tuyo) y el interruptor «Cambiar al abrir Otium» pone uno
    distinto cada vez que inicias la app.

Requiere aplicar_base_apariencia.py primero.

Uso (en la carpeta de reproductor.py):
    python aplicar_fondos_defecto.py
Se crea una copia: reproductor_antes_de_fondos_defecto.py
"""
import sys
from pathlib import Path

ARCHIVO = Path(sys.argv[1] if len(sys.argv) > 1 else "reproductor.py")


def error(msg):
    raise SystemExit(
        "\nNo se cambió nada.\n" + msg +
        "\nPásale este mensaje a Claude para ajustarlo."
    )


def unico(texto, viejo, nuevo, nombre):
    n = texto.count(viejo)
    if n != 1:
        error(f"No encontré con claridad (apariciones: {n}) este punto de tu código ({nombre}):\n    {viejo.strip()[:90]!r}")
    return texto.replace(viejo, nuevo, 1)


MODULO = r'''# ==============================================================
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


'''

CLASE = r'''    # ==========================================================
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

'''


METODO_APP = '''    def fondo_al_azar(self):
        # Pone un fondo al azar (por defecto o de Mis fondos).
        ruta = elegir_fondo_aleatorio(self.ajustes)
        if ruta:
            self.cambiar_personalizado(
                fondo_tipo="imagen", fondo_imagen=ruta
            )

'''


def main():
    if not ARCHIVO.exists():
        raise SystemExit(f"No encuentro {ARCHIVO}. Ejecútalo dentro de la carpeta de tu proyecto.")
    crudo = ARCHIVO.read_bytes().decode("utf-8")
    crlf = "\r\n" in crudo
    texto = crudo.replace("\r\n", "\n")

    if "def generar_fondo(" in texto:
        raise SystemExit("Los fondos por defecto ya estaban aplicados. No se cambió nada.")
    if "def _crear_menu(" not in texto:
        error("Primero hay que aplicar aplicar_base_apariencia.py.")

    # 1) Funciones de fondos (antes de la clase Reproductor)
    marca = "# ==============================================================\n# REPRODUCTOR\n"
    texto = unico(texto, marca, MODULO + "\n" + marca, "clase Reproductor")

    # 2) Pantalla de Apariencia: sección Fondos
    texto = unico(
        texto,
        "            self._panel_fondo_reproductor()\n\n        elif clave == \"efectos\":\n",
        "            self._panel_fondos_defecto()\n\n"
        "            self._panel_mis_fondos()\n\n"
        "            self._panel_aleatorio()\n\n"
        "            self._panel_fondo_reproductor()\n\n        elif clave == \"efectos\":\n",
        "sección Fondos")
    texto = unico(
        texto,
        "    # ==========================================================\n    # MENÚ LATERAL DE SECCIONES\n",
        CLASE + "    # ==========================================================\n    # MENÚ LATERAL DE SECCIONES\n",
        "menú lateral")

    # 3) Ajuste nuevo
    texto = unico(
        texto,
        "            resplandor_portada=None\n        ):",
        "            resplandor_portada=None, fondo_aleatorio=None\n        ):",
        "firma de cambiar_personalizado")
    texto = unico(
        texto,
        "            (\"resplandor_portada\", resplandor_portada, bool),\n",
        "            (\"resplandor_portada\", resplandor_portada, bool),\n"
        "            (\"fondo_aleatorio\", fondo_aleatorio, bool),\n",
        "lista de ajustes de fondo")
    texto = unico(
        texto,
        "    \"resplandor_portada\",\n]\n",
        "    \"resplandor_portada\",\n    \"fondo_aleatorio\",\n]\n",
        "CLAVES_APARIENCIA")
    texto = unico(
        texto,
        "    def cambiar_estilo_fondo(self, estilo):\n",
        METODO_APP + "    def cambiar_estilo_fondo(self, estilo):\n",
        "cambiar_estilo_fondo")

    # 4) Al iniciar la app
    texto = unico(
        texto,
        "ajustes = cargar_ajustes()\n",
        "ajustes = cargar_ajustes()\nfondo_aleatorio_inicio(ajustes)\n",
        "inicio de la app")

    compile(texto, str(ARCHIVO), "exec")
    copia = ARCHIVO.with_name("reproductor_antes_de_fondos_defecto.py")
    copia.write_bytes(crudo.encode("utf-8"))
    if crlf:
        texto = texto.replace("\n", "\r\n")
    ARCHIVO.write_bytes(texto.encode("utf-8"))
    print("Listo. Apariencia > Fondos tiene fondos por defecto, Mis fondos y fondo aleatorio.")
    print(f"Copia de seguridad: {copia.name}")


if __name__ == "__main__":
    main()
