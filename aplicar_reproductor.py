"""
PASO 5 (parte 1): sección «Reproductor» en Apariencia.

  - TAMAÑO DE LA PORTADA: Pequeña / Mediana / Grande. Cambia la portada
    grande de la playlist y la carátula de la barra inferior.
  - ESTILO DE LOS CONTROLES: Minimalistas / Clásicos / Grandes.
  - INFORMACIÓN: «Mostrar nombres y portada en los controles» (si lo apagas
    la barra solo muestra los controles) y Título + artista, o
    Título + artista + álbum. El álbum lo da YouTube cuando lo conoce; si
    no, se muestra el nombre de la playlist.

Todo se ve al instante y se descarta con Cancelar, como el resto.

Requiere aplicar_efectos.py primero.

Uso (en la carpeta de reproductor.py):
    python aplicar_reproductor.py
Se crea una copia: reproductor_antes_de_reproductor.py
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


MODULO = r'''# ==============================================================
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


'''

METODOS = r'''    # ---- Reproductor: tamaño de portada, controles e información ----
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

'''

PANEL_NUEVO = r'''    # ==========================================================
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

'''

IZQ_VIEJO = r'''        izq = tk.Frame(barra, bg=PANEL)
        izq.grid(row=0, column=0, sticky="w", padx=(18, 0))
        self.lbl_caratula = tk.Label(
            izq, image=self.img_caratula, bg=PANEL, bd=0
        )
        self.lbl_caratula.pack(side="left")
        textos = tk.Frame(izq, bg=PANEL)
        textos.pack(side="left", padx=(12, 0))
        self.lbl_titulo = etiqueta(
            textos, text="Ninguna canción", bg=PANEL, fg=TEXTO,
            font=self.f_barra_titulo, anchor="w"
        )
        self.lbl_titulo.pack(fill="x")
        self.lbl_artista = etiqueta(
            textos, text="", bg=PANEL, fg=TEXTO_SUAVE,
            font=self.f_barra_texto, anchor="w"
        )
        self.lbl_artista.pack(fill="x")
'''

IZQ_NUEVO = r'''        izq = tk.Frame(barra, bg=PANEL)
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
'''

CTRL_NUEVO = r'''        controles = tk.Frame(centro, bg=PANEL)
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

'''



def main():
    if not ARCHIVO.exists():
        raise SystemExit(f"No encuentro {ARCHIVO}. Ejecútalo dentro de la carpeta de tu proyecto.")
    crudo = ARCHIVO.read_bytes().decode("utf-8")
    crlf = "\r\n" in crudo
    texto = crudo.replace("\r\n", "\n")

    if "def aplicar_reproductor(" in texto:
        raise SystemExit("La sección Reproductor ya estaba aplicada. No se cambió nada.")
    if "def con_resplandor(" not in texto:
        error("Primero hay que aplicar aplicar_efectos.py.")

    # 1) Funciones del módulo
    marca = "# ==============================================================\n# REPRODUCTOR\n"
    texto = unico(texto, marca, MODULO + marca, "clase Reproductor")

    # 2) El álbum que da YouTube al preparar el audio
    texto = unico(
        texto,
        '    with yt_dlp.YoutubeDL({"format": "bestaudio/best", "quiet": True}) as ydl:\n'
        '        return ydl.extract_info(url, download=False)["url"]\n',
        '    with yt_dlp.YoutubeDL({"format": "bestaudio/best", "quiet": True}) as ydl:\n'
        '        info = ydl.extract_info(url, download=False)\n'
        '    try:\n'
        '        ALBUMES[video_id] = (info.get("album") or "").strip()\n'
        '    except Exception:\n'
        '        pass\n'
        '    return info["url"]\n',
        "resolver_audio")

    # 3) Ancho del texto de la barra según el tamaño de la carátula
    for viejo, nuevo in (
        ("self.f_barra_titulo, 190)", "self.f_barra_titulo, ancho_texto_barra())"),
        ("self.f_barra_texto, 190)", "self.f_barra_texto, ancho_texto_barra())"),
    ):
        if texto.count(viejo) != 3:
            error(f"No encontré las 3 apariciones esperadas de {viejo!r}.")
        texto = texto.replace(viejo, nuevo)

    # 4) Arranque
    texto = unico(
        texto,
        "        self.f_barra_texto = tkfont.Font(family=FUENTE, size=9)\n"
        "        self._crear_imagenes_tema()\n",
        "        self.f_barra_texto = tkfont.Font(family=FUENTE, size=9)\n"
        "        aplicar_reproductor(self.ajustes)\n"
        "        self._tam_imgs = (TAM_PORTADA, TAM_CARATULA_BARRA)\n"
        "        self._crear_imagenes_tema()\n",
        "arranque")

    # 5) Barra inferior
    texto = unico(
        texto, "        self.barra = barra\n",
        "        self.barra = barra\n"
        "        self.root.grid_rowconfigure(1, minsize=ALTO_BARRA)\n",
        "alto de la barra")
    texto = unico(texto, IZQ_VIEJO, IZQ_NUEVO, "izquierda de la barra")
    texto = entre(texto, "        controles = tk.Frame(centro, bg=PANEL)\n",
                  "        fila = tk.Frame(centro, bg=PANEL)\n",
                  CTRL_NUEVO, "controles de la barra")

    # 6) Reconstrucción
    texto = unico(
        texto,
        '        """Reconstruye la interfaz con la paleta actual sin detener la música."""\n',
        '        """Reconstruye la interfaz con la paleta actual sin detener la música."""\n'
        '        aplicar_reproductor(self.ajustes)\n'
        '        self._ajustar_tamano_imagenes()\n',
        "reconstruir (inicio)")
    texto = unico(
        texto,
        "        self._refrescar_resplandor()\n"
        "        self._fondo_reaplicar(80)\n\n    CLAVES_APARIENCIA",
        "        self._refrescar_info_barra()\n"
        "        self._refrescar_resplandor()\n"
        "        self._fondo_reaplicar(80)\n\n    CLAVES_APARIENCIA",
        "reconstruir (final)")

    # 7) Métodos
    texto = unico(texto, "    def cambiar_estilo_fondo(self, estilo):\n",
                  METODOS + "    def cambiar_estilo_fondo(self, estilo):\n",
                  "cambiar_estilo_fondo")
    texto = unico(
        texto,
        "    def _marcar_en_vista(self):\n"
        "        self.lista.marcar_sonando(self._posicion_sonando_en_vista())\n",
        "    def _marcar_en_vista(self):\n"
        "        self.lista.marcar_sonando(self._posicion_sonando_en_vista())\n"
        "        self._refrescar_info_barra()\n",
        "_marcar_en_vista")
    texto = unico(
        texto,
        "        self._precargando.discard(video_id)\n"
        "        self._guardar_audio(video_id, url)\n",
        "        self._precargando.discard(video_id)\n"
        "        self._guardar_audio(video_id, url)\n"
        "        if video_id == self.video_actual:\n"
        "            self._refrescar_info_barra()\n",
        "_audio_listo")
    texto = unico(
        texto,
        '        self.lbl_artista.config(text="")\n',
        '        self.lbl_artista.config(text="")\n'
        '        self._refrescar_info_barra()\n',
        "detener_todo")

    # 8) Ajustes que se restauran al cancelar
    texto = unico(
        texto,
        '    "fondo_animacion",\n]\n',
        '    "fondo_animacion",\n    "portada_tam",\n    "controles_estilo",\n'
        '    "info_en_barra",\n    "info_barra",\n]\n',
        "CLAVES_APARIENCIA")

    # 9) Pantalla de Apariencia
    texto = unico(
        texto,
        '        ("efectos", "Efectos", "✦"),\n',
        '        ("efectos", "Efectos", "✦"),\n'
        '        ("reproductor", "Reproductor", "▶"),\n',
        "menú de secciones")
    texto = unico(
        texto,
        '            self._panel_efectos_reproductor()\n\n        else:\n',
        '            self._panel_efectos_reproductor()\n\n'
        '        elif clave == "reproductor":\n\n'
        '            self._encabezado(\n'
        '                "Reproductor",\n'
        '                "Tamaño de las portadas, controles e información."\n'
        '            )\n\n'
        '            self._panel_reproductor()\n\n        else:\n',
        "sección Reproductor")
    texto = unico(texto, "    def _cambiar_efecto(self, clave, valor):\n",
                  PANEL_NUEVO + "    def _cambiar_efecto(self, clave, valor):\n",
                  "panel Reproductor")

    compile(texto, str(ARCHIVO), "exec")
    copia = ARCHIVO.with_name("reproductor_antes_de_reproductor.py")
    copia.write_bytes(crudo.encode("utf-8"))
    if crlf:
        texto = texto.replace("\n", "\r\n")
    ARCHIVO.write_bytes(texto.encode("utf-8"))
    print("Listo. Apariencia > Reproductor: tamaño de portada, controles e información.")
    print(f"Copia de seguridad: {copia.name}")


if __name__ == "__main__":
    main()
