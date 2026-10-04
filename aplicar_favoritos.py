"""
Añade FAVORITOS a tu reproductor:
  - un corazón en cada canción (aparece al pasar el mouse)
  - un corazón en la barra inferior para la canción que suena
  - una playlist automática «Me gusta» (arriba en la barra lateral) que
    junta las canciones marcadas de TODAS tus playlists

Uso (en la terminal de VS Code, dentro de la carpeta de tu proyecto):
    python aplicar_favoritos.py
o, si tu archivo tiene otro nombre:
    python aplicar_favoritos.py mi_archivo.py

Antes de tocar nada hace una copia: reproductor_antes_de_favoritos.py
Si algo no coincide con tu código, NO cambia nada y te dice qué falló.
"""
import sys
from pathlib import Path

ARCHIVO = Path(sys.argv[1] if len(sys.argv) > 1 else "reproductor.py")

# Cada cambio: (tipo, texto_a_buscar, texto_nuevo)
#   despues  -> agrega líneas justo DEBAJO de la línea que contiene el texto
#   antes    -> agrega líneas justo ENCIMA de la línea que contiene el texto
#   linea    -> reemplaza la línea completa que contiene el texto
#   texto    -> reemplaza solo ese fragmento
#   bloque   -> reemplaza un bloque exacto de varias líneas
CAMBIOS = []


def cambio(tipo, buscar, nuevo):
    CAMBIOS.append((tipo, buscar, nuevo))


# ---------------------------------------------------------------- íconos
cambio("despues", '"mas": "\\uE712"',
       '    "corazon": "\\uEB51", "corazon_lleno": "\\uEB52",')
cambio("despues", '"mas": "⋯"',
       '    "corazon": "♡", "corazon_lleno": "♥",')

# ------------------------------------------------------------ constantes
cambio("linea", "COL_DUR = 84", "COL_DUR = 84\nCOL_CORAZON = 44")
cambio("despues", "ARCHIVO_AJUSTES = ",
       'ARCHIVO_FAVORITOS = carpeta_datos() / "favoritos.json"')

# ---------------------------------------------- ícono de la barra lateral
cambio("texto",
       'def icono_nota(tam, color, radio=8, escala_nota=0.5, '
       'color_nota=(255, 255, 255, 235)):',
       'def icono_nota(tam, color, radio=8, escala_nota=0.5, '
       'color_nota=(255, 255, 255, 235), simbolo="♪"):')
cambio("texto", '"♪", font=fuente,', 'simbolo, font=fuente,')
cambio("despues", "def color_playlist(playlist):",
       '    if playlist.get("virtual"):\n'
       '        return ACENTO')
cambio("texto", "icono_nota(36, color_playlist(playlist), 8, 0.5)",
       'icono_nota(\n'
       '                36, color_playlist(playlist), 8, 0.5,\n'
       '                simbolo="♥" if playlist.get("virtual") else "♪"\n'
       '            )')

# ------------------------------------------------ tabla: nueva columna
cambio("linea", "frame.grid_columnconfigure(4, minsize=COL_DUR)",
       "    frame.grid_columnconfigure(4, minsize=COL_CORAZON)\n"
       "    frame.grid_columnconfigure(5, minsize=COL_DUR)")
cambio("texto", "self.h_dur.grid(row=0, column=4,",
       "self.h_dur.grid(row=0, column=5,")
cambio("texto",
       "def __init__(self, padre, al_clic, f_titulo, f_texto):",
       "def __init__(self, padre, al_clic, f_titulo, f_texto,\n"
       "                 al_corazon=None, es_favorito=None):")
cambio("despues", "self.al_clic = al_clic",
       "        self.al_corazon = al_corazon\n"
       "        self.es_favorito = es_favorito")
cambio("linea", "self.dur.grid(row=0, column=4",
       '        self.dur.grid(row=0, column=5, sticky="e", padx=(0, 16))\n'
       '\n'
       '        # El corazón no está en self.widgets: su clic no reproduce la\n'
       '        # canción, la marca o desmarca como «Me gusta».\n'
       '        self.corazon = tk.Label(\n'
       '            self.marco, bg=FONDO, fg=TEXTO_SUAVE,\n'
       '            font=(FUENTE_ICO, 12), cursor="hand2", width=3\n'
       '        )\n'
       '        self.corazon.grid(row=0, column=4, sticky="nsew")\n'
       '        self.corazon.bind("<Button-1>", self._clic_corazon)\n'
       '        self.corazon.bind("<Enter>", self._entrar)\n'
       '        self.corazon.bind("<Leave>", self._salir)')
cambio("antes", "def _entrar(self, e=None):",
       "    def _clic_corazon(self, e=None):\n"
       "        if self.indice is not None and self.al_corazon:\n"
       "            self.al_corazon(self.indice)\n"
       '        return "break"\n')
cambio("despues",
       "self.lbl_titulo.config(fg=ACENTO_HOVER if self.sonando else TEXTO)",
       "\n"
       "        me_gusta = bool(\n"
       "            self.es_favorito and self.video_id\n"
       "            and self.es_favorito(self.video_id)\n"
       "        )\n"
       "        self.corazon.config(bg=fondo)\n"
       "        if me_gusta:\n"
       '            self.corazon.config(text=glifo("corazon_lleno"), fg=ACENTO_HOVER)\n'
       "        elif self.hover:\n"
       '            self.corazon.config(text=glifo("corazon"), fg=TEXTO_SUAVE)\n'
       "        else:\n"
       '            self.corazon.config(text="")')

# --------------------------------------------- lista de canciones
cambio("texto",
       "def __init__(self, padre, al_reproducir, al_ordenar, cache=None):",
       "def __init__(self, padre, al_reproducir, al_ordenar, cache=None,\n"
       "                 al_favorito=None, es_favorito=None):")
cambio("despues", "self.al_ordenar = al_ordenar",
       "        self.al_favorito = al_favorito\n"
       "        self.es_favorito = es_favorito")
cambio("bloque",
       "    def _asegurar_filas(self, cantidad):\n"
       "        while len(self.filas) < cantidad:\n"
       "            self.filas.append(\n"
       "                FilaCancion(\n"
       "                    self.vista, self.al_reproducir,\n"
       "                    self.f_titulo, self.f_texto\n"
       "                )\n"
       "            )\n",
       "    def _asegurar_filas(self, cantidad):\n"
       "        while len(self.filas) < cantidad:\n"
       "            self.filas.append(\n"
       "                FilaCancion(\n"
       "                    self.vista, self.al_reproducir,\n"
       "                    self.f_titulo, self.f_texto,\n"
       "                    self._clic_corazon, self.es_favorito\n"
       "                )\n"
       "            )\n"
       "\n"
       "    def _clic_corazon(self, indice):\n"
       "        if self.al_favorito and 0 <= indice < len(self.pistas):\n"
       "            self.al_favorito(self.pistas[indice])\n"
       "\n"
       "    def repintar_filas(self):\n"
       '        """Vuelve a dibujar los corazones de las filas visibles."""\n'
       "        for fila in self.filas:\n"
       "            if fila.indice is not None:\n"
       "                fila._pintar()\n")
cambio("texto", "ancho - COL_NUM - COL_MINI - COL_ARTISTA - COL_DUR - 28, 60",
       "ancho - COL_NUM - COL_MINI - COL_ARTISTA - COL_CORAZON - COL_DUR - 28, 60")
cambio("texto", "cache=self.cache_miniaturas",
       "cache=self.cache_miniaturas,\n"
       "            al_favorito=self.alternar_favorito,\n"
       "            es_favorito=self.es_favorito")

# ----------------------------------------------- Reproductor: datos
cambio("despues", "self.cargar_playlists_guardadas()",
       "\n"
       "        # --- Favoritos: «Me gusta» es una playlist automática ---\n"
       "        self.me_gusta = {\n"
       '            "nombre": "Me gusta", "url": "", "pistas": [],\n'
       '            "no_disponibles": set(), "virtual": True\n'
       "        }\n"
       "        self.favoritos = []        # canciones con corazón (la última primero)\n"
       "        self.ids_favoritos = set()\n"
       "        self.cargar_favoritos()")
cambio("bloque",
       "        # Pantalla inicial\n"
       "        self.lateral.refrescar(\n"
       "            self.playlists, self.playlist_actual, self.playlist_sonando\n"
       "        )\n",
       "        # Pantalla inicial\n"
       "        self._refrescar_lateral()\n")
cambio("bloque",
       "    def _refrescar_lateral(self):\n"
       "        self.lateral.refrescar(\n"
       "            self.playlists, self.playlist_actual, self.playlist_sonando\n"
       "        )\n",
       "    def _refrescar_lateral(self):\n"
       "        self.lateral.refrescar(\n"
       "            [self.me_gusta] + self.playlists,\n"
       "            self.playlist_actual, self.playlist_sonando\n"
       "        )\n")

FAVORITOS = '''    # ==========================================================
    # FAVORITOS («Me gusta»)
    # ==========================================================
    def cargar_favoritos(self):
        self.favoritos = []
        try:
            datos = json.loads(ARCHIVO_FAVORITOS.read_text(encoding="utf-8"))
        except FileNotFoundError:
            datos = []
        except Exception:
            # Archivo dañado: se guarda una copia antes de empezar de cero.
            try:
                ARCHIVO_FAVORITOS.replace(ARCHIVO_FAVORITOS.with_suffix(".bak"))
            except OSError:
                pass
            datos = []
        if not isinstance(datos, list):
            datos = []

        vistos = set()
        for p in datos:
            if (
                isinstance(p, list) and len(p) >= 4
                and p[0] and p[1] and str(p[1]) not in vistos
            ):
                vistos.add(str(p[1]))
                self.favoritos.append(
                    (str(p[0]), str(p[1]), str(p[2] or ""), p[3])
                )
        self.ids_favoritos = vistos

    def guardar_favoritos(self):
        try:
            ARCHIVO_FAVORITOS.write_text(
                json.dumps(
                    [list(p) for p in self.favoritos],
                    ensure_ascii=False, indent=2
                ),
                encoding="utf-8"
            )
        except Exception as e:
            messagebox.showerror(
                "Error", f"No se pudieron guardar los Me gusta:\\n{e}"
            )

    def es_favorito(self, video_id):
        return video_id in self.ids_favoritos

    def _ids_no_disponibles(self):
        """Canciones que no se pueden reproducir, en cualquier playlist."""
        ids = set(self.me_gusta.get("no_disponibles", set()))
        for p in self.playlists:
            ids |= set(p.get("no_disponibles", set()))
        return ids

    def _pistas_me_gusta(self):
        ocultas = self._ids_no_disponibles()
        return [p for p in self.favoritos if p[1] not in ocultas]

    def alternar_favorito(self, pista):
        """Marca o desmarca una canción como «Me gusta»."""
        video_id = pista[1]
        if video_id in self.ids_favoritos:
            self.favoritos = [p for p in self.favoritos if p[1] != video_id]
            self.ids_favoritos.discard(video_id)
            self.mensaje("Quitada de Me gusta")
        else:
            self.favoritos.insert(0, tuple(pista[:4]))
            self.ids_favoritos.add(video_id)
            self.mensaje("Añadida a Me gusta")
        self.guardar_favoritos()
        # Dentro de «Me gusta» la fila no desaparece al instante (así la
        # lista no salta); se actualiza al volver a abrirla.
        self.lista.repintar_filas()
        self._refrescar_corazon_barra()

    def alternar_favorito_actual(self):
        """Corazón de la barra inferior: la canción que suena."""
        if not self.video_actual:
            return
        pista = next((p for p in self.cola if p[1] == self.video_actual), None)
        if pista is not None:
            self.alternar_favorito(pista)

    def _refrescar_corazon_barra(self):
        activo = bool(self.video_actual) and self.es_favorito(self.video_actual)
        self.btn_corazon.set_icono("corazon_lleno" if activo else "corazon")
        self.btn_corazon.set_activo(activo)

'''
cambio("antes", "def _indice_de(self, playlist):", FAVORITOS)

cambio("despues", "def pistas_disponibles_de_playlist(self, playlist):",
       '        if playlist.get("virtual"):\n'
       '            return self._pistas_me_gusta()')
cambio("despues", 'clave = self.ajustes.get("ultima_playlist")',
       '        if clave == self.me_gusta["nombre"]:\n'
       '            return self.me_gusta')
cambio("despues", 'self.lbl_nombre.config(text=cortar(playlist["nombre"], 30))',
       '        if playlist.get("virtual"):\n'
       '            self.btn_mas.pack_forget()   # «Me gusta» no se renombra ni se borra\n'
       '        else:\n'
       '            self.btn_mas.pack(side="left")')
cambio("despues", "def mostrar_menu(self, playlist, x, y):",
       '        if playlist is not None and playlist.get("virtual"):\n'
       '            return')
cambio("despues", 'playlist.setdefault("no_disponibles", set()).add(video_id)',
       '\n'
       '        if playlist.get("virtual"):\n'
       '            # Una canción de «Me gusta» que no se puede reproducir también\n'
       '            # se oculta en las playlists de donde viene.\n'
       '            for otra in self.playlists:\n'
       '                if any(p[1] == video_id for p in otra.get("pistas", [])):\n'
       '                    otra.setdefault("no_disponibles", set()).add(video_id)\n'
       '            if (\n'
       '                self.playlist_actual is not None\n'
       '                and self.playlist_actual is not playlist\n'
       '            ):\n'
       '                self.pistas_originales = self.pistas_disponibles_de_playlist(\n'
       '                    self.playlist_actual\n'
       '                )\n'
       '                self.aplicar_vista()')
cambio("despues", 'self.estado.pack(fill="x")',
       '        self.btn_corazon = BotonIcono(\n'
       '            izq, "corazon", self.alternar_favorito_actual,\n'
       '            tam=14, fondo=PANEL\n'
       '        )\n'
       '        self.btn_corazon.pack(side="left", padx=(10, 0))')
cambio("antes", "self._ticks += 1",
       "        self._refrescar_corazon_barra()\n")
cambio("antes", "self.lbl_resumen.config(text=texto)",
       "        if self.playlist_actual is self.me_gusta and not self.pistas_originales:\n"
       '            texto = "Aún no hay canciones. Pulsa el corazón de una canción para añadirla"')


def aplicar(texto):
    for n, (tipo, buscar, nuevo) in enumerate(CAMBIOS, 1):
        if texto.count(buscar) != 1:
            veces = texto.count(buscar)
            raise SystemExit(
                f"\nNo se cambió nada.\n"
                f"El cambio {n} no encontró su lugar en tu código "
                f"(el texto aparece {veces} veces, debía ser 1):\n    {buscar!r}\n"
                f"Pásale este mensaje a Claude para ajustarlo."
            )
        if tipo == "texto" or tipo == "bloque":
            texto = texto.replace(buscar, nuevo)
            continue
        lineas = texto.split("\n")
        i = next(k for k, l in enumerate(lineas) if buscar in l)
        if tipo == "despues":
            lineas[i + 1:i + 1] = nuevo.split("\n")
        elif tipo == "antes":
            lineas[i:i] = nuevo.split("\n")
        elif tipo == "linea":
            lineas[i:i + 1] = nuevo.split("\n")
        texto = "\n".join(lineas)
    return texto


def main():
    if not ARCHIVO.exists():
        raise SystemExit(f"No encuentro {ARCHIVO}. Ejecútalo dentro de la carpeta de tu proyecto.")

    crudo = ARCHIVO.read_bytes().decode("utf-8")
    crlf = "\r\n" in crudo
    texto = crudo.replace("\r\n", "\n")

    if "COL_CORAZON" in texto:
        raise SystemExit("Tu archivo ya tiene los Favoritos aplicados. No se cambió nada.")

    nuevo = aplicar(texto)
    compile(nuevo, str(ARCHIVO), "exec")   # comprueba que no quedó con errores

    copia = ARCHIVO.with_name("reproductor_antes_de_favoritos.py")
    copia.write_bytes(crudo.encode("utf-8"))
    if crlf:
        nuevo = nuevo.replace("\n", "\r\n")
    ARCHIVO.write_bytes(nuevo.encode("utf-8"))
    print(f"Listo. Se aplicaron {len(CAMBIOS)} cambios a {ARCHIVO.name}.")
    print(f"Copia de seguridad: {copia.name}")


if __name__ == "__main__":
    main()
