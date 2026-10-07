"""
PASO 3: colores y fondo dinámicos (Apariencia > Dinámico).

Qué trae:

  - COLOR DE LA INTERFAZ
      Color personalizado : tu paleta, como siempre.
      Color de la portada : toda la paleta (fondo, paneles, acento y
                            botones) sale de la portada de la canción
                            que suena y cambia con cada canción.
      Automático          : tu paleta se queda y solo el acento y los
                            botones toman el color vivo de la portada.
  - FONDO DINÁMICO ("Cambiar fondo al cambiar de canción")
      Portada de la canción  : la portada como fondo (como antes).
      Fondo aleatorio        : un fondo distinto en cada canción, de los de
                               Otium y de Mis fondos.
      Colores de la portada  : un degradado suave con los colores de la
                               portada.
    Al activarlo, el fondo se enciende solo (ya no hace falta elegir
    antes una imagen).
  - MODO AMBIENTE: un interruptor que activa «Color de la portada» y
    «Portada de la canción» juntos. Al apagarlo vuelve lo que tenías.

Cómo cambian los colores: Otium repinta toda la interfaz de una vez (tarda
una décima de segundo y no corta la música ni pierde tu lugar en la
lista). Solo se repinta si la portada nueva cambia los colores de verdad.

Elegir una paleta o un color en Paletas apaga el color dinámico.

Requiere aplicar_fondos_defecto.py primero.

Uso (en la carpeta de reproductor.py):
    python aplicar_colores_dinamicos.py
Se crea una copia: reproductor_antes_de_colores_dinamicos.py
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


MODULO = r'''PALETA_PORTADA = None      # (dominante, vivo) de la portada que está sonando


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


'''

MODULO2 = r'''

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


'''

METODOS = r'''    # ==========================================================
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

'''

PANEL_NUEVO = r'''    def _fila_interruptor(self, caja, titulo, descripcion, valor,
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
        tk.Frame(caja, bg=PANEL, height=8).pack()

'''



def main():
    if not ARCHIVO.exists():
        raise SystemExit(f"No encuentro {ARCHIVO}. Ejecútalo dentro de la carpeta de tu proyecto.")
    crudo = ARCHIVO.read_bytes().decode("utf-8")
    crlf = "\r\n" in crudo
    texto = crudo.replace("\r\n", "\n")

    if "def paleta_desde_pil(" in texto:
        raise SystemExit("Los colores dinámicos ya estaban aplicados. No se cambió nada.")
    if "def generar_fondo(" not in texto:
        error("Primero hay que aplicar aplicar_fondos_defecto.py.")

    # 1) Funciones nuevas (antes de acento_legible y antes de Reproductor)
    texto = unico(texto, "def acento_legible(tema, c):\n",
                  MODULO + "def acento_legible(tema, c):\n", "acento_legible")
    marca = "# ==============================================================\n# REPRODUCTOR\n"
    texto = unico(texto, marca, MODULO2 + marca, "clase Reproductor")

    # 2) La paleta puede salir de la portada
    texto = unico(
        texto,
        '    pal_img = None\n    if (\n        ajustes.get("fondo_tipo") == "imagen"\n',
        '    pal_img = None\n'
        '    modo_color = ajustes.get("color_interfaz", "personalizado")\n'
        '    if modo_color == "portada" and PALETA_PORTADA:\n'
        '        pal_img = PALETA_PORTADA\n'
        '    elif (\n        ajustes.get("fondo_tipo") == "imagen"\n',
        "resolver_tema")
    texto = unico(
        texto,
        "    # Color propio para los botones (vale para cualquier paleta).\n",
        '    # Automático: la paleta se queda y el acento sale de la portada.\n'
        '    if modo_color == "automatico" and PALETA_PORTADA:\n'
        '        (tema["ACENTO"], tema["ACENTO_HOVER"],\n'
        '         tema["ACENTO_BOTON"], tema["ACENTO_BOTON_HOVER"]) = (\n'
        '            acento_legible(tema, PALETA_PORTADA[1])\n'
        '        )\n\n'
        "    # Color propio para los botones (vale para cualquier paleta).\n",
        "color automático")

    # 3) Ajustes nuevos
    texto = unico(
        texto,
        "            resplandor_portada=None, fondo_aleatorio=None\n        ):",
        "            resplandor_portada=None, fondo_aleatorio=None,\n"
        "            fondo_dinamico_origen=None, color_interfaz=None,\n"
        "            modo_ambiente=None\n        ):",
        "firma de cambiar_personalizado")
    texto = unico(
        texto,
        '            ("fondo_aleatorio", fondo_aleatorio, bool),\n',
        '            ("fondo_aleatorio", fondo_aleatorio, bool),\n'
        '            ("fondo_dinamico_origen", fondo_dinamico_origen, str),\n'
        '            ("modo_ambiente", modo_ambiente, bool),\n',
        "lista de ajustes de fondo")
    texto = unico(
        texto,
        "        if acento or modo or intensidad is not None:\n"
        "            self.tema_nombre = TEMA_PERSONALIZADO\n",
        "        if color_interfaz:\n"
        "            a[\"color_interfaz\"] = color_interfaz\n"
        "            tema_cambia = True\n"
        "        if acento or modo or intensidad is not None:\n"
        "            a[\"color_interfaz\"] = \"personalizado\"\n"
        "            a[\"modo_ambiente\"] = False\n"
        "            self.tema_nombre = TEMA_PERSONALIZADO\n",
        "color propio")
    texto = unico(
        texto,
        '        self.ajustes["fondo_paleta_imagen"] = False\n        self.tema_nombre = nombre\n',
        '        self.ajustes["fondo_paleta_imagen"] = False\n'
        '        self.ajustes["color_interfaz"] = "personalizado"\n'
        '        self.ajustes["modo_ambiente"] = False\n'
        '        self.tema_nombre = nombre\n',
        "elegir_paleta")
    texto = unico(
        texto,
        '    "fondo_aleatorio",\n]\n',
        '    "fondo_aleatorio",\n    "color_interfaz",\n    "modo_ambiente",\n'
        '    "ambiente_previo",\n    "fondo_dinamico_origen",\n]\n',
        "CLAVES_APARIENCIA")
    texto = unico(texto, "    def cambiar_estilo_fondo(self, estilo):\n",
                  METODOS + "    def cambiar_estilo_fondo(self, estilo):\n",
                  "cambiar_estilo_fondo")

    # 4) Fondo: colores de la portada / aleatorio
    texto = unico(
        texto,
        '        if a.get("fondo_dinamico") and self.video_actual:\n            tipo = "portada_cancion"\n',
        '        origen_din = a.get("fondo_dinamico_origen", "portada")\n'
        '        if (a.get("fondo_dinamico") and self.video_actual\n'
        '                and origen_din == "colores"\n'
        '                and getattr(self, "_paleta_portada", None)):\n'
        '            dom, vivo = self._paleta_portada\n'
        '            clave = ("colores", dom, vivo)\n'
        '            guardado = getattr(self, "_fondo_colores", None)\n'
        '            if guardado is None or guardado[0] != clave:\n'
        '                self._fondo_colores = (clave, fondo_desde_colores(dom, vivo))\n'
        '            return (clave, self._fondo_colores[1])\n'
        '        if (a.get("fondo_dinamico") and self.video_actual\n'
        '                and origen_din == "portada"):\n'
        '            tipo = "portada_cancion"\n',
        "fondo dinámico")

    # 5) Al cargar la portada
    texto = unico(
        texto,
        "        self.lbl_caratula.config(\n            image=self.img_caratula\n        )\n\n        # Actualizar automáticamente el fondo cuando\n",
        "        self.lbl_caratula.config(\n            image=self.img_caratula\n        )\n\n"
        "        try:\n"
        "            self._portada_para_dinamico(video_id, img)\n"
        "        except Exception:\n"
        "            pass\n\n"
        "        # Actualizar automáticamente el fondo cuando\n",
        "carátula")

    # 6) Pantalla de Apariencia: sección Dinámico
    texto = entre(texto, "    def _panel_dinamico(self):\n",
                  "    def _escala_fondo(self, caja, titulo, clave, izq, der, defecto,\n",
                  PANEL_NUEVO, "panel dinámico")
    texto = unico(
        texto,
        '            self._panel_dinamico()\n\n            self._panel_proximamente(\n                (\n'
        '                    "Adaptar colores a la portada",\n'
        '                    "Color de la interfaz automático",\n'
        '                    "Modo ambiente",\n                )\n            )\n',
        '            self._panel_dinamico()\n',
        "sección Dinámico")

    compile(texto, str(ARCHIVO), "exec")
    copia = ARCHIVO.with_name("reproductor_antes_de_colores_dinamicos.py")
    copia.write_bytes(crudo.encode("utf-8"))
    if crlf:
        texto = texto.replace("\n", "\r\n")
    ARCHIVO.write_bytes(texto.encode("utf-8"))
    print("Listo. Apariencia > Dinámico: color de la interfaz, fondo dinámico y modo ambiente.")
    print(f"Copia de seguridad: {copia.name}")


if __name__ == "__main__":
    main()
