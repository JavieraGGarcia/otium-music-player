"""
El «Color de los botones» ahora manda sobre TODO lo que usa el color de acento:
barra de volumen, barra de reproducción (y su perilla), aleatorio/repetir
activos, la canción que suena (número, título, parlante), la playlist
seleccionada, enlaces, etc. Antes solo cambiaba el botón de play grande y
los botones «Guardar».

  - Con el interruptor apagado todo sigue el color principal, como antes.
  - Con el interruptor encendido, el color elegido reemplaza al acento.
  - Si el color elegido se lee mal sobre el fondo (un amarillo muy claro sobre
    un tema claro, o un azul muy oscuro sobre uno oscuro), el texto y las
    líneas usan una versión ajustada para que siempre se vea; los botones
    conservan exactamente el color que elegiste.

Uso (en la carpeta de reproductor.py):
    python aplicar_botones_acento.py
Se crea una copia: reproductor_antes_de_botones_acento.py
"""
import sys
from pathlib import Path

ARCHIVO = Path(sys.argv[1] if len(sys.argv) > 1 else "reproductor.py")

VIEJO = '''        c = ajustes["color_botones"]
        tema["ACENTO_BOTON"] = c
        tema["ACENTO_BOTON_HOVER"] = mezclar_hex(
            c, "#ffffff", 0.82 if luminancia(tema["FONDO"]) > 0.5 else 0.78
        )
    return tema
'''

NUEVO = '''        c = ajustes["color_botones"]
        claro = luminancia(tema["FONDO"]) > 0.5
        tema["ACENTO_BOTON"] = c
        tema["ACENTO_BOTON_HOVER"] = mezclar_hex(
            c, "#ffffff", 0.82 if claro else 0.78
        )
        # El mismo color tiñe barras, iconos activos y textos destacados,
        # ajustado para que se lea sobre el fondo de la paleta.
        ac = c
        if claro and luminancia(ac) > 0.55:
            ac = mezclar_hex(ac, "#000000", 0.55)
        elif not claro and luminancia(ac) < 0.18:
            ac = mezclar_hex(ac, "#ffffff", 0.45)
        tema["ACENTO"] = ac
        tema["ACENTO_HOVER"] = mezclar_hex(
            ac, "#ffffff", 0.82 if claro else 0.78
        )
    return tema
'''


def main():
    if not ARCHIVO.exists():
        raise SystemExit(f"No encuentro {ARCHIVO}. Ejecútalo dentro de la carpeta de tu proyecto.")
    crudo = ARCHIVO.read_bytes().decode("utf-8")
    crlf = "\r\n" in crudo
    texto = crudo.replace("\r\n", "\n")

    if "El mismo color tiñe barras" in texto:
        raise SystemExit("Ya estaba aplicado. No se cambió nada.")
    if texto.count(VIEJO) != 1:
        raise SystemExit(
            "\nNo se cambió nada.\nNo encontré con claridad la parte de "
            "«color de los botones» en resolver_tema.\n"
            "Pásale este mensaje a Claude para ajustarlo."
        )
    nuevo = texto.replace(VIEJO, NUEVO, 1)
    compile(nuevo, str(ARCHIVO), "exec")

    copia = ARCHIVO.with_name("reproductor_antes_de_botones_acento.py")
    copia.write_bytes(crudo.encode("utf-8"))
    if crlf:
        nuevo = nuevo.replace("\n", "\r\n")
    ARCHIVO.write_bytes(nuevo.encode("utf-8"))
    print("Listo. El color de los botones ahora tiñe barras, iconos activos y textos destacados.")
    print(f"Copia de seguridad: {copia.name}")


if __name__ == "__main__":
    main()
