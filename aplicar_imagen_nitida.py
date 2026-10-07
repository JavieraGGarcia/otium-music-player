"""
Imagen personalizada: ahora puedes elegir entre dos estilos.

  - Nítida:       se ve la imagen tal cual (puedes difuminar o aclarar con los
                  deslizadores).
  - Transparente: fondo suave, mezclado con la paleta (lo de la versión
                  anterior).

Para que la imagen nítida se vea limpia, cuando usas Imagen o Portada como
fondo el texto y los iconos de la cabecera, la barra lateral y la barra
inferior se dibujan directamente sobre la imagen (antes cada texto tenía su
propio rectángulo de color). Con «Ninguno» y «Color» todo sigue exactamente
igual que antes.

Requiere aplicar_imagen_paleta.py primero.

Uso (en la carpeta de reproductor.py):
    python aplicar_imagen_nitida.py
Se crea una copia: reproductor_antes_de_imagen_nitida.py
"""
import sys
from pathlib import Path

ARCHIVO = Path(sys.argv[1] if len(sys.argv) > 1 else "reproductor.py")


def error(msg):
    raise SystemExit(
        "\nNo se cambió nada.\n" + msg +
        "\nPásale este mensaje a Claude para ajustarlo."
    )


NUEVO_BLOQUE = '''def componer_fondo(src, ancho, alto, tipo, color, difuminado,
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
TIPOS_LIENZO = ("imagen", "portada_cancion", "portada_playlist")
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


'''

PANEL_ESTILO = '''        # --- Estilo de la imagen ---
        self._var_estilo = tk.StringVar(
            value=a.get("fondo_estilo", "transparente")
        )
        fila_est = tk.Frame(caja, bg=PANEL)
        fila_est.pack(fill="x", padx=14, pady=(8, 0))
        tk.Label(
            fila_est, text="Estilo de la imagen", bg=PANEL, fg=TEXTO,
            font=(FUENTE, 9, "bold")
        ).pack(side="left")
        for texto, valor in (("Transparente", "transparente"), ("Nítida", "nitida")):
            tk.Radiobutton(
                fila_est, text=texto, value=valor, variable=self._var_estilo,
                bg=PANEL, fg=TEXTO, selectcolor=PANEL_HOVER,
                activebackground=PANEL, activeforeground=TEXTO,
                font=(FUENTE, 9), highlightthickness=0, bd=0, cursor="hand2",
                command=lambda v=valor: self.app.cambiar_estilo_fondo(v)
            ).pack(side="right", padx=(8, 0))

'''

METODO_ESTILO = '''    def cambiar_estilo_fondo(self, estilo):
        self.ajustes["fondo_estilo"] = estilo
        self._fondo_reaplicar(0)

'''

# (viejo, nuevo): cada «viejo» debe aparecer exactamente una vez.
CAMBIOS = [
    ('        # --- Transparencia ---\n'
     '        self._escala_fondo(\n'
     '            caja, "Transparencia", "fondo_transparencia",\n',
     PANEL_ESTILO +
     '        # --- Transparencia ---\n'
     '        self._escala_fondo(\n'
     '            caja, "Transparencia", "fondo_transparencia",\n'),
    ('"Suave", "Muy difuminado", 0', '"Poco", "Mucho", 0'),
    ('    def programar_fondo(self, **cambios):\n',
     METODO_ESTILO + '    def programar_fondo(self, **cambios):\n'),
    ('        llave = (clave, ancho, alto, transp, dif, vidrio, color, FONDO)\n',
     '        estilo = a.get("fondo_estilo", "transparente")\n'
     '        llave = (clave, ancho, alto, transp, dif, vidrio, color, FONDO, estilo)\n'),
    ('                color, dif, transp, vidrio, FONDO\n            )\n',
     '                color, dif, transp, vidrio, FONDO, estilo\n            )\n'),
    ('    "fondo_paleta_imagen",\n',
     '    "fondo_paleta_imagen",\n    "fondo_estilo",\n'),
    # reconstruir cuando se entra o se sale del modo «lienzo»
    ('        antes_color = firma_paleta_fondo(a)\n',
     '        antes_color = firma_paleta_fondo(a)\n'
     '        antes_lienzo = a.get("fondo_tipo") in TIPOS_LIENZO\n'),
    ('        if tema_cambia or cambia_paleta_color or (antes_activo and not ahora_activo):\n',
     '        cambia_lienzo = antes_lienzo != (a.get("fondo_tipo") in TIPOS_LIENZO)\n'
     '        if (tema_cambia or cambia_paleta_color or cambia_lienzo\n'
     '                or (antes_activo and not ahora_activo)):\n'),
    # los ajustes los lee el constructor de widgets
    ('    def _construir_lateral(self):\n        self.lateral = BarraLateral(\n',
     '    def _construir_lateral(self):\n'
     '        globals()["AJUSTES_REF"] = self.ajustes\n'
     '        self.lateral = BarraLateral(\n'),
    # textos de la barra lateral, cabecera y barra inferior
    ('        self.cabecera = tk.Label(\n            self, text="Mis playlists"',
     '        self.cabecera = etiqueta(\n            self, text="Mis playlists"'),
    ('        lbl_tipo = tk.Label(\n            info,', '        lbl_tipo = etiqueta(\n            info,'),
    ('        self.lbl_nombre = tk.Label(\n            info,', '        self.lbl_nombre = etiqueta(\n            info,'),
    ('        self.lbl_resumen = tk.Label(\n            info,', '        self.lbl_resumen = etiqueta(\n            info,'),
    ('        self.lbl_titulo = tk.Label(\n            textos,', '        self.lbl_titulo = etiqueta(\n            textos,'),
    ('        self.lbl_artista = tk.Label(\n            textos,', '        self.lbl_artista = etiqueta(\n            textos,'),
    ('        self.estado = tk.Label(\n            textos,', '        self.estado = etiqueta(\n            textos,'),
    ('        self.lbl_t_act = tk.Label(\n            fila,', '        self.lbl_t_act = etiqueta(\n            fila,'),
    ('        self.lbl_t_tot = tk.Label(\n            fila,', '        self.lbl_t_tot = etiqueta(\n            fila,'),
    ('        tk.Label(\n            controles, text=glifo("corazon"), font=(FUENTE_ICO, 14),\n',
     '        etiqueta(\n            controles, text=glifo("corazon"), font=(FUENTE_ICO, 14),\n'),
]


def main():
    if not ARCHIVO.exists():
        raise SystemExit(f"No encuentro {ARCHIVO}. Ejecútalo dentro de la carpeta de tu proyecto.")
    crudo = ARCHIVO.read_bytes().decode("utf-8")
    crlf = "\r\n" in crudo
    texto = crudo.replace("\r\n", "\n")

    if "class EtiquetaLienzo(" in texto:
        raise SystemExit("La imagen nítida ya estaba aplicada. No se cambió nada.")
    if "def paleta_desde_imagen(" not in texto:
        error("Primero hay que aplicar aplicar_imagen_paleta.py.")

    # 1) componer_fondo nuevo + clases de lienzo (antes del banner REPRODUCTOR)
    ini = "def componer_fondo(src, ancho, alto, tipo, color, difuminado,\n"
    fin = "# ==============================================================\n# REPRODUCTOR\n"
    if texto.count(ini) != 1 or texto.count(fin) != 1:
        error("No encontré con claridad la función componer_fondo.")
    i, j = texto.index(ini), texto.index(fin)
    if j < i:
        error("Orden inesperado alrededor de componer_fondo.")
    texto = texto[:i] + NUEVO_BLOQUE + texto[j:]

    # 2) cambios puntuales
    for viejo, nuevo in CAMBIOS:
        n = texto.count(viejo)
        if n != 1:
            error(f"No encontré con claridad (apariciones: {n}) este punto de tu código:\n    {viejo.strip()[:90]!r}")
        texto = texto.replace(viejo, nuevo, 1)

    # 3) iconos de cabecera y barra inferior
    a = texto.index("    def _construir_contenido(self):\n")
    b = texto.index("    def configurar_estilos(self):\n")
    if b < a:
        error("Orden inesperado entre _construir_contenido y configurar_estilos.")
    tramo = texto[a:b]
    n = tramo.count("BotonIcono(")
    if n < 6:
        error(f"Esperaba al menos 6 BotonIcono en la cabecera y la barra (hay {n}).")
    texto = texto[:a] + tramo.replace("BotonIcono(", "boton_icono(") + texto[b:]

    compile(texto, str(ARCHIVO), "exec")
    copia = ARCHIVO.with_name("reproductor_antes_de_imagen_nitida.py")
    copia.write_bytes(crudo.encode("utf-8"))
    if crlf:
        texto = texto.replace("\n", "\r\n")
    ARCHIVO.write_bytes(texto.encode("utf-8"))
    print("Listo. Ya puedes elegir imagen Nítida o Transparente.")
    print(f"Copia de seguridad: {copia.name}")


if __name__ == "__main__":
    main()
