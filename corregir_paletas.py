"""
Corrige el error al elegir una paleta (la ventana quedaba sin lista de
canciones ni barra de reproducción).

Causa: en la sección PERSONALIZADO de la barra lateral se usa
`self.ajustes`, pero la barra lateral (BarraLateral) no tiene ese dato; solo
lo tiene Reproductor. Al reconstruir la interfaz, el panel de Apariencia
fallaba justo ahí y se cortaba todo lo que venía después.

Cambios:
  1. La barra lateral recibe `ajustes` en cuanto se crea.
  2. Al cambiar de paleta también se actualiza el fondo de la ventana
     (quedaba con el color de la paleta anterior).

Uso (en la carpeta de reproductor.py):
    python corregir_paletas.py
Se crea una copia: reproductor_antes_de_paletas.py
"""
import sys
from pathlib import Path

ARCHIVO = Path(sys.argv[1] if len(sys.argv) > 1 else "reproductor.py")

CAMBIOS = [
    ('        self.lateral.grid(row=0, column=0, sticky="nsew")\n',
     '        self.lateral.grid(row=0, column=0, sticky="nsew")\n'
     "        self.lateral.ajustes = self.ajustes   # lo usa la sección PERSONALIZADO\n"),
    ("        # Regenerar imágenes y estilos que dependen de la paleta.\n",
     "        # Regenerar imágenes y estilos que dependen de la paleta.\n"
     "        self.root.configure(bg=FONDO)\n"),
]


def main():
    if not ARCHIVO.exists():
        raise SystemExit(f"No encuentro {ARCHIVO}. Ejecútalo dentro de la carpeta de tu proyecto.")
    crudo = ARCHIVO.read_bytes().decode("utf-8")
    crlf = "\r\n" in crudo
    texto = crudo.replace("\r\n", "\n")

    if "self.lateral.ajustes = self.ajustes" in texto:
        raise SystemExit("La corrección ya estaba aplicada. No se cambió nada.")
    for n, (viejo, nuevo) in enumerate(CAMBIOS, 1):
        if texto.count(viejo) != 1:
            raise SystemExit(
                f"\nNo se cambió nada.\nEl cambio {n} no encontró su lugar "
                f"(aparece {texto.count(viejo)} veces, debía ser 1):\n    {viejo.strip()!r}\n"
                "Pásale este mensaje a Claude para ajustarlo."
            )
        texto = texto.replace(viejo, nuevo)
    compile(texto, str(ARCHIVO), "exec")

    copia = ARCHIVO.with_name("reproductor_antes_de_paletas.py")
    copia.write_bytes(crudo.encode("utf-8"))
    if crlf:
        texto = texto.replace("\n", "\r\n")
    ARCHIVO.write_bytes(texto.encode("utf-8"))
    print("Listo. Se corrigió el cambio de paletas.")
    print(f"Copia de seguridad: {copia.name}")


if __name__ == "__main__":
    main()
