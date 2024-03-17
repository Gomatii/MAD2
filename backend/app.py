from flask import Flask, request, jsonify
from flask_cors import CORS
from spotify import top_tracks , top_artists
import requests
import sqlite3

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
CORS(app, resources={r"/*": {"origins": "http://localhost:8081"}})

def create_table():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            uid INTEGER PRIMARY KEY AUTOINCREMENT,
            uname TEXT,
            email TEXT,
            contact TEXT,
            password TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Temporary storage for registered users
registered_users = []

@app.route('/',methods=["GET"])
def greet():
    return("Hello homepage")

# app.py
# ...

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    uname = data.get('username')
    email = data.get('email')
    contact = data.get('contact')
    password = data.get('password')

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Check if the email is already registered
    cursor.execute('SELECT * FROM users WHERE email=?', (email,))
    existing_user = cursor.fetchone()
    if existing_user:
        conn.close()
        return jsonify({'message': 'Email already registered'}), 400

    # Register the new user
    cursor.execute('INSERT INTO users (uname, email, contact, password) VALUES (?, ?, ?, ?)',
                   (uname, email, contact, password))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Registration successful'})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Check if the email and password match a registered user
    cursor.execute('SELECT * FROM users WHERE email=? AND password=?', (email, password))
    user = cursor.fetchone()

    conn.close()

    if user:
        return jsonify({'message': 'Login successful'})
    else:
        return jsonify({'message': 'Invalid email or password'}), 401

RAPIDAPI_KEY = "de17d3f5e9msh5253cfd24acdabap142e0cjsn431da95a3ff1"
RAPIDAPI_HOST = "spotify23.p.rapidapi.com"

@app.route('/search/artists', methods=['GET'])
def search_artists():
    try:
        search_query = request.args.get('q', '')
        if not search_query:
            return jsonify({"error": "Search query parameter 'q' is required"}), 400

        url = "https://spotify23.p.rapidapi.com/search/"
        querystring = {
            "q": search_query,
            "type": "artists",
            "offset": "0",
            "limit": "15",
            "numberOfTopResults": "5"
        }

        headers = {
            "X-RapidAPI-Key": RAPIDAPI_KEY,
            "X-RapidAPI-Host": RAPIDAPI_HOST
        }

        response = requests.get(url, headers=headers, params=querystring)
        api_response = response.json()

        artist_names = [item['data']['profile']['name'] for item in api_response['artists']['items']]
        return jsonify({"artists": artist_names})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/search/genres', methods=['GET'])
def search_genres():
    try:
        search_query = request.args.get('q', '')
        if not search_query:
            return jsonify({"error": "Search query parameter 'q' is required"}), 400

        url = "https://spotify23.p.rapidapi.com/search/"
        querystring = {
            "q": search_query,
            "type": "genres",
            "offset": "0",
            "limit": "15",
            "numberOfTopResults": "5"
        }

        headers = {
            "X-RapidAPI-Key": RAPIDAPI_KEY,
            "X-RapidAPI-Host": RAPIDAPI_HOST
        }

        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()  # Raise an exception for bad responses

        api_response = response.json()
        genre_names = [item["data"]["name"] for item in api_response["genres"]["items"]]
        return jsonify({"genres": genre_names})

    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500

    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@app.route('/search/tracks', methods=['GET'])
def search_tracks():
    try:
        search_query = request.args.get('q', '')
        if not search_query:
            return jsonify({"error": "Search query parameter 'q' is required"}), 400
        url = "https://spotify23.p.rapidapi.com/search/"
        querystring = {
            "q": search_query,
            "type": "tracks",
            "offset": "0",
            "limit": "10",
            "numberOfTopResults": "5"
        }

        headers = {
            "X-RapidAPI-Key": RAPIDAPI_KEY,
            "X-RapidAPI-Host": RAPIDAPI_HOST
        }

        response = requests.get(url, headers=headers, params=querystring)
        api_response = response.json()

        # Extracting information from the API response
        tracks = api_response.get("tracks", {}).get("items", [])

        # Creating a list of dictionaries containing song and artist information
        results = [{"Song": track.get("data", {}).get("name", "N/A"),
                    "Artist": track.get("data", {}).get("artists", {}).get("items", [{}])[0].get("profile", {}).get("name", "N/A")}
                   for track in tracks]
        #print(results)
        return jsonify({"results": results})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/artist/details', methods=['GET'])
def artist_details():
    try:
        artist_name = request.args.get('q', '')
        if not artist_name:
            return jsonify({"error": "Search query parameter 'q' is required"}), 400

        url = "https://spotify23.p.rapidapi.com/search/"
        querystring = {
            "q": artist_name,
            "type": "multi",
            "offset": "0",
            "limit": "10",
            "numberOfTopResults": "5"
        }

        headers = {
            "X-RapidAPI-Key": RAPIDAPI_KEY,
            "X-RapidAPI-Host": RAPIDAPI_HOST
        }

        response = requests.get(url, headers=headers, params=querystring)
        api_response = response.json()

        # Assuming api_response contains the provided JSON data

        # Extracting information from the API response
        albums = api_response.get("albums", {}).get("items", [])
        podcasts = api_response.get("podcasts", {}).get("items", [])
        tracks = api_response.get("tracks", {}).get("items", [])
        playlists = api_response.get("playlists", {}).get("items", [])

        results = {
            "albums": albums,
            "podcasts": podcasts,
            "tracks": tracks,
            "playlists": playlists
        }

        return jsonify({"results": results})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/genre/details', methods=['GET'])
def genre_details():
    try:
        genre_name = request.args.get('q', '')
        if not genre_name:
            return jsonify({"error": "Search query parameter 'q' is required"}), 400

        url = "https://spotify23.p.rapidapi.com/search/"
        querystring = {
            "q": genre_name,
            "type": "multi",
            "offset": "0",
            "limit": "10",
            "numberOfTopResults": "5"
        }

        headers = {
            "X-RapidAPI-Key": RAPIDAPI_KEY,
            "X-RapidAPI-Host": RAPIDAPI_HOST
        }

        response = requests.get(url, headers=headers, params=querystring)
        api_response = response.json()

        # Assuming api_response contains the provided JSON data

        # Extracting information from the API response
        albums = api_response.get("albums", {}).get("items", [])
        podcasts = api_response.get("podcasts", {}).get("items", [])
        tracks = api_response.get("tracks", {}).get("items", [])
        playlists = api_response.get("playlists", {}).get("items", [])

        results = {
            "albums": albums,
            "podcasts": podcasts,
            "tracks": tracks,
            "playlists": playlists
        }

        return jsonify({"results": results})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/tracklist' , methods=['GET'])
def get_tracklist():
        try:
            search_query = request.args.get('q', '')
            if not search_query:
                return jsonify({"error": "Search query parameter 'q' is required"}), 400
            url = "https://spotify23.p.rapidapi.com/search/"
            querystring = {
            "q": search_query,
            "type": "tracks",
            "offset": "0",
            "limit": "10",
            "numberOfTopResults": "5"
        }

            headers = {
            "X-RapidAPI-Key": RAPIDAPI_KEY,
            "X-RapidAPI-Host": RAPIDAPI_HOST
        }

            response = requests.get(url, headers=headers, params=querystring)
            api_response = response.json()

        # Extracting information from the API response
            tracks = api_response.get("tracks", {}).get("items", [])

        # Creating a list of dictionaries containing song and artist information
            results = [{"Song": track.get("data", {}).get("name", "N/A"),
                    "Artist": track.get("data", {}).get("artists", {}).get("items", [{}])[0].get("profile", {}).get("name", "N/A")}
                   for track in tracks]
        #print(results)
            return jsonify({"results": results})

        except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route('/top-tracks' , methods=['GET','POST'])
def get_top_tracks():
    #print(top_tracks)
    tracks = top_tracks.get("content", {})
    return jsonify({"tracks": list(top_tracks["content"].values())})

@app.route('/top-artists' , methods =['GET','POST'])
def get_top_artists():
    return jsonify(top_artists)

if __name__ == "__main__":
    create_table()
    app.run(debug=True)
