# Otium

🇪🇸 Español · [🇬🇧 English](README.en.md)

**Reproductor de música de escritorio para tu tiempo de calma.**

*Otium* es la palabra latina para el tiempo libre dedicado a lo que alimenta el alma. Esta aplicación nace de una idea simple: escuchar música es volver a casa, un refugio. Pega el enlace de una playlist de YouTube y escúchala en un solo lugar, con una interfaz oscura y tranquila.

<!-- Reemplaza esta línea por una captura de pantalla: ![Otium](captura.png) -->

## Funciones

- Importa playlists de YouTube a partir de su enlace y las guarda en tu computador.
- Reproduce solo el audio, en streaming, sin descargar las canciones.
- Pestaña de playlists guardadas, con las carátulas de cada canción.
- Búsqueda por título o artista y orden por título, artista o duración.
- Funciona con playlists grandes (cientos de canciones): solo dibuja las filas visibles.
- Temas de color, con opción de elegir tu propio color de acento.
- Modo aleatorio, repetir lista o repetir una canción, control de volumen y barra de progreso.
- Oculta automáticamente las canciones que no se pueden reproducir (privadas, eliminadas o con restricción de edad).
- Atajos de teclado: `Espacio` (play/pausa), `←` `→` (anterior/siguiente), `↑` `↓` (volumen).

## Tecnologías

Python · Tkinter · [python-vlc](https://pypi.org/project/python-vlc/) · [yt-dlp](https://github.com/yt-dlp/yt-dlp) · Pillow

## Instalación

Requisitos: Windows 10/11, [Python 3.10 o superior](https://www.python.org/downloads/) y [VLC](https://www.videolan.org/vlc/) instalado (la versión de 64 bits si tu Python es de 64 bits).

```bash
git clone https://github.com/JavieraGGarcia/otium-music-player.git
cd otium-music-player
pip install python-vlc yt-dlp pillow
python reproductor.py
```

## Uso

1. Pulsa **Nueva playlist** en la barra lateral y pega el enlace de una playlist de YouTube (pública o no listada).
2. Haz clic en una canción para reproducirla.
3. Tus playlists (`playlists.json`) y tus ajustes de tema (`ajustes.json`) quedan guardados en `%APPDATA%\Otium\`, así que cada persona que use la app tiene los suyos.

## Próximos pasos

- Más temas de color.
- Importar playlists desde un archivo CSV (por ejemplo, exportadas desde otros servicios).
- Generar un ejecutable (`.exe`).

## Nota

Proyecto personal hecho para aprender y para uso propio. Otium no descarga ni redistribuye música: reproduce en streaming el contenido de YouTube. Úsalo respetando los términos de uso de YouTube.

## Autora

Javiera Gutiérrez García · [GitHub](https://github.com/JavieraGGarcia) · [LinkedIn](https://www.linkedin.com/in/javiera-gutierrez-garc%C3%ADa-00733b415/)