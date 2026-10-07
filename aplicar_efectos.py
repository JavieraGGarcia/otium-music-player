"""
PASO 4: efectos (Apariencia > Efectos).

  - RESPLANDOR DE PORTADA: un halo del color de la portada alrededor de la
    carátula (la de la barra inferior y la grande de la cabecera). Tiene una
    barra de Intensidad.
  - BRILLO AMBIENTAL: una luz suave del color de la canción que sube desde
    los bordes de la ventana. También tiene Intensidad. Funciona sin fondo,
    con imagen o con portada (con fondo de color no se ve).
  - ANIMACIÓN SUAVE DEL FONDO: cuando el fondo cambia (otra canción, otra
    imagen) se funde con el anterior en vez de saltar. En equipos lentos
    se salta la animación sola.

Las barras de intensidad aparecen justo debajo de su interruptor y se van
al apagarlo. El efecto vidrio sigue donde estaba.

Requiere aplicar_colores_dinamicos.py primero.

Uso (en la carpeta de reproductor.py):
    python aplicar_efectos.py
Se crea una copia: reproductor_antes_de_efectos.py
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


def entre(texto, ini, fin, nuevo, nombre):
    if texto.count(ini) != 1 or texto.count(fin) != 1:
        error(f"No encontré con claridad el bloque «{nombre}».")
    i, j = texto.index(ini), texto.index(fin)
    if j < i:
        error(f"Orden inesperado en el bloque «{nombre}».")
    return texto[:i] + nuevo + texto[j:]


MODULO = r'''def con_resplandor(img, pad, color, fuerza):
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


'''

METODOS = r'''    # ==========================================================
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

'''

PANEL_NUEVO = r'''    def _panel_efectos_reproductor(self, padre=None):
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

'''


COMP_VIEJO = """        llave = (clave, ancho, alto, transp, dif, vidrio, color, FONDO, estilo)
        previo = getattr(self, "_fondo_comp_cache", None)
        if previo is not None and previo[0] == llave:
            comp = previo[1]
        else:
            comp = componer_fondo(
                src, ancho, alto,
                "color" if clave == "color" else "imagen",
                color, dif, transp, vidrio, FONDO, estilo
            )
            self._fondo_comp_cache = (llave, comp)
        self._fondo_comp = comp
        self._fondo_vivo = True

        ox, oy = root.winfo_rootx(), root.winfo_rooty()
"""

COMP_NUEVO = """        brillo = bool(a.get("brillo_ambiental"))
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
"""


def main():
    if not ARCHIVO.exists():
        raise SystemExit(f"No encuentro {ARCHIVO}. Ejecútalo dentro de la carpeta de tu proyecto.")
    crudo = ARCHIVO.read_bytes().decode("utf-8")
    crlf = "\r\n" in crudo
    texto = crudo.replace("\r\n", "\n")

    if "def con_resplandor(" in texto:
        raise SystemExit("Los efectos ya estaban aplicados. No se cambió nada.")
    if "def cambiar_dinamico(" not in texto:
        error("Primero hay que aplicar aplicar_colores_dinamicos.py.")

    # 1) Funciones de imagen
    texto = unico(texto, "def acento_legible(tema, c):\n",
                  "def acento_legible(tema, c):\n", "acento_legible")
    marca = "# ==============================================================\n# REPRODUCTOR\n"
    texto = unico(texto, marca, MODULO + marca, "clase Reproductor")

    # 2) Tipo de fondo «ambiente» (solo brillo, sin imagen)
    texto = unico(
        texto,
        'TIPOS_LIENZO = ("imagen", "portada_cancion", "portada_playlist")\n',
        'TIPOS_LIENZO = ("imagen", "portada_cancion", "portada_playlist",\n'
        '                "ambiente")\n',
        "TIPOS_LIENZO")
    texto = unico(
        texto,
        '        if tipo == "imagen":\n            ruta = a.get("fondo_imagen", "")\n',
        '        if tipo == "ambiente":\n'
        '            return (("ambiente", FONDO), Image.new("RGB", (64, 64), FONDO))\n\n'
        '        if tipo == "imagen":\n            ruta = a.get("fondo_imagen", "")\n',
        "fondo ambiente")

    # 3) Ajustes nuevos
    texto = unico(
        texto,
        "            fondo_dinamico_origen=None, color_interfaz=None,\n"
        "            modo_ambiente=None\n        ):",
        "            fondo_dinamico_origen=None, color_interfaz=None,\n"
        "            modo_ambiente=None, brillo_ambiental=None,\n"
        "            fondo_animacion=None\n        ):",
        "firma de cambiar_personalizado")
    texto = unico(
        texto,
        '            ("modo_ambiente", modo_ambiente, bool),\n',
        '            ("modo_ambiente", modo_ambiente, bool),\n'
        '            ("brillo_ambiental", brillo_ambiental, bool),\n'
        '            ("fondo_animacion", fondo_animacion, bool),\n',
        "lista de ajustes")
    texto = unico(
        texto,
        '        ahora_activo = a.get("fondo_tipo", "ninguno") != "ninguno"\n',
        '        if a.get("brillo_ambiental") and a.get("fondo_tipo", "ninguno") == "ninguno":\n'
        '            a["fondo_tipo"] = "ambiente"      # solo brillo, sin imagen\n'
        '        elif not a.get("brillo_ambiental") and a.get("fondo_tipo") == "ambiente":\n'
        '            a["fondo_tipo"] = "ninguno"\n'
        '        ahora_activo = a.get("fondo_tipo", "ninguno") != "ninguno"\n',
        "tipo ambiente")
    texto = unico(
        texto,
        '    "fondo_dinamico_origen",\n]\n',
        '    "fondo_dinamico_origen",\n    "resplandor_intensidad",\n'
        '    "brillo_ambiental",\n    "brillo_intensidad",\n'
        '    "fondo_animacion",\n]\n',
        "CLAVES_APARIENCIA")

    # 4) Métodos del Reproductor
    texto = unico(texto, "    def cambiar_estilo_fondo(self, estilo):\n",
                  METODOS + "    def cambiar_estilo_fondo(self, estilo):\n",
                  "cambiar_estilo_fondo")
    texto = unico(texto, COMP_VIEJO, COMP_NUEVO, "composición del fondo")

    # 5) Carátulas con resplandor
    texto = unico(
        texto,
        "        self.img_caratula = ImageTk.PhotoImage(img)\n        self.caratula_ok = True\n",
        "        self._caratula_pil = img\n"
        "        self.img_caratula = ImageTk.PhotoImage(self._con_resplandor(img, 6))\n"
        "        self.caratula_ok = True\n",
        "carátula de la barra")
    texto = unico(
        texto,
        "        self.img_portada = ImageTk.PhotoImage(portada)\n"
        "        self.portada.config(image=self.img_portada)\n"
        "        self._tintar(tinte(color))\n",
        "        self._portada_base = (playlist, portada)\n"
        "        self.img_portada = ImageTk.PhotoImage(self._con_resplandor(portada, 14))\n"
        "        self.portada.config(image=self.img_portada)\n"
        "        self._tintar(tinte(color))\n",
        "portada de la cabecera")
    texto = unico(
        texto,
        "        self._fondo_reaplicar(80)\n\n    CLAVES_APARIENCIA",
        "        self._refrescar_resplandor()\n"
        "        self._fondo_reaplicar(80)\n\n    CLAVES_APARIENCIA",
        "reconstruir")

    # 6) Pantalla de Apariencia
    texto = entre(
        texto, "    def _panel_efectos_reproductor(self, padre=None):\n",
        "    def _fila_interruptor(self, caja, titulo, descripcion, valor,\n",
        PANEL_NUEVO, "panel de efectos")
    texto = unico(
        texto,
        '            self._panel_efectos_reproductor()\n\n            self._panel_proximamente(\n                (\n'
        '                    "Resplandor de portada",\n'
        '                    "Brillo ambiental",\n'
        '                    "Animación suave del fondo",\n                )\n            )\n',
        '            self._panel_efectos_reproductor()\n',
        "sección Efectos")
    texto = unico(
        texto,
        '        self._var_fondo = tk.StringVar(value=a.get("fondo_tipo", "ninguno"))\n',
        '        tipo_radio = a.get("fondo_tipo", "ninguno")\n'
        '        if tipo_radio == "ambiente":\n'
        '            tipo_radio = "ninguno"\n'
        '        self._var_fondo = tk.StringVar(value=tipo_radio)\n',
        "radios de fondo")
    texto = unico(
        texto,
        '            if self.app.ajustes.get("fondo_tipo") in TIPOS_LIENZO:\n',
        '            if (self.app.ajustes.get("fondo_tipo") in TIPOS_LIENZO\n'
        '                    and self.app.ajustes.get("fondo_tipo") != "ambiente"):\n',
        "barras de Fondos")

    compile(texto, str(ARCHIVO), "exec")
    copia = ARCHIVO.with_name("reproductor_antes_de_efectos.py")
    copia.write_bytes(crudo.encode("utf-8"))
    if crlf:
        texto = texto.replace("\n", "\r\n")
    ARCHIVO.write_bytes(texto.encode("utf-8"))
    print("Listo. Apariencia > Efectos: resplandor de portada, brillo ambiental y animación del fondo.")
    print(f"Copia de seguridad: {copia.name}")


if __name__ == "__main__":
    main()
