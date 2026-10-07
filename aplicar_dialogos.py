"""
«Color» del Fondo ahora crea una PALETA COMPLETA a partir del color elegido.

Antes pintaba un rectángulo liso en la barra lateral y la barra inferior,
dejando el resto con la paleta anterior (texto claro sobre fondo claro, etc.).
Ahora, al elegir un color:

  - Un rosa claro  -> todo el reproductor en rosas claros (fondo, paneles,
                      hover, barras) con texto oscuro y un acento rosa fuerte.
  - Un rosa oscuro -> todo el reproductor en rosas oscuros, texto claro y
                      acento rosa brillante.
  - Claro u oscuro se decide solo según el color elegido.
  - Los tonos se calculan por luminancia, así el texto siempre se lee
    (revisado con 864 colores, contraste mínimo 3:1 en el texto suave).
  - Elegir una paleta o mover «Color principal» después deja de usar el color
    de fondo (gana lo último que elijas).
  - El color de los botones sigue pudiendo ser propio.

Requiere aplicar_fondo.py primero.

Uso (en la carpeta de reproductor.py):
    python aplicar_color_paleta.py
Se crea una copia: reproductor_antes_de_color_paleta.py
"""
import sys
from pathlib import Path

ARCHIVO = Path(sys.argv[1] if len(sys.argv) > 1 else "reproductor.py")


def error(msg):
    raise SystemExit(
        "\nNo se cambió nada.\n" + msg +
        "\nPásale este mensaje a Claude para ajustarlo."
    )


FUNCIONES = '''def lum_relativa(hex_color):
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


'''

# (viejo, nuevo): cada «viejo» debe aparecer exactamente una vez.
CAMBIOS = [
    # 1) funciones nuevas antes de resolver_tema
    ("def resolver_tema(nombre, ajustes):\n",
     FUNCIONES + "def resolver_tema(nombre, ajustes):\n"),
    # 2) el color de fondo manda sobre la paleta
    ('    if nombre == TEMA_PERSONALIZADO and ajustes.get("acento_personalizado"):\n'
     '        tema = tema_desde_acento(\n',
     '    if ajustes.get("fondo_tipo") == "color" and ajustes.get("fondo_color"):\n'
     '        tema = tema_desde_fondo(ajustes["fondo_color"])\n'
     '    elif nombre == TEMA_PERSONALIZADO and ajustes.get("acento_personalizado"):\n'
     '        tema = tema_desde_acento(\n'),
    # 3) cambiar_personalizado: color de fondo = cambio de paleta
    ('        if acento or modo or intensidad is not None:\n'
     '            self.tema_nombre = TEMA_PERSONALIZADO\n',
     '        if acento or modo or intensidad is not None:\n'
     '            self.tema_nombre = TEMA_PERSONALIZADO\n'
     '            if fondo_tipo is None and a.get("fondo_tipo") == "color":\n'
     '                a["fondo_tipo"] = "ninguno"   # gana lo último que elijas\n'),
    ('        antes_activo = a.get("fondo_tipo", "ninguno") != "ninguno"\n',
     '        antes_activo = a.get("fondo_tipo", "ninguno") != "ninguno"\n'
     '        antes_color = (a.get("fondo_tipo") == "color", a.get("fondo_color"))\n'),
    ('        if tema_cambia or (antes_activo and not ahora_activo):\n',
     '        ahora_color = (a.get("fondo_tipo") == "color", a.get("fondo_color"))\n'
     '        cambia_paleta_color = (\n'
     '            (antes_color[0] or ahora_color[0]) and antes_color != ahora_color\n'
     '        )\n'
     '        if tema_cambia or cambia_paleta_color or (antes_activo and not ahora_activo):\n'),
    # 4) el motor de imagen ignora el modo «color» (ya es una paleta)
    ('        if self.ajustes.get("fondo_tipo", "ninguno") == "ninguno":\n'
     '            return\n',
     '        if self.ajustes.get("fondo_tipo", "ninguno") in ("ninguno", "color"):\n'
     '            return\n'),
    ('        if a.get("fondo_tipo", "ninguno") == "ninguno":\n'
     '            self._fondo_vivo = False\n',
     '        if a.get("fondo_tipo", "ninguno") in ("ninguno", "color"):\n'
     '            self._fondo_vivo = False\n'),
    # 5) pantalla de Apariencia
    ('("Color", "color"),', '("Color (toda la paleta)", "color"),'),
    ('"Se ve en la cabecera, la barra lateral y la barra inferior."',
     '"Imagen y portadas: cabecera y barras. Color: adapta toda la paleta."'),
    ('        muestra.pack(side="right")\n',
     '        muestra.pack(side="right")\n'
     '        self._muestra_color = muestra\n'),
    ('    def _cambiar_fondo_tipo(self, tipo):\n',
     '    def _cambiar_fondo_tipo(self, tipo):\n'
     '        if tipo == "color" and not self.app.ajustes.get("fondo_color_elegido"):\n'
     '            self._elegir_fondo_color(self._muestra_color)\n'
     '            return\n'),
    ('        muestra.config(bg=elegido[1])\n        self._var_fondo.set("color")\n',
     '        muestra.config(bg=elegido[1])\n        self._var_fondo.set("color")\n'
     '        self.app.ajustes["fondo_color_elegido"] = True\n'),
    ('    "fondo_color",\n    "fondo_transparencia",\n',
     '    "fondo_color",\n    "fondo_color_elegido",\n    "fondo_transparencia",\n'),
    # 6) elegir una paleta deja de usar el color de fondo
    ('        self.tema_nombre = nombre\n        self._aplicar_tema_actual()\n',
     '        if self.ajustes.get("fondo_tipo") == "color":\n'
     '            self.ajustes["fondo_tipo"] = "ninguno"\n'
     '        self.tema_nombre = nombre\n        self._aplicar_tema_actual()\n'),
]


def main():
    if not ARCHIVO.exists():
        raise SystemExit(f"No encuentro {ARCHIVO}. Ejecútalo dentro de la carpeta de tu proyecto.")
    crudo = ARCHIVO.read_bytes().decode("utf-8")
    crlf = "\r\n" in crudo
    texto = crudo.replace("\r\n", "\n")

    if "def tema_desde_fondo(" in texto:
        raise SystemExit("El color de fondo como paleta ya estaba aplicado. No se cambió nada.")
    if "def _aplicar_fondo(self" not in texto:
        error("Primero hay que aplicar aplicar_fondo.py.")

    for viejo, nuevo in CAMBIOS:
        n = texto.count(viejo)
        if n != 1:
            error(f"No encontré con claridad (apariciones: {n}) este punto de tu código:\n    {viejo.strip()[:90]!r}")
        texto = texto.replace(viejo, nuevo, 1)

    compile(texto, str(ARCHIVO), "exec")
    copia = ARCHIVO.with_name("reproductor_antes_de_color_paleta.py")
    copia.write_bytes(crudo.encode("utf-8"))
    if crlf:
        texto = texto.replace("\n", "\r\n")
    ARCHIVO.write_bytes(texto.encode("utf-8"))
    print(f"Listo. Se hicieron {len(CAMBIOS)} cambios: «Color» ahora crea una paleta completa.")
    print(f"Copia de seguridad: {copia.name}")


if __name__ == "__main__":
    main()
