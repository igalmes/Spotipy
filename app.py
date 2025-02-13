# Importar los módulos necesarios
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, request, render_template
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Configurar la aplicación Flask
app = Flask(__name__)

# Obtener credenciales desde .env
client_id = os.getenv('SPOTIPY_CLIENT_ID')
client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')
redirect_uri = os.getenv('SPOTIPY_REDIRECT_URI')

# Inicializar la autenticación con Spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri=redirect_uri,
                                               scope='user-library-read'))

# 🔹 Ruta principal (Index)
@app.route('/')
def index():
    return render_template('index.html')

# 🔹 Ruta para buscar un artista
@app.route('/buscar_artista', methods=['GET'])
def buscar_artista():
    artist_name = request.args.get('artist_name')

    if artist_name:
        results = sp.search(q='artist:' + artist_name, type='artist')
        artists = results['artists']['items']

        if len(artists) > 0:
            artist = artists[0]

            artist_info = {
                'id': artist['id'],
                'name': artist['name'],
                'followers': artist['followers']['total'],
                'genres': artist['genres'],
                'popularity': artist['popularity'],
                'spotify_url': artist['external_urls']['spotify'],
                'rank': 101 - artist['popularity']  # Simulación de ranking basado en popularidad
            }

            artist_image = artist['images'][0]['url'] if artist['images'] else None

            return render_template('artist.html', artist_info=artist_info, artist_image=artist_image)
        else:
            return f"No se encontró ningún artista con el nombre '{artist_name}'"
    else:
        return "Error: Debes ingresar un nombre de artista."

# 🔹 Ruta para buscar una canción
@app.route('/buscar_cancion', methods=['GET'])
def buscar_cancion():
    cancion_name = request.args.get('cancion_name')

    if cancion_name:
        results = sp.search(q='track:' + cancion_name, type='track')
        canciones = results['tracks']['items']

        if len(canciones) > 0:
            track = canciones[0]

            track_info = {
                'name': track['name'],
                'artist': track['artists'][0]['name'],
                'album': track['album']['name'],
                'release_date': track['album']['release_date'],
                'popularity': track['popularity'],
                'duration_ms': track['duration_ms'],
                'preview_url': track.get('preview_url'),
                'spotify_url': track['external_urls']['spotify'],
                'album_image': track['album']['images'][0]['url'] if track['album']['images'] else None
            }

            return render_template('index.html', track_info=track_info)
        else:
            return render_template('index.html', error="No se encontró ninguna canción con ese nombre.")
    else:
        return render_template('index.html', error="Error: Debes ingresar el nombre de una canción.")

# 🔹 Ruta para mostrar recomendaciones
@app.route('/recomendaciones')
def mostrar_recomendaciones():
    return render_template('recomendaciones.html', recommended_tracks=[])

# 🚀 **Mover esto al final para evitar problemas**
if __name__ == '__main__':
    app.run(debug=True)
