"""
Nitidez y Transparencia dentro de cada opción de Apariencia > Dinámico.

  - Al activar MODO AMBIENTE, las barras Nitidez y Transparencia se
    despliegan justo debajo del interruptor, dentro de su caja.
  - Al activar FONDO DINÁMICO, se despliegan justo debajo de las opciones
    («Portada de la canción», «Fondo aleatorio», «Colores de la portada»).
  - Al desactivar la opción, las barras desaparecen.

Si ya habías aplicado la versión anterior (una caja aparte al final), esta
la reemplaza.

Requiere aplicar_colores_dinamicos.py primero.

Uso (en la carpeta de reproductor.py):
    python aplicar_barras_dinamico.py
Se crea una copia: reproductor_antes_de_barras_dinamico.py
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


CAJA_VIEJA_INI = "\n        # --- Nitidez y transparencia (solo con fondo dinámico/ambiente) ---\n"
FIN_PANEL = "\n    def _escala_fondo("

METODO = '''    def _barras_fondo(self, caja):
        """Nitidez y Transparencia, dentro de la caja que las pide."""
        self._escala_fondo(
            caja, "Nitidez", "fondo_difuminado",
            "Borrosa", "Nítida", 0, invertir=True
        )
        self._escala_fondo(
            caja, "Transparencia", "fondo_transparencia",
            "Transparente", "Opaco", FONDO_TRANSP_DEF
        )

'''


def main():
    if not ARCHIVO.exists():
        raise SystemExit(f"No encuentro {ARCHIVO}. Ejecútalo dentro de la carpeta de tu proyecto.")
    crudo = ARCHIVO.read_bytes().decode("utf-8")
    crlf = "\r\n" in crudo
    texto = crudo.replace("\r\n", "\n")

    if "def _barras_fondo(" in texto:
        raise SystemExit("Las barras de Dinámico ya estaban aplicadas. No se cambió nada.")
    if "def cambiar_dinamico(" not in texto:
        error("Primero hay que aplicar aplicar_colores_dinamicos.py.")

    # Versión anterior: caja aparte al final -> se quita.
    if CAJA_VIEJA_INI in texto:
        i = texto.index(CAJA_VIEJA_INI)
        j = texto.index(FIN_PANEL, i)
        texto = texto[:i] + "\n" + texto[j:]

    # Modo ambiente: debajo del interruptor
    texto = unico(
        texto,
        "        tk.Frame(caja, bg=PANEL, height=6).pack()\n\n        # --- Color de la interfaz ---\n",
        "        if a.get(\"modo_ambiente\"):\n"
        "            self._barras_fondo(caja)\n"
        "        tk.Frame(caja, bg=PANEL, height=6).pack()\n\n        # --- Color de la interfaz ---\n",
        "modo ambiente")

    # Fondo dinámico: debajo de las opciones
    texto = unico(
        texto,
        "                app.cambiar_dinamico(origen=c),\n"
        "                self._tras_elegir_fondo()\n"
        "            )\n"
        "        )\n"
        "        tk.Frame(caja, bg=PANEL, height=8).pack()\n",
        "                app.cambiar_dinamico(origen=c),\n"
        "                self._tras_elegir_fondo()\n"
        "            )\n"
        "        )\n"
        "        if a.get(\"fondo_dinamico\"):\n"
        "            self._barras_fondo(caja)\n"
        "        tk.Frame(caja, bg=PANEL, height=8).pack()\n",
        "fondo dinámico")

    texto = unico(
        texto, "    def _panel_dinamico(self):\n",
        METODO + "    def _panel_dinamico(self):\n", "panel dinámico")

    compile(texto, str(ARCHIVO), "exec")
    copia = ARCHIVO.with_name("reproductor_antes_de_barras_dinamico.py")
    copia.write_bytes(crudo.encode("utf-8"))
    if crlf:
        texto = texto.replace("\n", "\r\n")
    ARCHIVO.write_bytes(texto.encode("utf-8"))
    print("Listo. Las barras aparecen dentro de Modo ambiente y de Fondo dinámico.")
    print(f"Copia de seguridad: {copia.name}")


if __name__ == "__main__":
    main()
