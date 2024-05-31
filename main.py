from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json
import csv
import string

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

def get_token():
    auth_string = f"{client_id}:{client_secret}"
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": f"Basic {auth_base64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    
    response = post(url, headers=headers, data=data)
    response_data = response.json()
    return response_data.get("access_token")

def get_auth_header(token):
    return {"Authorization": f"Bearer {token}"}

def search_artists(token, query, offset, limit):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    params = {
        "q": query,
        "type": "artist",
        "offset": offset,
        "limit": limit
    }
    
    response = get(url, headers=headers, params=params)
    
    return response.json().get("artists", {}).get("items", [])

def save_artists_to_csv(artists, filepath):
    with open(filepath, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        for artist in artists:
            name = artist.get("name", "Unknown")
            artist_id = artist.get("id", "Unknown")
            spotify_link = artist.get("external_urls", {}).get("spotify", "Unknown")
            artist_type = artist.get("type", "Unknown")
            followers = artist.get("followers", {}).get("total", "Unknown")
            popularity = artist.get("popularity", "Unknown")
            genres = ", ".join(artist.get("genres", []))
            image_url = next((img["url"] for img in artist.get("images", []) if img["height"] == 640), "Unknown")
            writer.writerow([name, artist_id, spotify_link, artist_type, followers, popularity, genres, image_url])

def retrieve_all_artists(initial_letter):
    token = get_token()
    if not token:
        print("Failed to get token, exiting.")
        return
    
    limit = 50
    filename = f"artists_{initial_letter}.csv"
    folder_path = "datasets/Raw"
    os.makedirs(folder_path, exist_ok=True)  # Ensure the datasets folder exists
    filepath = os.path.join(folder_path, filename)

    if not os.path.exists(filepath):
        with open(filepath, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Artist Name", "ID", "Spotify Link", "Type", "Total Followers", "Popularity", "Genres", "Image URL (640x640)"])

    # Generate all possible prefixes based on the initial letter or digit
    if initial_letter.isalpha():
        prefixes = [initial_letter + c for c in string.ascii_lowercase]
    else:
        prefixes = [initial_letter]

    for prefix in prefixes:
        offset = 0
        while True:
            artists = search_artists(token, prefix, offset, limit)
            if not artists:
                break
            save_artists_to_csv(artists, filepath)
            offset += limit
            if offset >= 1000:
                break

if __name__ == "__main__":
    initial_letter = "a"  # Change this to "b", "c", etc. for subsequent runs or "0" for digits
    retrieve_all_artists(initial_letter)