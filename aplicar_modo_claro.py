"""
Color PERSONALIZADO en modo Oscuro o Claro.

Hoy, al elegir un color en PERSONALIZADO, ese color solo se usa como acento
y el resto de la app se genera siempre con fondos oscuros; por eso, aunque
elijas un color claro, todo se ve oscuro.

Este script agrega, dentro del cuadro PERSONALIZADO, dos botones junto al
círculo de color:  «Oscuro»  y  «Claro».
  - Oscuro: igual que ahora.
  - Claro: fondos claros teñidos con tu color, texto oscuro y el acento
    oscurecido solo si hace falta para que se lea bien.
La elección se guarda en ajustes.json (modo_personalizado).

Requisito: tener aplicado corregir_paletas.py.

Uso (en la carpeta de reproductor.py):
    python aplicar_modo_claro.py
Se crea una copia: reproductor_antes_de_modo_claro.py
"""
import sys
from pathlib import Path

ARCHIVO = Path(sys.argv[1] if len(sys.argv) > 1 else "reproductor.py")

TEMA_NUEVO = '''def tema_desde_acento(acento, claro=False):
    """Genera una paleta completa a partir del color elegido por el usuario.
    Oscura por defecto; con claro=True usa fondos claros."""
    if claro:
        # Sobre un fondo claro el acento debe ser lo bastante oscuro.
        if luminancia(acento) > 0.55:
            acento = mezclar_hex(acento, "#000000", 0.62)
        return {
            "FONDO": mezclar_hex(acento, "#fbfaf8", 0.05),
            "PANEL": mezclar_hex(acento, "#efeeec", 0.08),
            "PANEL_HOVER": mezclar_hex(acento, "#e0dfdc", 0.14),
            "PISTA": mezclar_hex(acento, "#c9c8c4", 0.22),
            "TEXTO": "#202020",
            "TEXTO_SUAVE": "#747474",
            "ACENTO": acento,
            "ACENTO_HOVER": mezclar_hex(acento, "#ffffff", 0.82),
        }

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
        return tema_desde_acento(
            ajustes["acento_personalizado"],
            claro=ajustes.get("modo_personalizado") == "claro"
        )

    return TEMAS.get(nombre, TEMAS[TEMA_POR_DEFECTO])


'''

ANCLA_UI = (
    "        self._tooltip_circulo(\n"
    "        circulo_color,\n"
    '        "Elegir color personalizado"\n'
    "        )\n"
)
UI_NUEVA = ANCLA_UI + '''
        # Modo del color personalizado: Oscuro o Claro.
        modo_actual = getattr(self, "ajustes", {}).get(
            "modo_personalizado", "oscuro"
        )

        def elegir_modo(valor):
            self.ajustes.setdefault("acento_personalizado", ACENTO)
            self.ajustes["modo_personalizado"] = valor
            al_seleccionar(TEMA_PERSONALIZADO)

        for texto, valor in (("Oscuro", "oscuro"), ("Claro", "claro")):
            activo = (
                valor == modo_actual and tema_actual == TEMA_PERSONALIZADO
            )
            etiqueta = tk.Label(
                fila_personalizado, text=texto,
                bg=ACENTO if activo else PANEL_HOVER,
                fg=color_sobre(ACENTO) if activo else TEXTO,
                font=(FUENTE, 8, "bold"), padx=10, pady=3, cursor="hand2"
            )
            etiqueta.pack(side="left", padx=(8 if valor == "oscuro" else 3, 0))
            etiqueta.bind("<Button-1>", lambda e, v=valor: elegir_modo(v))
'''


def main():
    if not ARCHIVO.exists():
        raise SystemExit(f"No encuentro {ARCHIVO}. Ejecútalo dentro de la carpeta de tu proyecto.")
    crudo = ARCHIVO.read_bytes().decode("utf-8")
    crlf = "\r\n" in crudo
    texto = crudo.replace("\r\n", "\n")

    if "modo_personalizado" in texto:
        raise SystemExit("El modo claro ya estaba aplicado. No se cambió nada.")
    if "self.lateral.ajustes = self.ajustes" not in texto:
        raise SystemExit(
            "Primero hay que aplicar corregir_paletas.py. No se cambió nada."
        )

    ini = "def tema_desde_acento(acento):\n"
    fin = "def colorear_barra_titulo(root, color_fondo, color_texto):\n"
    if texto.count(ini) != 1 or texto.count(fin) != 1 or texto.count(ANCLA_UI) != 1:
        raise SystemExit(
            "\nNo se cambió nada: no encontré con claridad el lugar de los "
            "cambios. Pásale este mensaje a Claude para ajustarlo."
        )
    i, j = texto.index(ini), texto.index(fin)
    if not (i < j and "resolver_tema" in texto[i:j] and j - i < 2500):
        raise SystemExit(
            "\nNo se cambió nada: la zona de temas no tiene la forma esperada. "
            "Pásale este mensaje a Claude para ajustarlo."
        )
    nuevo = texto[:i] + TEMA_NUEVO + texto[j:]
    nuevo = nuevo.replace(ANCLA_UI, UI_NUEVA)
    compile(nuevo, str(ARCHIVO), "exec")

    copia = ARCHIVO.with_name("reproductor_antes_de_modo_claro.py")
    copia.write_bytes(crudo.encode("utf-8"))
    if crlf:
        nuevo = nuevo.replace("\n", "\r\n")
    ARCHIVO.write_bytes(nuevo.encode("utf-8"))
    print("Listo. Ahora PERSONALIZADO tiene los botones Oscuro / Claro.")
    print(f"Copia de seguridad: {copia.name}")


if __name__ == "__main__":
    main()
