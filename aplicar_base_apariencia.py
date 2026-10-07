"""
PASO 1 de la nueva pantalla de Apariencia: la base.

Qué cambia (no se pierde ninguna opción que ya tenías):

  - Aparece un MENÚ LATERAL dentro de Apariencia con 4 secciones:
        Paletas   -> paletas prediseñadas + Personalizado
                     (color principal, color de botones, modo claro/oscuro)
        Fondos    -> ninguno / color / portadas / imagen, con Nitidez y
                     Transparencia
        Efectos   -> efecto vidrio (+ próximamente)
        Dinámico  -> fondo dinámico (+ próximamente)
    La tarjeta «Personalizado» y la pestaña del mismo nombre ya no hacen
    falta: sus opciones están al final de «Paletas».

  - A la derecha hay un panel de VISTA PREVIA: una miniatura del reproductor
    (barra lateral, cabecera, canciones, controles) que se actualiza sola
    con la paleta, el color, el fondo, la nitidez y la transparencia.
    Si la ventana es angosta, la vista previa se oculta sola.

  - Abajo, junto a Restablecer y Guardar, hay un botón Cancelar.

Requiere aplicar_barras_imagen.py primero.

Uso (en la carpeta de reproductor.py):
    python aplicar_base_apariencia.py
Se crea una copia: reproductor_antes_de_base_apariencia.py
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


# ----------------------------------------------------------------------
# 1) Atributos de clase
# ----------------------------------------------------------------------
CLASE_VIEJO = "    ANCHO_TARJETA = 154\n"
CLASE_NUEVO = '''    SECCIONES = (
        ("paletas", "Paletas", "◐"),
        ("fondos", "Fondos", "▣"),
        ("efectos", "Efectos", "✦"),
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
'''

# ----------------------------------------------------------------------
# 2) _construir: sin pestañas, con zona de tres columnas
# ----------------------------------------------------------------------
TABS_INI = "        # ------------------------------------------------------\n        # PESTAÑAS\n"
TABS_FIN = "        # ------------------------------------------------------\n        # PIE FIJO\n"
TABS_NUEVO = '''        # (el menú de secciones está en la columna izquierda, más abajo)
        self._tabs = {}

'''

PIE_VIEJO = '''        app.boton(
            fila_botones,
            "Restablecer",
            app.restablecer_apariencia,
            ancho=12
        ).pack(
            side="right",
            padx=(0, 10)
        )
'''
PIE_NUEVO = '''        app.boton(
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
'''

MARCO_VIEJO = '''        marco = tk.Frame(
            self,
            bg=FONDO
        )

        marco.pack(
            fill="both",
            expand=True,
            padx=(30, 10)
        )
'''
MARCO_NUEVO = '''        zona = tk.Frame(
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
'''

# ----------------------------------------------------------------------
# 3) Columnas de la rejilla de paletas (ahora hay menos ancho)
# ----------------------------------------------------------------------
COLS = [
    ("        if ancho >= 780:\n", "        if ancho >= 700:\n"),
    ("        elif ancho >= 590:\n", "        elif ancho >= 530:\n"),
    ("        elif ancho >= 400:\n", "        elif ancho >= 350:\n"),
]

# ----------------------------------------------------------------------
# 4) mostrar_pestana
# ----------------------------------------------------------------------
PEST_INI = "    def mostrar_pestana(self, clave):\n"
PEST_FIN = "    # ==========================================================\n    # PALETAS\n"
PEST_NUEVO = '''    def mostrar_pestana(self, clave):

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

            self._panel_fondo_reproductor()

        elif clave == "efectos":

            self._encabezado(
                "Efectos",
                "Detalles visuales que se aplican sobre el fondo."
            )

            self._panel_efectos_reproductor()

            self._panel_proximamente(
                (
                    "Resplandor de portada",
                    "Brillo ambiental",
                    "Animación suave del fondo",
                )
            )

        else:

            self._encabezado(
                "Dinámico",
                "Haz que Otium cambie según lo que suena."
            )

            self._panel_dinamico()

            self._panel_proximamente(
                (
                    "Adaptar colores a la portada",
                    "Color de la interfaz automático",
                    "Modo ambiente",
                )
            )

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

'''

# ----------------------------------------------------------------------
# 5) «Personalizado» pasa al final de Paletas
# ----------------------------------------------------------------------
CARD_INI = "        # ------------------------------------------------------\n        # TARJETA PERSONALIZADO\n"
CARD_FIN = "        self._organizar_tarjetas()\n\n    def _crear_categoria(\n"
CARD_NUEVO = '''        # ------------------------------------------------------
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

'''

# ----------------------------------------------------------------------
# 6) Efectos / Dinámico
# ----------------------------------------------------------------------
EF_INI = "    def _panel_efectos_reproductor(self, padre=None):\n"
EF_FIN = "    def _escala_fondo(self, caja, titulo, clave, izq, der, defecto,\n"
EF_NUEVO = '''    def _panel_efectos_reproductor(self, padre=None):
        """Efectos visuales del fondo."""
        caja = self._caja("Efecto vidrio", "Se aplica sobre el fondo elegido.")
        self._crear_interruptor(
            caja, "Efecto vidrio",
            "Suaviza y aclara un poco el fondo",
            "efecto_vidrio"
        )
        tk.Frame(caja, bg=PANEL, height=6).pack()

    def _panel_dinamico(self):
        """Opciones que reaccionan a la canción que suena."""
        caja = self._caja(
            "Fondo dinámico",
            "El fondo cambia con la música."
        )
        self._crear_interruptor(
            caja, "Fondo dinámico",
            "Sigue la portada de la canción que suena",
            "fondo_dinamico"
        )
        tk.Frame(caja, bg=PANEL, height=6).pack()

'''

PROX_INI = "    def _panel_proximamente(self):\n"
PROX_FIN = "    # ==========================================================\n    # SELECTOR COLOR PRINCIPAL\n"
PROX_NUEVO = '''    def _panel_proximamente(self, textos=()):

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

'''

# ----------------------------------------------------------------------
# 7) Menú lateral + vista previa
# ----------------------------------------------------------------------
SCROLL_MARCA = "    # ==========================================================\n    # SCROLL\n"
NUEVOS_METODOS = '''    # ==========================================================
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

'''

# ----------------------------------------------------------------------
# 8) Refrescar la vista previa cuando se repinta el fondo
# ----------------------------------------------------------------------
HOOK_VIEJO = '''        self._fondo_job = None
        try:
            self._aplicar_fondo_interno()
        except Exception:
            import traceback
            traceback.print_exc()
'''
HOOK_NUEVO = HOOK_VIEJO + '''        # La vista previa de Apariencia sigue al fondo real.
        p = getattr(self, "pantalla_apariencia", None)
        if p is not None and getattr(self, "apariencia_abierta", False):
            try:
                p.refrescar_previa()
            except Exception:
                pass
'''


def main():
    if not ARCHIVO.exists():
        raise SystemExit(f"No encuentro {ARCHIVO}. Ejecútalo dentro de la carpeta de tu proyecto.")
    crudo = ARCHIVO.read_bytes().decode("utf-8")
    crlf = "\r\n" in crudo
    texto = crudo.replace("\r\n", "\n")

    if "def _crear_menu(" in texto:
        raise SystemExit("La base de Apariencia ya estaba aplicada. No se cambió nada.")
    if "def _refrescar_ajustes_img(" not in texto:
        error("Primero hay que aplicar aplicar_barras_imagen.py.")

    texto = unico(texto, CLASE_VIEJO, CLASE_NUEVO, "clase")
    texto = entre(texto, TABS_INI, TABS_FIN, TABS_NUEVO, "pestañas")
    texto = unico(texto, PIE_VIEJO, PIE_NUEVO, "pie")
    texto = unico(texto, MARCO_VIEJO, MARCO_NUEVO, "marco")
    for viejo, nuevo in COLS:
        texto = unico(texto, viejo, nuevo, "columnas")
    texto = entre(texto, PEST_INI, PEST_FIN, PEST_NUEVO, "mostrar_pestana")
    texto = entre(texto, CARD_INI, CARD_FIN, CARD_NUEVO, "tarjeta personalizado")
    texto = entre(texto, EF_INI, EF_FIN, EF_NUEVO, "efectos")
    texto = entre(texto, PROX_INI, PROX_FIN, PROX_NUEVO, "próximamente")
    texto = unico(texto, SCROLL_MARCA, NUEVOS_METODOS + SCROLL_MARCA, "scroll")
    texto = unico(texto, HOOK_VIEJO, HOOK_NUEVO, "fondo")

    compile(texto, str(ARCHIVO), "exec")
    copia = ARCHIVO.with_name("reproductor_antes_de_base_apariencia.py")
    copia.write_bytes(crudo.encode("utf-8"))
    if crlf:
        texto = texto.replace("\n", "\r\n")
    ARCHIVO.write_bytes(texto.encode("utf-8"))
    print("Listo. Apariencia ahora tiene menú lateral y vista previa.")
    print(f"Copia de seguridad: {copia.name}")


if __name__ == "__main__":
    main()
