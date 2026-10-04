"""Discord Rich Presence para Otium: muestra en tu perfil lo que estás escuchando.

Requisitos
----------
1. pip install -U pypresence
2. Una aplicación de Discord (https://discord.com/developers/applications).
   Su «Application ID» es el client_id, y su nombre es lo que se ve en tu
   perfil: «Escuchando Otium».

Cómo funciona
-------------
Otium llama a `actualizar(estado)` cada medio segundo (desde su `vigilar`).
Este módulo decide si hay algo nuevo que contar a Discord (otra canción,
pausa, un salto en la barra de progreso) y, si lo hay, se lo pasa a un hilo
en segundo plano que habla con Discord. Así la ventana nunca se queda
esperando, aunque Discord esté cerrado o tarde en responder.
"""
import queue
import threading
import time

INTERVALO_MIN = 5.0    # segundos mínimos entre dos envíos (Discord limita a 5 cada 20 s)
SALTO_MS = 4000        # desviación de la posición a partir de la cual se asume un salto
REINTENTO_S = 15.0     # espera antes de volver a intentar conectar con Discord
MAX_TEXTO = 128        # límite de Discord para cada línea de texto


def _importar_pypresence():
    """Devuelve (Presence, ActivityType); None si no está instalado.
    ActivityType solo existe en pypresence 4.3 o más nuevo."""
    try:
        from pypresence import Presence
    except Exception:
        return None, None
    try:
        from pypresence import ActivityType
    except Exception:
        ActivityType = None
    return Presence, ActivityType


def _texto(texto, vacio):
    """Texto válido para Discord: sin saltos de línea, de 2 a 128 caracteres."""
    texto = " ".join(str(texto or "").split())
    if not texto:
        texto = vacio
    if len(texto) < 2:
        texto += " ♪"
    if len(texto) > MAX_TEXTO:
        texto = texto[: MAX_TEXTO - 1].rstrip() + "…"
    return texto


def construir_actividad(estado, ahora, con_boton=True):
    """Convierte el estado del reproductor en los datos que pide Discord.

    estado: {"id", "titulo", "artista", "duracion" (s), "pos_ms",
             "reproduciendo", "playlist"}
    """
    video_id = estado["id"]
    artista = _texto(estado.get("artista"), "Artista desconocido")
    reproduciendo = bool(estado.get("reproduciendo"))

    actividad = {
        "details": _texto(estado.get("titulo"), "Sin título"),
        "state": artista if reproduciendo else _texto(f"{artista} · en pausa", ""),
        "large_image": f"https://i.ytimg.com/vi/{video_id}/mqdefault.jpg",
        "large_text": _texto(estado.get("playlist"), "Otium"),
    }

    if reproduciendo:
        # Discord dibuja la barra de progreso con estas dos marcas de tiempo.
        pos = max(int(estado.get("pos_ms") or 0), 0) / 1000
        inicio = int(ahora - pos)
        actividad["start"] = inicio
        duracion = estado.get("duracion")
        if duracion and duracion > 0 and inicio + duracion > ahora:
            actividad["end"] = int(inicio + duracion)

    if con_boton:
        actividad["buttons"] = [{
            "label": "Escuchar en YouTube",
            "url": f"https://www.youtube.com/watch?v={video_id}",
        }]
    return actividad


class PresenciaDiscord:
    def __init__(self, client_id, activo=True):
        self.client_id = str(client_id or "").strip()
        self.activo = bool(activo)
        self._Presence, self._ActivityType = _importar_pypresence()

        self._cola = queue.Queue()
        self._hilo = None
        self._ultimo = None      # lo último que se envió: clave, posición y momento
        self._ultimo_t = 0.0

    # ----------------------------------------------------------
    # Estado (para mostrarlo en la interfaz)
    # ----------------------------------------------------------
    def motivo_no_disponible(self):
        """Texto que explica qué falta, o '' si todo está listo."""
        if self._Presence is None:
            return (
                "Falta instalar pypresence.\n\n"
                "Abre una terminal y ejecuta:\n\n"
                "    pip install -U pypresence\n\n"
                "Después vuelve a abrir Otium."
            )
        if not self.client_id:
            return (
                "Falta el ID de tu aplicación de Discord.\n\n"
                "1. Entra en discord.com/developers/applications\n"
                "2. Pulsa «New Application» y ponle el nombre Otium "
                "(es lo que se verá en tu perfil)\n"
                "3. Copia el «Application ID»\n"
                "4. Pégalo en DISCORD_CLIENT_ID, arriba en el código de Otium"
            )
        return ""

    def disponible(self):
        return not self.motivo_no_disponible()

    def estado_texto(self):
        if not self.disponible():
            return "Sin configurar"
        return "Activado" if self.activo else "Desactivado"

    # ----------------------------------------------------------
    # Uso desde el reproductor
    # ----------------------------------------------------------
    def actualizar(self, estado, ahora=None):
        """Se llama a menudo. 'estado' es None si no hay nada que mostrar."""
        if not self.activo or not self.disponible():
            return
        ahora = time.time() if ahora is None else ahora

        if estado is None:
            # Había algo mostrándose y ya no: se borra.
            if self._ultimo is not None and ahora - self._ultimo_t >= INTERVALO_MIN:
                self._enviar(("clear",))
                self._ultimo = None
                self._ultimo_t = ahora
            return

        clave = (estado["id"], bool(estado["reproduciendo"]))
        cambio = self._ultimo is None or self._ultimo["clave"] != clave

        if not cambio and estado["reproduciendo"]:
            # Mientras suena, la posición avanza sola; si se desvía, hubo un salto.
            esperada = self._ultimo["pos_ms"] + (ahora - self._ultimo["t"]) * 1000
            cambio = abs(estado["pos_ms"] - esperada) > SALTO_MS

        if not cambio:
            return
        if ahora - self._ultimo_t < INTERVALO_MIN:
            return   # demasiado pronto: se reintenta en la siguiente llamada

        self._enviar(("update", construir_actividad(estado, ahora)))
        self._ultimo = {
            "clave": clave,
            "pos_ms": estado["pos_ms"],
            "t": ahora,
        }
        self._ultimo_t = ahora

    def activar(self, valor):
        """Enciende o apaga la función. Al apagar, se borra del perfil."""
        valor = bool(valor)
        if valor == self.activo:
            return
        self.activo = valor
        self._ultimo = None
        if not valor and self._hilo is not None:
            self._enviar(("clear",))

    def cerrar(self):
        """Al cerrar Otium: quita la actividad del perfil y para el hilo."""
        if self._hilo is not None and self._hilo.is_alive():
            self._cola.put(("stop",))
            self._hilo.join(timeout=2.0)

    # ----------------------------------------------------------
    # Hilo que habla con Discord
    # ----------------------------------------------------------
    def _enviar(self, orden):
        if self._hilo is None or not self._hilo.is_alive():
            self._hilo = threading.Thread(
                target=self._bucle, name="discord-presence", daemon=True
            )
            self._hilo.start()
        self._cola.put(orden)

    def _bucle(self):
        rpc = None
        pendiente = None        # última orden que aún no se ha entregado
        proximo_intento = 0.0

        while True:
            ordenes = []
            try:
                ordenes.append(self._cola.get(timeout=1.0))
            except queue.Empty:
                pass
            while True:
                try:
                    ordenes.append(self._cola.get_nowait())
                except queue.Empty:
                    break

            detener = False
            for orden in ordenes:     # solo importa la más reciente
                if orden[0] == "stop":
                    detener = True
                else:
                    pendiente = orden

            if detener:
                if rpc is not None:
                    try:
                        rpc.clear()
                    except Exception:
                        pass
                    self._cerrar_rpc(rpc)
                return

            if pendiente is None:
                continue

            if rpc is None:
                if time.time() < proximo_intento:
                    continue
                rpc = self._conectar()
                if rpc is None:
                    proximo_intento = time.time() + REINTENTO_S
                    continue

            if self._entregar(rpc, pendiente):
                pendiente = None
            else:
                # Discord se cerró o la conexión se cayó: se reconecta luego.
                self._cerrar_rpc(rpc)
                rpc = None
                proximo_intento = time.time() + REINTENTO_S

    def _conectar(self):
        try:
            rpc = self._Presence(self.client_id)
            rpc.connect()
            return rpc
        except Exception:
            return None

    def _entregar(self, rpc, orden):
        try:
            if orden[0] == "clear":
                rpc.clear()
                return True
            datos = dict(orden[1])
            if self._ActivityType is not None:
                datos["activity_type"] = self._ActivityType.LISTENING
            try:
                rpc.update(**datos)
            except TypeError:
                # pypresence antiguo, sin activity_type: se muestra como «Jugando».
                rpc.update(**orden[1])
            return True
        except Exception:
            return False

    @staticmethod
    def _cerrar_rpc(rpc):
        try:
            rpc.close()
        except Exception:
            pass
