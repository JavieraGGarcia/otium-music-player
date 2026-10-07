"""
Barras de Nitidez y Transparencia que se despliegan solas.

En Apariencia > Fondo, al elegir «Portada de la canción», «Portada de la
playlist» o una imagen personalizada, se despliegan debajo dos barras:

  - Nitidez:       de borrosa a nítida (antes se llamaba «Difuminado» y
                   estaba en otra caja).
  - Transparencia: de transparente a opaca.

Con «Ninguno» o «Color» las barras se ocultan. Los cambios se ven al
instante en la cabecera y las barras de la ventana.

También se quita el selector «Estilo de la imagen» (Nítida/Transparente): ya
no hace falta, porque las dos barras controlan todo. Si quieres el aspecto
suave de antes, baja la Nitidez y sube un poco la Transparencia.

Requiere aplicar_imagen_nitida.py primero.

Uso (en la carpeta de reproductor.py):
    python aplicar_barras_imagen.py
Se crea una copia: reproductor_antes_de_barras_imagen.py
"""
import sys
from pathlib import Path

ARCHIVO = Path(sys.argv[1] if len(sys.argv) > 1 else "reproductor.py")


def error(msg):
    raise SystemExit(
        "\nNo se cambió nada.\n" + msg +
        "\nPásale este mensaje a Claude para ajustarlo."
    )


NUEVO = '''        # --- Barras de la imagen: se despliegan con Imagen o Portadas ---
        self._espacio_fondo = tk.Frame(caja, bg=PANEL, height=6)
        self._espacio_fondo.pack()
        self._ajustes_img = tk.Frame(caja, bg=PANEL)
        self._escala_fondo(
            self._ajustes_img, "Nitidez", "fondo_difuminado",
            "Borrosa", "Nítida", 0, invertir=True
        )
        self._escala_fondo(
            self._ajustes_img, "Transparencia", "fondo_transparencia",
            "Transparente", "Opaco", FONDO_TRANSP_DEF
        )
        self._refrescar_ajustes_img()

    def _refrescar_ajustes_img(self):
        """Despliega las barras solo si el fondo es una imagen o una portada."""
        try:
            marco = self._ajustes_img
            if not marco.winfo_exists():
                return
            if self.app.ajustes.get("fondo_tipo") in TIPOS_LIENZO:
                marco.pack(fill="x", before=self._espacio_fondo)
            else:
                marco.pack_forget()
        except (AttributeError, tk.TclError):
            pass

    def _panel_efectos_reproductor(self, padre=None):
        """Efectos visuales del fondo."""
        caja = self._caja("Efectos", "Se aplican sobre el fondo elegido.")
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

    def _escala_fondo(self, caja, titulo, clave, izq, der, defecto,
                      invertir=False):
        """Deslizador que guarda su valor al moverlo y pinta al hacer una
        pausa (sin reconstruir la pantalla). Con invertir=True la barra
        muestra 100 - valor guardado (Nitidez = 100 - difuminado)."""
        tk.Label(
            caja, text=titulo, bg=PANEL, fg=TEXTO,
            font=(FUENTE, 9, "bold"), anchor="w"
        ).pack(fill="x", padx=14, pady=(8, 2))
        fila = tk.Frame(caja, bg=PANEL)
        fila.pack(fill="x", padx=14, pady=(0, 6))
        tk.Label(
            fila, text=izq, bg=PANEL, fg=TEXTO_SUAVE, font=(FUENTE, 8)
        ).pack(side="left")
        crudo = int(self.app.ajustes.get(clave, defecto))
        valor = 100 - crudo if invertir else crudo
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
            self.app.programar_fondo(**{clave: 100 - v if invertir else v})

        Slider(
            fila, 0, 100, valor, ancho=160, fondo=PANEL, al_mover=mover
        ).pack(side="left", fill="x", expand=True, padx=8)

'''

CAMBIOS = [
    ('        estilo = a.get("fondo_estilo", "transparente")\n',
     '        estilo = "nitida"   # lo controlan las barras Nitidez y Transparencia\n'),
    ('        self.app.cambiar_personalizado(fondo_tipo=tipo)\n\n'
     '    def _restaurar_radio_fondo(self):\n',
     '        self.app.cambiar_personalizado(fondo_tipo=tipo)\n'
     '        self._refrescar_ajustes_img()\n\n'
     '    def _restaurar_radio_fondo(self):\n'),
    ('                lambda e: self.app.cambiar_personalizado(fondo_tipo="imagen")\n',
     '                lambda e: (\n'
     '                    self.app.cambiar_personalizado(fondo_tipo="imagen"),\n'
     '                    self._refrescar_ajustes_img()\n'
     '                )\n'),
]


def main():
    if not ARCHIVO.exists():
        raise SystemExit(f"No encuentro {ARCHIVO}. Ejecútalo dentro de la carpeta de tu proyecto.")
    crudo = ARCHIVO.read_bytes().decode("utf-8")
    crlf = "\r\n" in crudo
    texto = crudo.replace("\r\n", "\n")

    if "def _refrescar_ajustes_img(" in texto:
        raise SystemExit("Las barras de imagen ya estaban aplicadas. No se cambió nada.")
    if "class EtiquetaLienzo(" not in texto:
        error("Primero hay que aplicar aplicar_imagen_nitida.py.")

    ini = "        # --- Estilo de la imagen ---\n"
    fin = "    def _crear_interruptor(\n"
    if texto.count(ini) != 1 or texto.count(fin) != 1:
        error("No encontré con claridad el bloque de Estilo/Transparencia del panel de Fondo.")
    i, j = texto.index(ini), texto.index(fin)
    if j < i:
        error("Orden inesperado en el panel de Fondo.")
    texto = texto[:i] + NUEVO + texto[j:]

    for viejo, nuevo in CAMBIOS:
        n = texto.count(viejo)
        if n != 1:
            error(f"No encontré con claridad (apariciones: {n}) este punto de tu código:\n    {viejo.strip()[:90]!r}")
        texto = texto.replace(viejo, nuevo, 1)

    compile(texto, str(ARCHIVO), "exec")
    copia = ARCHIVO.with_name("reproductor_antes_de_barras_imagen.py")
    copia.write_bytes(crudo.encode("utf-8"))
    if crlf:
        texto = texto.replace("\n", "\r\n")
    ARCHIVO.write_bytes(texto.encode("utf-8"))
    print("Listo. Las barras de Nitidez y Transparencia se despliegan con Imagen o Portadas.")
    print(f"Copia de seguridad: {copia.name}")


if __name__ == "__main__":
    main()
