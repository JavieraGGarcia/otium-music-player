"""
Etapa 2 de Apariencia: FONDO en la cabecera, la barra lateral y la barra
inferior. Arregla y completa lo que ya empezaste en tu código.

Qué estaba fallando en tu versión
  - «Color de fondo» llamaba a _elegir_fondo_color, que no existía.
  - Cada clic reconstruía toda la ventana DOS veces y borraba el fondo que
    acababa de dibujar (cambiar_personalizado tenía el cuerpo duplicado).
  - El fondo se ponía detrás de los paneles, que son opacos, así que
    nunca se veía.
  - Elegir un fondo cambiaba además la paleta a «Personalizado».
  - Las cajas de Fondo/Efectos pasaban mal los argumentos a _caja.
  - Vidrio, adaptar colores y resplandor solo guardaban el ajuste.

Qué hace ahora
  - Ninguno / Color / Imagen / Portada de la canción / Portada de la playlist.
  - Transparencia, difuminado, Fondo dinámico (sigue la portada de la canción
    que suena) y Efecto vidrio.
  - Se ve en la cabecera, la barra lateral y la barra inferior. La lista de
    canciones y las filas de playlists quedan sólidas.
  - Los controles de Apariencia aplican sin reconstruir la pantalla; los
    deslizadores se aplican al soltar/pausar el arrastre.
  - «Adaptar colores a la portada» y «Resplandor de portada» pasan a la lista
    de «próximamente» (no estaban implementados).

Uso (en la carpeta de reproductor.py):
    python aplicar_fondo.py
Se crea una copia: reproductor_antes_de_fondo.py
"""
import re
import sys
from pathlib import Path

ARCHIVO = Path(sys.argv[1] if len(sys.argv) > 1 else "reproductor.py")


def error(msg):
    raise SystemExit(
        "\nNo se cambió nada.\n" + msg +
        "\nPásale este mensaje a Claude para ajustarlo."
    )


# ==========================================================================
# 1) FUNCIONES SUELTAS (antes de class Reproductor)
# ==========================================================================
AYUDAS = '''# ==============================================================
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
                   transparencia, vidrio, base):
    """Imagen final del tamaño de la ventana: recorte tipo «cubrir»,
    difuminado, vidrio y mezcla con el color del tema."""
    if tipo == "color":
        return Image.new("RGB", (ancho, alto), color)

    difuminado = max(0, min(100, int(difuminado)))
    t = max(0, min(100, int(transparencia))) / 100
    img = src.convert("RGB")
    iw, ih = img.size

    # Con difuminado se trabaja a media resolución (más rápido).
    s = 1.0 if (difuminado == 0 and not vidrio) else 0.5
    w2, h2 = max(1, int(ancho * s)), max(1, int(alto * s))
    esc = max(w2 / iw, h2 / ih)
    nw, nh = max(1, round(iw * esc)), max(1, round(ih * esc))
    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
    izq, arr = (nw - w2) // 2, (nh - h2) // 2
    img = img.crop((izq, arr, izq + w2, arr + h2))

    radio = difuminado / 100 * 60 * s + (10 * s if vidrio else 0)
    if radio > 0:
        img = img.filter(ImageFilter.GaussianBlur(radio))
    if s != 1.0:
        img = img.resize((ancho, alto), Image.Resampling.BICUBIC)
    if vidrio:
        img = Image.blend(img, Image.new("RGB", img.size, "#ffffff"), 0.08)
    if t > 0:
        img = Image.blend(img, Image.new("RGB", img.size, base), t)
    return img


'''

# ==========================================================================
# 2) MÉTODOS DE REPRODUCTOR: motor del fondo + cambiar_personalizado
#    (reemplaza desde cambiar_personalizado hasta restablecer_apariencia)
# ==========================================================================
CAMBIAR = '''    def cambiar_personalizado(
            self, acento=None, modo=None, intensidad=None,
            botones_propios=None, color_botones=None,
            fondo_tipo=None, fondo_imagen=None, fondo_color=None,
            fondo_transparencia=None, fondo_difuminado=None,
            fondo_dinamico=None, cambio_fondo_cancion=None,
            adaptar_colores_portada=None, efecto_vidrio=None,
            resplandor_portada=None
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
        if acento or modo or intensidad is not None:
            self.tema_nombre = TEMA_PERSONALIZADO

        # --- Fondo y efectos (no cambian la paleta) ---
        antes_activo = a.get("fondo_tipo", "ninguno") != "ninguno"
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
        ):
            if valor is not None:
                a[clave] = conv(valor)
                hubo_fondo = True
        ahora_activo = a.get("fondo_tipo", "ninguno") != "ninguno"

        if tema_cambia or (antes_activo and not ahora_activo):
            # Reconstruye (y _reconstruir vuelve a pintar el fondo).
            self._aplicar_tema_actual()
        elif hubo_fondo:
            self._fondo_reaplicar(0)

    def programar_fondo(self, **cambios):
        """Para los deslizadores: guarda el valor y pinta cuando el
        arrastre hace una pausa (sin reconstruir nada)."""
        for clave, valor in cambios.items():
            self.ajustes[clave] = int(float(valor))
        self._fondo_reaplicar(160)

'''

MOTOR = '''    # ==========================================================
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
        if self.ajustes.get("fondo_tipo", "ninguno") == "ninguno":
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
        if a.get("fondo_dinamico") and self.video_actual:
            tipo = "portada_cancion"

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

    def _aplicar_fondo_interno(self):
        a = self.ajustes
        if a.get("fondo_tipo", "ninguno") == "ninguno":
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
        llave = (clave, ancho, alto, transp, dif, vidrio, color, FONDO)
        previo = getattr(self, "_fondo_comp_cache", None)
        if previo is not None and previo[0] == llave:
            comp = previo[1]
        else:
            comp = componer_fondo(
                src, ancho, alto,
                "color" if clave == "color" else "imagen",
                color, dif, transp, vidrio, FONDO
            )
            self._fondo_comp_cache = (llave, comp)
        self._fondo_comp = comp
        self._fondo_vivo = True

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
            propia = getattr(w, "_fondo_foto", None) is not None
            if str(w.cget("image")) and not propia:
                # Portada / carátula: solo se ajusta el marco.
                w.config(bg=medio)
            elif (
                str(w.cget("anchor")) == "center" and ww <= 120 and hh <= 60
            ):
                foto = ImageTk.PhotoImage(recorte)
                w.config(
                    image=foto, compound="center", padx=0, pady=0, bg=medio
                )
                w._fondo_foto = foto
            else:
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

'''

# ==========================================================================
# 3) PANTALLA DE APARIENCIA: paneles Fondo y Efectos + manejadores
# ==========================================================================
PANELES = '''    def _panel_fondo_reproductor(self, padre=None):
        """Opciones de fondo del reproductor."""
        a = self.app.ajustes
        caja = self._caja(
            "Fondo",
            "Se ve en la cabecera, la barra lateral y la barra inferior."
        )

        self._var_fondo = tk.StringVar(value=a.get("fondo_tipo", "ninguno"))
        opciones = [
            ("Ninguno", "ninguno"),
            ("Color", "color"),
            ("Imagen personalizada", "imagen"),
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
        muestra.bind("<Button-1>", lambda e: self._elegir_fondo_color(muestra))

        # --- Imagen ---
        fila_img = tk.Frame(caja, bg=PANEL)
        fila_img.pack(fill="x", padx=14, pady=(6, 4))
        tk.Button(
            fila_img, text="Elegir imagen...", command=self._elegir_imagen_fondo,
            bg=PANEL_HOVER, fg=TEXTO, activebackground=ACENTO,
            activeforeground=color_sobre(ACENTO), relief="flat", bd=0,
            font=(FUENTE, 9), cursor="hand2", padx=10, pady=4
        ).pack(side="left")
        ruta = a.get("fondo_imagen", "")
        tk.Label(
            fila_img, text=os.path.basename(ruta) if ruta else "Ninguna",
            bg=PANEL, fg=TEXTO_SUAVE, font=(FUENTE, 8), anchor="w"
        ).pack(side="left", padx=10)

        # --- Transparencia ---
        self._escala_fondo(
            caja, "Transparencia", "fondo_transparencia",
            "Transparente", "Opaco", FONDO_TRANSP_DEF
        )
        tk.Frame(caja, bg=PANEL, height=6).pack()

    def _panel_efectos_reproductor(self, padre=None):
        """Efectos visuales del fondo."""
        caja = self._caja("Efectos", "Se aplican sobre el fondo elegido.")
        self._escala_fondo(
            caja, "Difuminado", "fondo_difuminado",
            "Nítido", "Muy difuminado", 0
        )
        self._crear_interruptor(
            caja, "Fondo dinámico",
            "Sigue la portada de la canción que suena",
            "fondo_dinamico"
        )
        self._crear_interruptor(
            caja, "Efecto vidrio",
            "Suaviza y aclara un poco el fondo",
            "efecto_vidrio"
        )
        tk.Frame(caja, bg=PANEL, height=6).pack()

    def _escala_fondo(self, caja, titulo, clave, izq, der, defecto):
        """Deslizador que guarda su valor al moverlo y pinta al hacer una
        pausa (sin reconstruir la pantalla)."""
        tk.Label(
            caja, text=titulo, bg=PANEL, fg=TEXTO,
            font=(FUENTE, 9, "bold"), anchor="w"
        ).pack(fill="x", padx=14, pady=(8, 2))
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
            lbl.config(text=f"{int(v)}%")
            self.app.programar_fondo(**{clave: v})

        Slider(
            fila, 0, 100, valor, ancho=160, fondo=PANEL, al_mover=mover
        ).pack(side="left", fill="x", expand=True, padx=8)

'''

MANEJADORES = '''    def _cambiar_fondo_tipo(self, tipo):
        if tipo == "imagen" and not self.app.ajustes.get("fondo_imagen"):
            self._elegir_imagen_fondo()
            return
        self.app.cambiar_personalizado(fondo_tipo=tipo)

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

'''

PROXIMAMENTE = '''    def _panel_proximamente(self):

        caja = self._caja(
            "Próximamente",
            "Estas opciones llegarán en una próxima etapa."
        )

        for texto in (
            "Adaptar colores a la portada",
            "Resplandor de portada",
            "Mostrar nombres y portada en los controles",
        ):
            fila = tk.Frame(caja, bg=PANEL)
            fila.pack(fill="x", padx=16, pady=3)
            tk.Label(
                fila, text="○", bg=PANEL, fg=PANEL_HOVER, font=(FUENTE, 12)
            ).pack(side="left")
            tk.Label(
                fila, text=texto, bg=PANEL, fg=TEXTO_SUAVE, font=(FUENTE, 9)
            ).pack(side="left", padx=8)
        tk.Frame(caja, bg=PANEL, height=8).pack()

'''


# ==========================================================================
def pos_unica(texto, ancla, etiqueta=None):
    n = texto.count(ancla)
    if n != 1:
        error(
            f"No encontré con claridad (apariciones: {n}) este punto de tu "
            f"código:\n    {(etiqueta or ancla).strip()!r}"
        )
    return texto.index(ancla)


def region(texto, inicio, fin, nuevo):
    i = pos_unica(texto, inicio)
    j = pos_unica(texto, fin)
    if j < i:
        error(f"Orden inesperado entre {inicio.strip()!r} y {fin.strip()!r}.")
    return texto[:i] + nuevo + texto[j:]


def reemplazar(texto, viejo, nuevo):
    pos_unica(texto, viejo)
    return texto.replace(viejo, nuevo, 1)


def aplicar(t):
    # 1) Funciones sueltas antes de la clase Reproductor.
    banner = "# ==============================================================\n# REPRODUCTOR\n"
    if t.count(banner) == 1:
        t = reemplazar(t, banner, AYUDAS + banner)
    else:
        t = reemplazar(t, "class Reproductor:\n", AYUDAS + "class Reproductor:\n")

    # 2) cambiar_personalizado (con la cola duplicada) + restablecer intacto.
    t = region(
        t, "    def cambiar_personalizado(\n",
        "    def restablecer_apariencia(self):\n", CAMBIAR
    )

    # 3) Motor antiguo del fondo -> motor nuevo.
    t = region(
        t, "    def _obtener_imagen_fondo(self):\n",
        "    def cancelar_apariencia(self):\n", MOTOR
    )

    # 4) Paneles de Fondo y Efectos.
    t = region(
        t, "    def _panel_fondo_reproductor(self, padre):\n",
        "    def _crear_interruptor(\n", PANELES
    )
    t = region(
        t, "    def _cambiar_fondo_tipo(self, tipo):\n",
        "    # ==========================================================\n"
        "    # CONSTRUCCIÓN PRINCIPAL\n", MANEJADORES + "\n"
    )

    # 5) «Próximamente» solo con lo pendiente, y el orden de los paneles.
    t = region(
        t, "    def _panel_proximamente(self):\n",
        "    # ==========================================================\n"
        "    # SELECTOR COLOR PRINCIPAL\n", PROXIMAMENTE
    )
    patron = re.compile(
        r"self\._panel_proximamente\(\)\s*"
        r"self\._panel_fondo_reproductor\(self\.cuerpo\)\s*"
        r"self\._panel_efectos_reproductor\(self\.cuerpo\)"
    )
    if len(patron.findall(t)) != 1:
        error("No encontré el bloque que arma los paneles de Apariencia.")
    t = patron.sub(
        "self._panel_fondo_reproductor()\n\n"
        "        self._panel_efectos_reproductor()\n\n"
        "        self._panel_proximamente()", t
    )

    # 6) Transparencia por defecto (0 dejaba el texto ilegible sobre fotos).
    t = reemplazar(t, '"fondo_transparencia": 0,', '"fondo_transparencia": FONDO_TRANSP_DEF,')
    t = reemplazar(
        t, 'setdefault("fondo_transparencia", 0)',
        'setdefault("fondo_transparencia", FONDO_TRANSP_DEF)'
    )

    # 7) Enganches en el resto de la app.
    t = reemplazar(
        t, "    def _tintar(self, color):\n        self.color_cab = color\n"
        "        for w in self._tintables:\n            w.config(bg=color)\n"
        "        self._dibujar_degradado()\n",
        "    def _tintar(self, color):\n        self.color_cab = color\n"
        "        for w in self._tintables:\n            w.config(bg=color)\n"
        "        self._dibujar_degradado()\n"
        "        self._fondo_reaplicar()   # la tinta de la portada no tapa el fondo\n"
    )
    t = reemplazar(
        t, "    def _dibujar_degradado(self):\n        c = self.canvas_deg\n",
        "    def _dibujar_degradado(self):\n"
        "        if self._pintar_degradado_fondo():\n            return\n"
        "        c = self.canvas_deg\n"
    )
    t = reemplazar(
        t, "    def _refrescar_lateral(self):\n        self.lateral.refrescar(\n"
        "            [self.me_gusta] + self.playlists,\n"
        "            self.playlist_actual, self.playlist_sonando\n        )\n",
        "    def _refrescar_lateral(self):\n        self.lateral.refrescar(\n"
        "            [self.me_gusta] + self.playlists,\n"
        "            self.playlist_actual, self.playlist_sonando\n        )\n"
        "        self._fondo_reaplicar(30)\n"
    )
    t = reemplazar(
        t, "        # Los widgets anteriores ya no sirven con los colores nuevos.\n",
        "        self._fondo_vivo = False\n"
        "        # Los widgets anteriores ya no sirven con los colores nuevos.\n"
    )
    t = reemplazar(
        t, "        self._refrescar_play(reproduciendo)\n"
        "        colorear_barra_titulo(self.root, FONDO, TEXTO)\n",
        "        self._refrescar_play(reproduciendo)\n"
        "        colorear_barra_titulo(self.root, FONDO, TEXTO)\n"
        "        self._fondo_reaplicar(80)\n"
    )
    t = reemplazar(
        t, "        barra = tk.Frame(self.root, bg=PANEL, height=ALTO_BARRA)\n",
        "        self._fondo_enganchar()\n"
        "        barra = tk.Frame(self.root, bg=PANEL, height=ALTO_BARRA)\n"
    )
    t = reemplazar(
        t, 'if self.ajustes.get("fondo_tipo") == "portada_cancion":',
        'if (self.ajustes.get("fondo_tipo") == "portada_cancion"\n'
        '                or self.ajustes.get("fondo_dinamico")):'
    )
    return t


def main():
    if not ARCHIVO.exists():
        raise SystemExit(f"No encuentro {ARCHIVO}. Ejecútalo dentro de la carpeta de tu proyecto.")

    crudo = ARCHIVO.read_bytes().decode("utf-8")
    crlf = "\r\n" in crudo
    texto = crudo.replace("\r\n", "\n")

    if "def _aplicar_fondo(self" in texto:
        raise SystemExit("El fondo ya estaba aplicado. No se cambió nada.")
    if "class PantallaApariencia" not in texto or "def _panel_fondo_reproductor" not in texto:
        error("Este script es para el código que ya tiene la pantalla de "
              "Apariencia con las opciones de Fondo que añadiste.")

    nuevo = aplicar(texto)
    compile(nuevo, str(ARCHIVO), "exec")   # comprueba que no quedó con errores

    copia = ARCHIVO.with_name("reproductor_antes_de_fondo.py")
    copia.write_bytes(crudo.encode("utf-8"))
    if crlf:
        nuevo = nuevo.replace("\n", "\r\n")
    ARCHIVO.write_bytes(nuevo.encode("utf-8"))
    print("Listo. El fondo de Apariencia quedó funcionando (etapa 2).")
    print(f"Copia de seguridad: {copia.name}")


if __name__ == "__main__":
    main()
