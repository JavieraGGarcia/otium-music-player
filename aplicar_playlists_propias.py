"""
Agrega a Otium las PLAYLISTS PROPIAS (listas armadas a mano).

Qué hace:
  - El botón «Nueva playlist» (el cuadrado punteado con «+», al final de la
    lista) ahora ofrece: «Playlist propia (vacía)» o «Desde un link de
    YouTube». Cuando hay tantas playlists que no caben, el botón queda
    fijo (flotando) en la parte de abajo de la lista para no perderse.
  - Clic derecho en cualquier canción:
        · Añadir a playlist  ->  elige una playlist propia o crea una nueva
        · Añadir / Quitar de Mis favoritos
        · Quitar de esta playlist (solo dentro de una playlist propia)
  - Las playlists propias se guardan en playlists.json junto a las demás,
    se pueden renombrar y eliminar desde el menú de la barra lateral.

Requisito: tener ya aplicados los Favoritos (aplicar_favoritos.py).

Uso (en la carpeta de reproductor.py):
    python aplicar_playlists_propias.py
Se crea una copia: reproductor_antes_de_propias.py
"""
import sys
from pathlib import Path

ARCHIVO = Path(sys.argv[1] if len(sys.argv) > 1 else "reproductor.py")

CAMBIOS = []


def cambio(tipo, buscar, nuevo):
    # despues -> inserta líneas después de la línea que contiene `buscar`
    # antes   -> inserta líneas antes de la línea que contiene `buscar`
    # texto   -> reemplaza solo ese fragmento
    # bloque  -> reemplaza un bloque exacto de varias líneas
    CAMBIOS.append((tipo, buscar, nuevo))


# ------------------------------------- barra lateral: botón «Nueva playlist»
cambio("texto", "al_nueva=self.nueva_playlist,",
       "al_nueva=self.menu_nueva_playlist,")

# ------------------------------------------------------------- guardado
cambio("texto", '"url": p["url"],',
       '"url": p["url"],\n                "propia": bool(p.get("propia")),')
cambio("texto",
       '                    "no_disponibles": no_disponibles\n                })',
       '                    "no_disponibles": no_disponibles,\n'
       '                    "propia": bool(p.get("propia"))\n'
       "                })")

# Las playlists propias no se «actualizan» desde YouTube.
cambio("bloque",
       "        menu.add_command(\n"
       '            label="Actualizar",\n'
       "            command=lambda: self.actualizar_playlist(playlist)\n"
       "        )\n",
       '        if not playlist.get("propia"):\n'
       "            menu.add_command(\n"
       '                label="Actualizar",\n'
       "                command=lambda: self.actualizar_playlist(playlist)\n"
       "            )\n")

# ------------------------------------------- lista de canciones: clic derecho
cambio("bloque",
       "                    self._clic_corazon, self.es_favorito\n"
       "                )\n"
       "            )\n",
       "                    self._clic_corazon, self.es_favorito\n"
       "                )\n"
       "            )\n"
       "            nueva = self.filas[-1]\n"
       "            for w in nueva.widgets + [nueva.corazon]:\n"
       "                w.bind(\n"
       '                    "<Button-3>",\n'
       "                    lambda e, f=nueva: self._menu_derecho(f, e)\n"
       "                )\n")
cambio("antes", "def _clic_corazon(self, indice):",
       "    def _menu_derecho(self, fila, e):\n"
       '        cb = getattr(self, "al_menu_cancion", None)\n'
       "        if (\n"
       "            cb and fila.indice is not None\n"
       "            and 0 <= fila.indice < len(self.pistas)\n"
       "        ):\n"
       "            cb(fila.indice, e.x_root, e.y_root)\n"
       '        return "break"\n')
cambio("despues",
       'self.lista.pack(fill="both", expand=True, padx=(16, 8), pady=(0, 8))',
       "        self.lista.al_menu_cancion = self.mostrar_menu_cancion")

# ------------------------------------------------ mensaje de playlist vacía
cambio("antes", "self.lbl_resumen.config(text=texto)",
       "        if (\n"
       '            self.playlist_actual is not None\n'
       '            and self.playlist_actual.get("propia")\n'
       "            and not self.pistas_originales\n"
       "        ):\n"
       '            texto = ("Playlist vacía. Clic derecho en una canción y elige "\n'
       '                     "«Añadir a playlist»")')

# --------------------------------------------------------- métodos nuevos
PROPIAS = '''    # ==========================================================
    # PLAYLISTS PROPIAS
    # ==========================================================
    def _menu_estilo(self, padre=None):
        return tk.Menu(
            padre or self.root, tearoff=0, bg=PANEL, fg=TEXTO,
            activebackground=ACENTO, activeforeground=color_sobre(ACENTO),
            bd=0, relief="flat", font=(FUENTE, 10)
        )

    def menu_nueva_playlist(self):
        """Botón «Nueva playlist» de la barra lateral."""
        x = self.root.winfo_pointerx()
        y = self.root.winfo_pointery()
        menu = self._menu_estilo()
        menu.add_command(
            label="Playlist propia (vacía)",
            command=self.nueva_playlist_propia
        )
        menu.add_command(
            label="Desde un link de YouTube",
            command=self.nueva_playlist
        )
        try:
            menu.tk_popup(x, y)
        finally:
            menu.grab_release()

    def _propias(self):
        return [p for p in self.playlists if p.get("propia")]

    def nueva_playlist_propia(self, con_pista=None):
        """Pide un nombre y crea una playlist propia (opcionalmente con una
        primera canción)."""
        ventana = tk.Toplevel(self.root)
        ventana.title("Nueva playlist propia")
        ventana.configure(bg=FONDO)
        ventana.resizable(False, False)
        ventana.transient(self.root)
        ventana.grab_set()

        tk.Label(
            ventana, text="Nombre de la playlist:", bg=FONDO, fg=TEXTO,
            font=(FUENTE, 10, "bold")
        ).pack(padx=22, pady=(18, 6), anchor="w")

        entrada = tk.Entry(
            ventana, width=40, bg=PANEL, fg=TEXTO, insertbackground=TEXTO,
            relief="flat", font=(FUENTE, 10)
        )
        entrada.pack(padx=22, fill="x", ipady=6)
        entrada.insert(0, "Mi playlist")
        entrada.select_range(0, "end")

        def crear():
            nombre = entrada.get().strip()
            if not nombre:
                return
            playlist = {
                "nombre": nombre,
                "url": "",
                "pistas": [],
                "no_disponibles": set(),
                "propia": True
            }
            if con_pista is not None:
                playlist["pistas"].append(tuple(con_pista[:4]))
            self.playlists.append(playlist)
            self.guardar_playlists()
            ventana.destroy()
            self.abrir_playlist(playlist)
            if con_pista is not None:
                self.mensaje(f"Añadida a {cortar(nombre, 24)}")

        self.boton(
            ventana, "Crear", crear, ancho=10, acento=True
        ).pack(pady=14)

        entrada.focus_set()
        ventana.bind("<Return>", lambda e: crear())
        ventana.bind("<Escape>", lambda e: ventana.destroy())

    def agregar_a_playlist_propia(self, playlist, pista):
        if any(p[1] == pista[1] for p in playlist["pistas"]):
            self.mensaje(f"Ya estaba en {cortar(playlist['nombre'], 24)}")
            return
        playlist["pistas"].append(tuple(pista[:4]))
        self.guardar_playlists()
        self.mensaje(f"Añadida a {cortar(playlist['nombre'], 24)}")
        self._refrescar_si_abierta(playlist)

    def quitar_de_playlist_propia(self, playlist, pista):
        playlist["pistas"] = [
            p for p in playlist["pistas"] if p[1] != pista[1]
        ]
        self.guardar_playlists()
        self.mensaje(f"Quitada de {cortar(playlist['nombre'], 24)}")
        self._refrescar_si_abierta(playlist)

    def _refrescar_si_abierta(self, playlist):
        if playlist is self.playlist_actual:
            self.pistas_originales = self.pistas_disponibles_de_playlist(
                playlist
            )
            self.aplicar_vista()

    def mostrar_menu_cancion(self, indice, x, y):
        """Clic derecho sobre una canción de la lista."""
        if not (0 <= indice < len(self.lista.pistas)):
            return
        pista = self.lista.pistas[indice]
        actual = self.playlist_actual

        menu = self._menu_estilo()
        sub = self._menu_estilo(menu)
        for p in self._propias():
            if p is actual:
                continue
            sub.add_command(
                label=cortar(p["nombre"], 28),
                command=lambda p=p: self.agregar_a_playlist_propia(p, pista)
            )
        if sub.index("end") is not None:
            sub.add_separator()
        sub.add_command(
            label="Nueva playlist propia…",
            command=lambda: self.nueva_playlist_propia(con_pista=pista)
        )
        menu.add_cascade(label="Añadir a playlist", menu=sub)

        if self.es_favorito(pista[1]):
            menu.add_command(
                label="Quitar de Mis favoritos",
                command=lambda: self.alternar_favorito(pista)
            )
        else:
            menu.add_command(
                label="Añadir a Mis favoritos",
                command=lambda: self.alternar_favorito(pista)
            )

        if actual is not None and actual.get("propia"):
            menu.add_separator()
            menu.add_command(
                label="Quitar de esta playlist",
                command=lambda: self.quitar_de_playlist_propia(actual, pista)
            )
        try:
            menu.tk_popup(x, y)
        finally:
            menu.grab_release()

'''
cambio("antes", "def mostrar_menu(self, playlist, x, y):",
       PROPIAS.rstrip("\n").replace("\n    # ====", "\n    # ====")
       + "\n")

# ======================================================================
# Botón «Nueva playlist» (el cuadrado punteado): se mantiene al final de la
# lista y, cuando la lista no cabe, pasa a una fila fija abajo («flotante»).
# ======================================================================
CAMBIOS_BOTON = []


def cambio_boton(tipo, buscar, nuevo):
    CAMBIOS_BOTON.append((tipo, buscar, nuevo))


cambio_boton("bloque",
       "        self.canvas.pack(fill=\"both\", expand=True)\n"
       "        self.interior = tk.Frame(self.canvas, bg=PANEL)\n",
       "        # Fila «Nueva playlist» flotante: se muestra solo cuando la lista\n"
       "        # de playlists es más larga que el panel.\n"
       "        self.flotante = tk.Frame(marco, bg=PANEL)\n"
       "        self._flota = None\n"
       "        self._flot_hecha = False\n"
       "        self._n_items = 0\n"
       "        self.canvas.pack(fill=\"both\", expand=True)\n"
       "        self.interior = tk.Frame(self.canvas, bg=PANEL)\n")
cambio_boton("texto",
       "            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox(\"all\"))",
       "            lambda e: self._al_cambiar_interior()")
cambio_boton("texto",
       "            lambda e: self.canvas.itemconfig(self.ventana, width=e.width)\n        )\n\n    def abrir_apariencia",
       "            lambda e: self._al_cambiar_canvas(e)\n        )\n\n    def abrir_apariencia")
cambio_boton("antes", "    def _crear_nueva(self):",
       "    def _al_cambiar_interior(self):\n"
       "        self.canvas.configure(scrollregion=self.canvas.bbox(\"all\"))\n"
       "\n"
       "    def _al_cambiar_canvas(self, e):\n"
       "        self.canvas.itemconfig(self.ventana, width=e.width)\n"
       "        self._ajustar_nueva()\n"
       "\n"
       "    def _ajustar_nueva(self):\n"
       "        \"\"\"Si hay más playlists que espacio, «Nueva playlist» queda fija\n"
       "        abajo (flotando); si caben, va justo después de la última.\"\"\"\n"
       "        if self.apariencia or not hasattr(self, \"flotante\"):\n"
       "            return\n"
       "        try:\n"
       "            disponible = self.canvas.master.winfo_height()\n"
       "            if disponible <= 1:\n"
       "                return\n"
       "            desborda = (self._n_items + 1) * 54 + 4 > disponible\n"
       "            if desborda == self._flota:\n"
       "                return\n"
       "            self._flota = desborda\n"
       "            if desborda:\n"
       "                if not self._flot_hecha:\n"
       "                    tk.Frame(\n"
       "                        self.flotante, bg=PANEL_HOVER, height=1\n"
       "                    ).pack(fill=\"x\", padx=10, pady=(0, 4))\n"
       "                    self._crear_nueva(self.flotante)\n"
       "                    self.flotante.pack_propagate(True)\n"
       "                    self._flot_hecha = True\n"
       "                self._fila_inline.pack_forget()\n"
       "                self.flotante.pack(\n"
       "                    side=\"bottom\", fill=\"x\", pady=(0, 6),\n"
       "                    before=self.canvas\n"
       "                )\n"
       "            else:\n"
       "                self.flotante.pack_forget()\n"
       "                self._fila_inline.pack(fill=\"x\", padx=10, pady=1)\n"
       "        except tk.TclError:\n"
       "            pass\n")
cambio_boton("bloque",
       "    def _crear_nueva(self):\n"
       "        fila = tk.Frame(self.interior, bg=PANEL, height=52, cursor=\"hand2\")\n",
       "    def _crear_nueva(self, padre=None):\n"
       "        fila = tk.Frame(\n"
       "            padre or self.interior, bg=PANEL, height=52, cursor=\"hand2\"\n"
       "        )\n"
       "        if padre is None:\n"
       "            self._fila_inline = fila\n")
cambio_boton("bloque",
       "        self._crear_nueva()\n"
       "        self.canvas.yview_moveto(0)",
       "        self._n_items = len(playlists)\n"
       "        self._crear_nueva()\n"
       "        self._flota = None\n"
       "        self.canvas.yview_moveto(0)\n"
       "        self.after_idle(self._ajustar_nueva)")


# ======================================================================
# Si ya tenías la versión anterior (botón «+» junto a «Mis playlists»), se
# devuelve esa parte a como estaba antes de aplicar lo nuevo.
# ======================================================================
V1_ENCABEZADO = (
    "        self.fila_cab = tk.Frame(self, bg=PANEL)\n"
    '        self.fila_cab.pack(fill="x", padx=(20, 10), pady=(18, 6))\n'
    "        self.cabecera = tk.Label(\n"
    '            self.fila_cab, text="Mis playlists", bg=PANEL, fg=TEXTO_SUAVE,\n'
    '            font=(FUENTE, 10, "bold"), anchor="w"\n'
    "        )\n"
    '        self.cabecera.pack(side="left")\n'
    "        # «+» justo a la derecha del título: crea una playlist nueva\n"
    "        self.btn_nueva = BotonIcono(\n"
    '            self.fila_cab, "nuevo", lambda: self.al_nueva(),\n'
    "            tam=12, fondo=PANEL\n"
    "        )\n"
    '        self.btn_nueva.pack(side="left", padx=(2, 0))\n')
ORIGINAL_ENCABEZADO = (
    "        self.cabecera = tk.Label(\n"
    '            self, text="Mis playlists", bg=PANEL, fg=TEXTO_SUAVE,\n'
    '            font=(FUENTE, 10, "bold"), anchor="w"\n'
    "        )\n"
    '        self.cabecera.pack(fill="x", padx=20, pady=(22, 10))\n')
V1_MENU_POS = (
    '        """Botón «+» junto a «Mis playlists»."""\n'
    "        b = self.lateral.btn_nueva\n"
    "        x = b.winfo_rootx()\n"
    "        y = b.winfo_rooty() + b.winfo_height()\n")
NUEVO_MENU_POS = (
    '        """Botón «Nueva playlist» de la barra lateral."""\n'
    "        x = self.root.winfo_pointerx()\n"
    "        y = self.root.winfo_pointery()\n")


def revertir_v1(texto):
    pares = [
        (V1_ENCABEZADO, ORIGINAL_ENCABEZADO),
        ("        self.btn_nueva.pack_forget()\n", ""),
        ('        self.btn_nueva.pack(side="left", padx=(2, 0))\n', ""),
        ("            self._crear_item(p, p is actual, p is sonando)\n"
         "        self.canvas.yview_moveto(0)",
         "            self._crear_item(p, p is actual, p is sonando)\n"
         "        self._crear_nueva()\n"
         "        self.canvas.yview_moveto(0)"),
        ("Pulsa «+» junto a «Mis playlists» para crear una.",
         "Pulsa «Nueva playlist» en la barra lateral para añadir una."),
        (V1_MENU_POS, NUEVO_MENU_POS),
    ]
    for viejo, nuevo in pares:
        if texto.count(viejo) != 1:
            raise SystemExit(
                "\nNo se cambió nada.\n"
                "No pude devolver el botón «+» a su lugar original "
                f"(fragmento encontrado {texto.count(viejo)} veces):\n    {viejo[:80]!r}\n"
                "Pásale este mensaje a Claude para ajustarlo."
            )
        texto = texto.replace(viejo, nuevo)
    return texto



def aplicar(texto, cambios=None):
    cambios = CAMBIOS if cambios is None else cambios
    for n, (tipo, buscar, nuevo) in enumerate(cambios, 1):
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

    if "_ajustar_nueva" in texto:
        raise SystemExit("Tu archivo ya tiene las playlists propias. No se cambió nada.")
    if "COL_CORAZON" not in texto:
        raise SystemExit(
            "Primero hay que aplicar los Favoritos (aplicar_favoritos.py). "
            "No se cambió nada."
        )

    if "menu_nueva_playlist" in texto:
        # Versión anterior de este script (botón «+» arriba): se actualiza.
        base = revertir_v1(texto)
        nuevo = aplicar(base, CAMBIOS_BOTON)
        total = len(CAMBIOS_BOTON)
    else:
        nuevo = aplicar(aplicar(texto), CAMBIOS_BOTON)
        total = len(CAMBIOS) + len(CAMBIOS_BOTON)
    compile(nuevo, str(ARCHIVO), "exec")   # comprueba que no quedó con errores

    copia = ARCHIVO.with_name("reproductor_antes_de_propias.py")
    copia.write_bytes(crudo.encode("utf-8"))
    if crlf:
        nuevo = nuevo.replace("\n", "\r\n")
    ARCHIVO.write_bytes(nuevo.encode("utf-8"))
    print(f"Listo. Se aplicaron {total} cambios a {ARCHIVO.name}.")
    print(f"Copia de seguridad: {copia.name}")


if __name__ == "__main__":
    main()
