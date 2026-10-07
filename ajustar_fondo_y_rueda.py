"""
Dos arreglos en Apariencia:

  1) La rueda del mouse no desplazaba la pantalla de Apariencia: al reescribir
     la clase PantallaApariencia se perdió el método _rueda que la app llama
     en cada giro de la rueda (daba un error en la terminal). Se vuelve a
     añadir.
  2) «Imagen personalizada» deja de ser una opción redonda y pasa a ser el
     título de su bloque, justo encima del botón «Elegir imagen...». Si ya
     elegiste una imagen y estás usando otro fondo, aparece «Usar esta
     imagen» para volver a ella sin abrir el explorador de archivos.

Uso (en la carpeta de reproductor.py):
    python ajustar_fondo_y_rueda.py
Se crea una copia: reproductor_antes_de_ajuste_fondo.py
"""
import sys
from pathlib import Path

ARCHIVO = Path(sys.argv[1] if len(sys.argv) > 1 else "reproductor.py")


def error(msg):
    raise SystemExit(
        "\nNo se cambió nada.\n" + msg +
        "\nPásale este mensaje a Claude para ajustarlo."
    )


RUEDA = '''    def _rueda(self, e):
        """Rueda del mouse sobre la pantalla de Apariencia."""
        try:
            sobre = self.winfo_containing(e.x_root, e.y_root)
        except Exception:
            return
        if sobre is None or not str(sobre).startswith(str(self)):
            return
        try:
            if e.num == 4:
                self.canvas.yview_scroll(-2, "units")
            elif e.num == 5:
                self.canvas.yview_scroll(2, "units")
            else:
                self.canvas.yview_scroll(int(-e.delta / 120) * 2, "units")
        except tk.TclError:
            pass

'''

BLOQUE_IMAGEN = '''        # --- Imagen personalizada ---
        activa = a.get("fondo_tipo") == "imagen"
        ruta = a.get("fondo_imagen", "")
        titulo = tk.Frame(caja, bg=PANEL)
        titulo.pack(fill="x", padx=14, pady=(12, 0))
        tk.Label(
            titulo, text="Imagen personalizada", bg=PANEL,
            fg=ACENTO_HOVER if activa else TEXTO,
            font=(FUENTE, 9, "bold"), anchor="w"
        ).pack(side="left")
        if activa:
            tk.Label(
                titulo, text="  ·  en uso", bg=PANEL, fg=TEXTO_SUAVE,
                font=(FUENTE, 8)
            ).pack(side="left")
        elif ruta:
            usar = tk.Label(
                titulo, text="Usar esta imagen", bg=PANEL, fg=ACENTO_HOVER,
                font=(FUENTE, 8, "underline"), cursor="hand2"
            )
            usar.pack(side="right")
            usar.bind(
                "<Button-1>",
                lambda e: self.app.cambiar_personalizado(fondo_tipo="imagen")
            )
        fila_img = tk.Frame(caja, bg=PANEL)
        fila_img.pack(fill="x", padx=14, pady=(6, 4))
        tk.Button(
            fila_img, text="Elegir imagen...", command=self._elegir_imagen_fondo,
            bg=PANEL_HOVER, fg=TEXTO, activebackground=ACENTO,
            activeforeground=color_sobre(ACENTO), relief="flat", bd=0,
            font=(FUENTE, 9), cursor="hand2", padx=10, pady=4
        ).pack(side="left")
'''

CAMBIOS = [
    # fuera la opción redonda
    ('            ("Imagen personalizada", "imagen"),\n', ''),
    # título + botón (reemplaza el bloque antiguo hasta el nombre del archivo)
    ('        # --- Imagen ---\n'
     '        fila_img = tk.Frame(caja, bg=PANEL)\n'
     '        fila_img.pack(fill="x", padx=14, pady=(6, 4))\n'
     '        tk.Button(\n'
     '            fila_img, text="Elegir imagen...", command=self._elegir_imagen_fondo,\n'
     '            bg=PANEL_HOVER, fg=TEXTO, activebackground=ACENTO,\n'
     '            activeforeground=color_sobre(ACENTO), relief="flat", bd=0,\n'
     '            font=(FUENTE, 9), cursor="hand2", padx=10, pady=4\n'
     '        ).pack(side="left")\n'
     '        ruta = a.get("fondo_imagen", "")\n',
     BLOQUE_IMAGEN),
    # rueda del mouse
    ('    def _anotar_scroll(self, valor):\n',
     RUEDA + '    def _anotar_scroll(self, valor):\n'),
]


def main():
    if not ARCHIVO.exists():
        raise SystemExit(f"No encuentro {ARCHIVO}. Ejecútalo dentro de la carpeta de tu proyecto.")
    crudo = ARCHIVO.read_bytes().decode("utf-8")
    crlf = "\r\n" in crudo
    texto = crudo.replace("\r\n", "\n")

    if "# --- Imagen personalizada ---" in texto:
        raise SystemExit("Ya estaba aplicado. No se cambió nada.")
    if "def _panel_fondo_reproductor" not in texto:
        error("Primero hay que aplicar aplicar_fondo.py.")

    for viejo, nuevo in CAMBIOS:
        n = texto.count(viejo)
        if n != 1:
            error(f"No encontré con claridad (apariciones: {n}) este punto de tu código:\n    {viejo.strip()[:90]!r}")
        texto = texto.replace(viejo, nuevo, 1)

    compile(texto, str(ARCHIVO), "exec")
    copia = ARCHIVO.with_name("reproductor_antes_de_ajuste_fondo.py")
    copia.write_bytes(crudo.encode("utf-8"))
    if crlf:
        texto = texto.replace("\n", "\r\n")
    ARCHIVO.write_bytes(texto.encode("utf-8"))
    print("Listo. Rueda del mouse repuesta y «Imagen personalizada» ahora es un título.")
    print(f"Copia de seguridad: {copia.name}")


if __name__ == "__main__":
    main()
