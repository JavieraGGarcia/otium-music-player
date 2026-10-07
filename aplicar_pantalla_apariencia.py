"""
ETAPA 1 de la nueva Apariencia: pantalla propia en el área principal.

Qué agrega (según la maqueta):
  - Al pulsar «Apariencia» (abajo en la barra lateral) se abre una pantalla en
    el área principal, con flecha para volver, título y dos pestañas:
        · Paletas: cuadrícula de paletas con una vista previa dibujada de cada
          una (Oscuras, Claras y tu Personalizada). Un clic la aplica en vivo.
        · Personalizado: color principal (con selector de color), Intensidad
          (Suave ↔ Intenso), modo Oscuro/Claro y Color de los botones
          (interruptor «Usar color principal» o un color propio).
  - Restablecer (vuelve a los valores por defecto) y Guardar (confirma).
    La flecha de volver descarta lo que no hayas guardado.
  - El color de los botones se aplica al botón de play grande y a los botones
    de acción de los cuadros (Añadir, Crear, Guardar...).
  - Si abres otra playlist mientras estás en Apariencia, se sale de ella
    descartando lo no guardado.

La barra lateral queda normal (ya no se transforma en el panel de paletas).

Requisitos: tener aplicados corregir_paletas.py y aplicar_modo_claro.py.

Uso (en la carpeta de reproductor.py):
    python aplicar_pantalla_apariencia.py
Se crea una copia: reproductor_antes_de_pantalla_apariencia.py
"""
import sys
from pathlib import Path

ARCHIVO = Path(sys.argv[1] if len(sys.argv) > 1 else "reproductor.py")


# ======================================================================
# 1) Temas: botón propio, intensidad
# ======================================================================
APLICAR_TEMA = '''def aplicar_tema(tema):
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


'''

TEMA_NUEVO = '''def tema_desde_acento(acento, claro=False, intensidad=50):
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


def resolver_tema(nombre, ajustes):
    if nombre == TEMA_PERSONALIZADO and ajustes.get("acento_personalizado"):
        tema = tema_desde_acento(
            ajustes["acento_personalizado"],
            claro=ajustes.get("modo_personalizado") == "claro",
            intensidad=ajustes.get("intensidad_personalizado", 50)
        )
    else:
        tema = dict(TEMAS.get(nombre, TEMAS[TEMA_POR_DEFECTO]))

    # Color propio para los botones (vale para cualquier paleta).
    if ajustes.get("botones_propios") and ajustes.get("color_botones"):
        c = ajustes["color_botones"]
        tema["ACENTO_BOTON"] = c
        tema["ACENTO_BOTON_HOVER"] = mezclar_hex(
            c, "#ffffff", 0.82 if luminancia(tema["FONDO"]) > 0.5 else 0.78
        )
    return tema


'''

# ======================================================================
# 2) Clases nuevas: Interruptor y PantallaApariencia
# ======================================================================
CLASES = '''def rect_redondeado(lienzo, x1, y1, x2, y2, r, **opciones):
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
    """Pantalla de Apariencia en el área principal: pestañas Paletas y
    Personalizado, con vista previa en vivo."""

    NOMBRES_OSCURAS = (
        "Morado nocturno", "Océano", "Esmeralda", "Atardecer",
        "Rosa neón", "Carmesí", "AMOLED"
    )
    NOMBRES_CLARAS = (
        "Blanco limpio", "Gris elegante", "Beige cálido", "Lavanda suave",
        "Azul hielo", "Verde salvia", "Rosa empolvado"
    )
    ANCHO_T, ALTO_T = 150, 92

    def __init__(self, padre, app):
        super().__init__(padre, bg=FONDO)
        self.app = app
        self._scroll_inicial = getattr(app, "_scroll_apariencia", 0.0)
        self._listo = False
        self._grupos = []
        self._columnas = 0
        self._construir()

    # ------------------------------------------------------------ armado
    def _construir(self):
        app = self.app
        cab = tk.Frame(self, bg=FONDO)
        cab.pack(fill="x", padx=(20, 28), pady=(20, 0))
        BotonIcono(
            cab, "atras", app.cancelar_apariencia, tam=14, fondo=FONDO
        ).pack(side="left", padx=(0, 6))
        tk.Label(
            cab, text="Apariencia", bg=FONDO, fg=TEXTO,
            font=(FUENTE, 18, "bold")
        ).pack(side="left")
        tk.Label(
            self, text="Elige una paleta o personaliza tu propia apariencia.",
            bg=FONDO, fg=TEXTO_SUAVE, font=(FUENTE, 10), anchor="w"
        ).pack(fill="x", padx=28, pady=(2, 12))

        fila_tabs = tk.Frame(self, bg=FONDO)
        fila_tabs.pack(fill="x", padx=28, pady=(0, 8))
        self._tabs = {}
        for clave, texto in (("paletas", "Paletas"),
                             ("personalizado", "Personalizado")):
            t = tk.Label(
                fila_tabs, text=texto, font=(FUENTE, 10, "bold"),
                padx=18, pady=6, cursor="hand2"
            )
            t.pack(side="left", padx=(0, 8))
            t.bind("<Button-1>", lambda e, c=clave: self.mostrar_pestana(c))
            self._tabs[clave] = t

        # Pie con Restablecer / Guardar (va antes del cuerpo para reservar
        # su espacio abajo).
        pie = tk.Frame(self, bg=PANEL)
        pie.pack(side="bottom", fill="x")
        tk.Frame(pie, bg=PANEL_HOVER, height=1).pack(fill="x")
        botones = tk.Frame(pie, bg=PANEL)
        botones.pack(fill="x", padx=28, pady=12)
        app.boton(
            botones, "Guardar", app.guardar_apariencia, ancho=12, acento=True
        ).pack(side="right")
        app.boton(
            botones, "Restablecer", app.restablecer_apariencia, ancho=12
        ).pack(side="right", padx=(0, 10))

        marco = tk.Frame(self, bg=FONDO)
        marco.pack(fill="both", expand=True, padx=(28, 10))
        self.canvas = tk.Canvas(
            marco, bg=FONDO, highlightthickness=0, bd=0
        )
        barra = ttk.Scrollbar(
            marco, orient="vertical", command=self.canvas.yview,
            style="Musica.Vertical.TScrollbar"
        )
        barra.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.configure(
            yscrollcommand=lambda a, b: (barra.set(a, b), self._anotar(a))
        )
        self.cuerpo = tk.Frame(self.canvas, bg=FONDO)
        self._ventana = self.canvas.create_window(
            (0, 0), window=self.cuerpo, anchor="nw"
        )
        self.cuerpo.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        self.canvas.bind("<Configure>", self._al_redimensionar)

        self.mostrar_pestana(getattr(app, "_pestana_apariencia", "paletas"))
        self.after(60, self._restaurar_scroll)

    def _anotar(self, a):
        if self._listo:
            try:
                self.app._scroll_apariencia = float(a)
            except (TypeError, ValueError):
                pass

    def _restaurar_scroll(self):
        try:
            self.canvas.yview_moveto(self._scroll_inicial)
        except tk.TclError:
            return
        self._listo = True

    def _al_redimensionar(self, e):
        self.canvas.itemconfig(self._ventana, width=e.width)
        columnas = max(2, e.width // (self.ANCHO_T + 14))
        if columnas != self._columnas:
            self._columnas = columnas
            self._organizar()

    def _rueda(self, e):
        try:
            sobre = self.winfo_containing(e.x_root, e.y_root)
        except Exception:
            return
        if sobre is None or not str(sobre).startswith(str(self)):
            return
        if self.cuerpo.winfo_height() <= self.canvas.winfo_height():
            return
        if e.num == 4:
            self.canvas.yview_scroll(-2, "units")
        elif e.num == 5:
            self.canvas.yview_scroll(2, "units")
        else:
            self.canvas.yview_scroll(int(-e.delta / 120) * 2, "units")

    # ---------------------------------------------------------- pestañas
    def mostrar_pestana(self, clave):
        self.app._pestana_apariencia = clave
        for k, t in self._tabs.items():
            if k == clave:
                t.config(bg=mezclar_hex(ACENTO, FONDO, 0.35), fg=TEXTO)
            else:
                t.config(bg=PANEL, fg=TEXTO_SUAVE)
        for w in self.cuerpo.winfo_children():
            w.destroy()
        self._grupos = []
        if clave == "paletas":
            self._cuerpo_paletas()
        else:
            self._cuerpo_personalizado()
        self.canvas.yview_moveto(0)

    # ------------------------------------------------------------ paletas
    def _cuerpo_paletas(self):
        oscuras = [n for n in self.NOMBRES_OSCURAS if n in TEMAS]
        claras = [n for n in self.NOMBRES_CLARAS if n in TEMAS]
        for titulo, nombres in (("Oscuras", oscuras), ("Claras", claras),
                                ("Tu paleta", [TEMA_PERSONALIZADO])):
            tk.Label(
                self.cuerpo, text=titulo, bg=FONDO, fg=TEXTO,
                font=(FUENTE, 11, "bold"), anchor="w"
            ).pack(fill="x", pady=(8, 4))
            rejilla = tk.Frame(self.cuerpo, bg=FONDO)
            rejilla.pack(fill="x", anchor="w")
            tarjetas = [self._tarjeta(rejilla, n) for n in nombres]
            self._grupos.append((rejilla, tarjetas))
        self._organizar()

    def _organizar(self):
        columnas = max(self._columnas, 2)
        for rejilla, tarjetas in self._grupos:
            for i, t in enumerate(tarjetas):
                t.grid(
                    row=i // columnas, column=i % columnas,
                    padx=(0, 12), pady=6, sticky="n"
                )

    def _tema_de(self, nombre):
        if nombre == TEMA_PERSONALIZADO:
            if self.app.ajustes.get("acento_personalizado"):
                return resolver_tema(nombre, self.app.ajustes)
            return None
        return TEMAS[nombre]

    def _tarjeta(self, padre, nombre):
        tema = self._tema_de(nombre)
        sel = (nombre == self.app.tema_nombre)
        marco = tk.Frame(padre, bg=FONDO, cursor="hand2")
        lienzo = tk.Canvas(
            marco, width=self.ANCHO_T, height=self.ALTO_T, bg=FONDO,
            highlightthickness=0, bd=0, cursor="hand2"
        )
        lienzo.pack()
        self._dibujar_tarjeta(lienzo, tema, sel)
        etiqueta = tk.Label(
            marco, text=nombre, bg=FONDO,
            fg=TEXTO if sel else TEXTO_SUAVE,
            font=(FUENTE, 9, "bold" if sel else "normal"), cursor="hand2"
        )
        etiqueta.pack(pady=(4, 0))
        if nombre == TEMA_PERSONALIZADO:
            accion = lambda e: (
                self.mostrar_pestana("personalizado")
                if tema is None else self.app.elegir_paleta(nombre)
            )
        else:
            accion = lambda e, n=nombre: self.app.elegir_paleta(n)
        for w in (marco, lienzo, etiqueta):
            w.bind("<Button-1>", accion)
        return marco

    def _dibujar_tarjeta(self, c, tema, sel):
        w, h = self.ANCHO_T, self.ALTO_T
        if tema is None:
            # Aún no hay paleta personalizada: un recuadro con «+».
            rect_redondeado(
                c, 2, 2, w - 2, h - 2, 10, fill=PANEL, outline=PISTA, width=1
            )
            c.create_text(
                w // 2, h // 2, text="+", fill=TEXTO_SUAVE,
                font=(FUENTE, 26)
            )
            return
        rect_redondeado(
            c, 2, 2, w - 2, h - 2, 10, fill=tema["FONDO"],
            outline=tema["ACENTO"] if sel else tema["PISTA"],
            width=3 if sel else 1
        )
        # barra lateral
        rect_redondeado(c, 9, 9, 40, h - 9, 6, fill=tema["PANEL"], outline="")
        # cabecera teñida con el acento
        rect_redondeado(
            c, 47, 9, w - 9, 38, 6,
            fill=mezclar_hex(tema["ACENTO"], tema["FONDO"], 0.30), outline=""
        )
        for k, col in enumerate(
            (tema["ACENTO"], tema["ACENTO_HOVER"], tema["TEXTO"])
        ):
            c.create_oval(
                54 + k * 13, 18, 63 + k * 13, 27, fill=col, outline=""
            )
        # filas de canciones
        for i in range(3):
            y = 47 + i * 9
            c.create_line(
                52, y, 52 + 70 - i * 14, y, width=3, capstyle="round",
                fill=tema["TEXTO_SUAVE"]
            )
        # barra de reproducción
        rect_redondeado(
            c, 47, h - 25, w - 9, h - 9, 6, fill=tema["PANEL"], outline=""
        )
        c.create_oval(
            w // 2 + 4, h - 22, w // 2 + 16, h - 12,
            fill=tema.get("ACENTO_BOTON", tema["ACENTO"]), outline=""
        )

    # ------------------------------------------------------ personalizado
    def _caja(self, titulo):
        caja = tk.Frame(
            self.cuerpo, bg=PANEL,
            highlightthickness=1, highlightbackground=PANEL_HOVER
        )
        caja.pack(fill="x", pady=(8, 4))
        tk.Label(
            caja, text=titulo, bg=PANEL, fg=TEXTO,
            font=(FUENTE, 11, "bold"), anchor="w"
        ).pack(fill="x", padx=16, pady=(12, 8))
        return caja

    def _circulo(self, padre, color, comando=None):
        c = tk.Canvas(
            padre, width=38, height=38, bg=PANEL, highlightthickness=0,
            bd=0, cursor="hand2" if comando else ""
        )
        c.create_oval(3, 3, 35, 35, fill=color, outline=PISTA, width=2)
        if comando:
            c.bind("<Button-1>", lambda e: comando())
        return c

    def _pedir_color(self, titulo, inicial):
        _, elegido = colorchooser.askcolor(
            color=inicial, title=titulo, parent=self.winfo_toplevel()
        )
        return elegido

    def _cuerpo_personalizado(self):
        app = self.app
        a = app.ajustes
        acento = a.get("acento_personalizado") or ACENTO

        # ---- Color del reproductor
        caja = self._caja("Color del reproductor")
        fila = tk.Frame(caja, bg=PANEL)
        fila.pack(fill="x", padx=16, pady=(0, 8))
        self._circulo(fila, acento, self._elegir_principal).pack(side="left")
        textos = tk.Frame(fila, bg=PANEL)
        textos.pack(side="left", padx=12)
        tk.Label(
            textos, text="Color principal", bg=PANEL, fg=TEXTO,
            font=(FUENTE, 10, "bold"), anchor="w"
        ).pack(fill="x")
        tk.Label(
            textos, text=acento.upper(), bg=PANEL, fg=TEXTO_SUAVE,
            font=(FUENTE, 9), anchor="w"
        ).pack(fill="x")

        der = tk.Frame(fila, bg=PANEL)
        der.pack(side="right", fill="x", expand=True, padx=(30, 0))
        cab_int = tk.Frame(der, bg=PANEL)
        cab_int.pack(fill="x")
        tk.Label(
            cab_int, text="Intensidad", bg=PANEL, fg=TEXTO,
            font=(FUENTE, 9), anchor="w"
        ).pack(side="left")
        valor = int(a.get("intensidad_personalizado", 50))
        lbl_int = tk.Label(
            cab_int, text=f"{valor}%", bg=PANEL, fg=TEXTO_SUAVE,
            font=(FUENTE, 9)
        )
        lbl_int.pack(side="right")
        slider = Slider(
            der, 0, 100, valor=valor, ancho=200, fondo=PANEL,
            al_mover=lambda v: lbl_int.config(text=f"{int(v)}%"),
            al_soltar=lambda: app.cambiar_personalizado(
                intensidad=round(slider.get())
            )
        )
        slider.pack(fill="x")
        ext = tk.Frame(der, bg=PANEL)
        ext.pack(fill="x")
        tk.Label(
            ext, text="Suave", bg=PANEL, fg=TEXTO_SUAVE, font=(FUENTE, 8)
        ).pack(side="left")
        tk.Label(
            ext, text="Intenso", bg=PANEL, fg=TEXTO_SUAVE, font=(FUENTE, 8)
        ).pack(side="right")

        # modo Oscuro / Claro
        fila_modo = tk.Frame(caja, bg=PANEL)
        fila_modo.pack(fill="x", padx=16, pady=(4, 14))
        tk.Label(
            fila_modo, text="Modo", bg=PANEL, fg=TEXTO,
            font=(FUENTE, 9), anchor="w"
        ).pack(side="left", padx=(0, 12))
        modo_actual = a.get("modo_personalizado", "oscuro")
        for texto, clave in (("Oscuro", "oscuro"), ("Claro", "claro")):
            activo = (
                clave == modo_actual
                and app.tema_nombre == TEMA_PERSONALIZADO
            )
            e = tk.Label(
                fila_modo, text=texto,
                bg=ACENTO_BOTON if activo else PANEL_HOVER,
                fg=color_sobre(ACENTO_BOTON) if activo else TEXTO,
                font=(FUENTE, 8, "bold"), padx=12, pady=4, cursor="hand2"
            )
            e.pack(side="left", padx=(0, 6))
            e.bind(
                "<Button-1>",
                lambda ev, m=clave: app.cambiar_personalizado(modo=m)
            )

        # ---- Color de los botones
        caja2 = self._caja("Color de los botones")
        fila2 = tk.Frame(caja2, bg=PANEL)
        fila2.pack(fill="x", padx=16, pady=(0, 14))
        propios = bool(a.get("botones_propios"))
        color_b = a.get("color_botones") or acento
        self._circulo(
            fila2, color_b if propios else acento,
            self._elegir_botones if propios else None
        ).pack(side="left")
        textos2 = tk.Frame(fila2, bg=PANEL)
        textos2.pack(side="left", padx=12)
        tk.Label(
            textos2, text="Usar color principal", bg=PANEL, fg=TEXTO,
            font=(FUENTE, 10, "bold"), anchor="w"
        ).pack(fill="x")
        tk.Label(
            textos2,
            text=("Los botones usan el color principal." if not propios
                  else "Pulsa el círculo para elegir otro color."),
            bg=PANEL, fg=TEXTO_SUAVE, font=(FUENTE, 9), anchor="w"
        ).pack(fill="x")
        Interruptor(
            fila2, valor=not propios,
            al_cambiar=lambda v: app.cambiar_personalizado(
                botones_propios=not v
            )
        ).pack(side="right")

    def _elegir_principal(self):
        inicial = self.app.ajustes.get("acento_personalizado") or ACENTO
        elegido = self._pedir_color("Elige tu color principal", inicial)
        if elegido:
            self.app.cambiar_personalizado(acento=elegido)

    def _elegir_botones(self):
        a = self.app.ajustes
        inicial = a.get("color_botones") or a.get("acento_personalizado") or ACENTO
        elegido = self._pedir_color("Elige el color de los botones", inicial)
        if elegido:
            self.app.cambiar_personalizado(color_botones=elegido)


'''

BANNER_REPRODUCTOR = (
    "# ==============================================================\n"
    "# REPRODUCTOR\n"
    "# ==============================================================\n"
    "class Reproductor:\n"
)

# ======================================================================
# 3) Métodos del Reproductor
# ======================================================================
METODOS = '''    CLAVES_APARIENCIA = (
        "tema", "acento_personalizado", "modo_personalizado",
        "intensidad_personalizado", "botones_propios", "color_botones"
    )

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
        self.tema_nombre = nombre
        self._aplicar_tema_actual()

    def previsualizar_tema(self, nombre):
        self.elegir_paleta(nombre)

    def cambiar_personalizado(
        self, acento=None, modo=None, intensidad=None,
        botones_propios=None, color_botones=None
    ):
        """Cambios de la pestaña Personalizado (vista previa en vivo)."""
        a = self.ajustes
        a.setdefault("acento_personalizado", ACENTO)
        if acento:
            a["acento_personalizado"] = acento
        if modo:
            a["modo_personalizado"] = modo
        if intensidad is not None:
            a["intensidad_personalizado"] = int(intensidad)
        if botones_propios is not None:
            a["botones_propios"] = bool(botones_propios)
            if botones_propios and not a.get("color_botones"):
                a["color_botones"] = a["acento_personalizado"]
        if color_botones:
            a["color_botones"] = color_botones
        if acento or modo or intensidad is not None:
            self.tema_nombre = TEMA_PERSONALIZADO
        self._aplicar_tema_actual()

    def restablecer_apariencia(self):
        """Vuelve a los valores por defecto (se guarda con Guardar)."""
        for k in self.CLAVES_APARIENCIA:
            if k != "tema":
                self.ajustes.pop(k, None)
        self.tema_nombre = TEMA_POR_DEFECTO
        self._aplicar_tema_actual()

    def cancelar_apariencia(self):
        """Flecha de volver: descarta lo que no se guardó."""
        self._cerrar_apariencia(guardar=False)

    def guardar_apariencia(self):
        """Confirma la apariencia actual y vuelve a la playlist."""
        self.ajustes["tema"] = self.tema_nombre
        guardar_ajustes(self.ajustes)
        self._cerrar_apariencia(guardar=True)

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

'''


# ======================================================================
# Motor de cambios
# ======================================================================
def region(texto, ini, fin, nuevo, maximo, requisito=None):
    if texto.count(ini) != 1 or texto.count(fin) != 1:
        raise SystemExit(
            "\nNo se cambió nada.\n"
            f"No encontré con claridad esta parte de tu código:\n    {ini.strip()!r}\n"
            "Pásale este mensaje a Claude para ajustarlo."
        )
    i, j = texto.index(ini), texto.index(fin)
    if not (i < j and j - i <= maximo) or (requisito and requisito not in texto[i:j]):
        raise SystemExit(
            "\nNo se cambió nada.\n"
            f"La zona {ini.strip()!r} no tiene la forma esperada. "
            "Pásale este mensaje a Claude para ajustarlo."
        )
    return texto[:i] + nuevo + texto[j:]


def reemplazar(texto, viejo, nuevo, nombre):
    if texto.count(viejo) != 1:
        raise SystemExit(
            "\nNo se cambió nada.\n"
            f"El cambio «{nombre}» no encontró su lugar en tu código "
            f"(aparece {texto.count(viejo)} veces, debía ser 1).\n"
            "Pásale este mensaje a Claude para ajustarlo."
        )
    return texto.replace(viejo, nuevo)


def despues_de_linea(texto, ancla, nuevo, nombre):
    if texto.count(ancla) != 1:
        raise SystemExit(
            "\nNo se cambió nada.\n"
            f"El cambio «{nombre}» no encontró su lugar en tu código "
            f"(aparece {texto.count(ancla)} veces, debía ser 1).\n"
            "Pásale este mensaje a Claude para ajustarlo."
        )
    lineas = texto.split("\n")
    i = next(k for k, l in enumerate(lineas) if ancla in l)
    lineas[i + 1:i + 1] = nuevo.split("\n")
    return "\n".join(lineas)


def aplicar(t):
    # --- glifo «atrás»
    t = despues_de_linea(t, '"mas": "\\uE712"', '    "atras": "\\uE72B",', "glifo atrás")
    t = despues_de_linea(t, '"mas": "⋯"', '    "atras": "←",', "glifo atrás simple")

    # --- temas
    t = region(t, "def aplicar_tema(tema):\n", "aplicar_tema(TEMAS[TEMA_POR_DEFECTO])\n",
               APLICAR_TEMA, 1500, "global FONDO")
    t = region(t, "def tema_desde_acento(acento, claro=False):\n",
               "def colorear_barra_titulo(root, color_fondo, color_texto):\n",
               TEMA_NUEVO, 3000, "def resolver_tema")

    # --- colores de los botones
    t = reemplazar(
        t,
        "            acciones, 52, bg, ACENTO, ACENTO_HOVER, color_sobre(ACENTO),\n",
        "            acciones, 52, bg, ACENTO_BOTON, ACENTO_BOTON_HOVER,\n"
        "            color_sobre(ACENTO_BOTON),\n",
        "botón de play grande")
    t = reemplazar(
        t,
        "        color = ACENTO if acento else PANEL\n"
        "        hover = ACENTO_HOVER if acento else PANEL_HOVER\n",
        "        color = ACENTO_BOTON if acento else PANEL\n"
        "        hover = ACENTO_BOTON_HOVER if acento else PANEL_HOVER\n",
        "botones de los cuadros")

    # --- clases nuevas
    t = reemplazar(t, BANNER_REPRODUCTOR, CLASES + BANNER_REPRODUCTOR, "clases nuevas")

    # --- la barra lateral ya no se transforma
    t = reemplazar(
        t,
        "        self.lateral.ajustes = self.ajustes   # lo usa la sección PERSONALIZADO\n"
        "        if self.apariencia_abierta:\n"
        "            self.lateral.abrir_apariencia(\n"
        "                self.tema_nombre, self.previsualizar_tema\n"
        "            )\n",
        "        self.lateral.ajustes = self.ajustes   # lo usa la sección PERSONALIZADO\n",
        "barra lateral normal")

    # --- _reconstruir
    t = reemplazar(
        t,
        "        # Si estábamos dentro de Apariencia, mantener el panel abierto\n"
        "        # después de cambiar de paleta.\n"
        "        if self.apariencia_abierta:\n"
        "            self.lateral.abrir_apariencia(\n"
        "                self.tema_nombre, self.previsualizar_tema\n"
        "            )\n\n",
        "", "reconstruir 1")
    t = reemplazar(
        t,
        "        if playlist is not None:\n"
        "            self.abrir_playlist(playlist)\n"
        "            self.orden_col = orden_col\n",
        "        if playlist is not None:\n"
        "            self._reconstruyendo = True\n"
        "            try:\n"
        "                self.abrir_playlist(playlist)\n"
        "            finally:\n"
        "                self._reconstruyendo = False\n"
        "            self.orden_col = orden_col\n",
        "reconstruir 2")
    t = reemplazar(
        t,
        "        # Si estábamos dentro de Apariencia, mantener el panel abierto\n"
        "        # después de restaurar el contenido del reproductor.\n"
        "        if self.apariencia_abierta:\n"
        "            self.lateral.abrir_apariencia(\n"
        "            self.tema_nombre,\n"
        "            self.previsualizar_tema\n"
        "        )\n",
        "        # Si estábamos dentro de Apariencia, volver a mostrar esa pantalla.\n"
        "        if self.apariencia_abierta:\n"
        "            self._mostrar_pantalla_apariencia()\n",
        "reconstruir 3")

    # --- métodos de apariencia
    t = region(t, "    def dialogo_apariencia(self, pos=None):\n",
               "    # ==========================================================\n"
               "    # CABECERA: COLOR Y PORTADA\n",
               METODOS + "    # ==========================================================\n"
               "    # CABECERA: COLOR Y PORTADA\n", 3000, "def guardar_apariencia")

    # --- pantalla en el contenido, rueda del mouse, abrir playlist
    t = despues_de_linea(t, "self.contenido = tk.Frame(self.root, bg=FONDO)",
                         "        self.pantalla_apariencia = None", "pantalla en contenido")
    t = despues_de_linea(t, "        self.lateral._rueda(e)",
                         "        p = getattr(self, \"pantalla_apariencia\", None)\n"
                         "        if p is not None and self.apariencia_abierta:\n"
                         "            p._rueda(e)", "rueda del mouse")
    t = reemplazar(
        t,
        "        if playlist is None:\n"
        "            return\n"
        "\n"
        "        self.playlist_actual = playlist\n"
        "        self.pistas_originales = self.pistas_disponibles_de_playlist(playlist)\n",
        "        if playlist is None:\n"
        "            return\n"
        "\n"
        "        # Salir de Apariencia (sin guardar) al abrir otra playlist.\n"
        "        if self.apariencia_abierta and not getattr(self, \"_reconstruyendo\", False):\n"
        "            self._cerrar_apariencia(guardar=False)\n"
        "\n"
        "        self.playlist_actual = playlist\n"
        "        self.pistas_originales = self.pistas_disponibles_de_playlist(playlist)\n",
        "abrir playlist")
    return t


def main():
    if not ARCHIVO.exists():
        raise SystemExit(f"No encuentro {ARCHIVO}. Ejecútalo dentro de la carpeta de tu proyecto.")
    crudo = ARCHIVO.read_bytes().decode("utf-8")
    crlf = "\r\n" in crudo
    texto = crudo.replace("\r\n", "\n")

    if "class PantallaApariencia" in texto:
        raise SystemExit("La pantalla de Apariencia ya estaba aplicada. No se cambió nada.")
    if "self.lateral.ajustes = self.ajustes" not in texto:
        raise SystemExit("Primero hay que aplicar corregir_paletas.py. No se cambió nada.")
    if "modo_personalizado" not in texto:
        raise SystemExit("Primero hay que aplicar aplicar_modo_claro.py. No se cambió nada.")

    nuevo = aplicar(texto)
    compile(nuevo, str(ARCHIVO), "exec")   # comprueba que no quedó con errores

    copia = ARCHIVO.with_name("reproductor_antes_de_pantalla_apariencia.py")
    copia.write_bytes(crudo.encode("utf-8"))
    if crlf:
        nuevo = nuevo.replace("\n", "\r\n")
    ARCHIVO.write_bytes(nuevo.encode("utf-8"))
    print("Listo. La pantalla de Apariencia (etapa 1) quedó aplicada.")
    print(f"Copia de seguridad: {copia.name}")


if __name__ == "__main__":
    main()
