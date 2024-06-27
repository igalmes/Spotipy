# Importar los módulos necesarios
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, request, render_template

# Configurar la aplicación Flask
app = Flask(__name__)

# Configurar las credenciales de tu aplicación Spotify
client_id = '5765c5b1ae724890b2269e53feb21550'
client_secret = '67cb8c10ac814f2098089d2c7f2df968'
redirect_uri = 'http://localhost:8888/callback'
scope = 'user-library-read'  # Ejemplo de alcance de permisos

# Inicializar el objeto de autenticación de Spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri=redirect_uri,
                                               scope=scope))

# Ruta principal que renderiza el template index.html
@app.route('/')
def hello_world():
    return render_template('index.html')

# Ruta para buscar un artista
@app.route('/buscar_artista', methods=['GET'])
def buscar_artista():
    # Obtener el parámetro 'artist_name' del query string
    artist_name = request.args.get('artist_name')
    
    if artist_name:
        # Realizar la búsqueda del artista en Spotify
        results = sp.search(q='artist:' + artist_name, type='artist')
        artists = results['artists']['items']
        
        if len(artists) > 0:
            # Mostrar el primer artista encontrado
            new_artist = artists[0]
            
            # Obtener la imagen del artista (seleccionamos la primera imagen disponible)
            artist_image = None
            if len(new_artist['images']) > 0:
                artist_image = new_artist['images'][0]['url']
            
            # Obtener los álbumes del artista
            albums = sp.artist_albums(new_artist['id'], album_type='album')
            album_info = []
            
            for album in albums['items']:
                album_details = {
                    'name': album['name'],
                    'release_date': album['release_date'],
                    'total_tracks': album['total_tracks'],
                    'album_type': album['album_type']
                }
                album_info.append(album_details)
            
            # Obtener las canciones más populares del artista
            top_tracks = sp.artist_top_tracks(new_artist['id'])
            top_tracks_info = []
            
            for track in top_tracks['tracks']:
                track_details = {
                    'name': track['name'],
                    'popularity': track['popularity'],
                    'preview_url': track['preview_url']
                }
                top_tracks_info.append(track_details)
            
            # Obtener información adicional del artista
            artist_info = {
                'name': new_artist['name'],
                'followers': new_artist['followers']['total'],
                'genres': new_artist['genres'],
                'popularity': new_artist['popularity'],
                'country': new_artist.get('country', 'País desconocido')  # Usar get() para manejar la ausencia de 'country'
            }
            
            return render_template('artist.html', artist_info=artist_info, 
                                   albums=album_info, top_tracks=top_tracks_info, 
                                   artist_image=artist_image)
        else:
            return f"No se encontró ningún artista con el nombre '{artist_name}'"
    else:
        return "Error: Debes ingresar un nombre de artista"

# Ruta para buscar una canción y obtener información
# Ruta para buscar una canción y obtener información
@app.route('/buscar_cancion', methods=['GET'])
def buscar_cancion():
    # Obtener el parámetro 'cancion_name' del query string
    cancion_name = request.args.get('cancion_name')

    if cancion_name:
        # Realizar la búsqueda de la canción en Spotify
        results = sp.search(q='track:' + cancion_name, type='track')
        canciones = results['tracks']['items']

        if len(canciones) > 0:
            # Tomar la primera canción encontrada
            track_id = canciones[0]['id']

            # Obtener la popularidad de la canción (likes)
            popularity = canciones[0]['popularity']

            # Información adicional de la canción
            track_info = {
                'name': canciones[0]['name'],
                'artist': canciones[0]['artists'][0]['name'],
                'album': canciones[0]['album']['name'],
                'release_date': canciones[0]['album']['release_date'],
                'popularity': popularity
            }

            # Obtener recomendaciones de canciones similares
            recommendations = sp.recommendations(seed_tracks=[track_id], limit=10)

            # Extraer la información de las recomendaciones
            recommended_tracks = []
            for track in recommendations['tracks']:
                track_details = {
                    'name': track['name'],
                    'artist': track['artists'][0]['name'],
                    'album': track['album']['name'],
                    'release_date': track['album']['release_date'],
                    'popularity': track['popularity'],
                    'preview_url': track.get('preview_url')  # Asegurarse de manejar la ausencia de 'preview_url'
                }
                recommended_tracks.append(track_details)

            # Renderizar el template canciones.html con la información de la canción y las recomendaciones
            return render_template('canciones.html', track_info=track_info, recommended_tracks=recommended_tracks)
        else:
            return f"No se encontró ninguna canción con el nombre '{cancion_name}'"
    else:
        return "Error: Debes ingresar el nombre de una canción"


# Ruta para mostrar recomendaciones de canciones
@app.route('/recomendaciones')
def mostrar_recomendaciones():
    # Definir recommended_tracks como una lista vacía por defecto si no se ha definido previamente
    recommended_tracks = []
    return render_template('recomendaciones.html', recommended_tracks=recommended_tracks)



# Iniciar la aplicación Flask
if __name__ == '__main__':
    app.run(debug=True)
