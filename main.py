from dotenv import load_dotenv # for loading .env files
import os
import base64
from requests import post,get
import json

load_dotenv()

# Retrieves the values of CLIENT_ID and CLIENT_SECRET
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

def get_token():
    auth_string = client_id + ':' + client_secret
    auth_bytes = auth_string.encode("utf-8") # concatenated string in bytes
    auth_base64 = str(base64.b64encode(auth_bytes), 'utf-8') # base64-encoded version of the concatenated string

    url = "https://accounts.spotify.com/api/token" # URL to which request is sent

    headers = {
        "Authorization" : "Basic " + auth_base64, # Basic authentication
        "Content-type" : "application/x-www-form-urlencoded" # tells the server that the body of the request is URL-encoded form data
    }
    data = {
    "grant_type": "client_credentials" # client (our application) requests an access token
    }
    result = post(url, headers=headers, data=data) # post request made and the response obj containing status code, headers, content etc.. are stored in result
    json_result = json.loads(result.content) # the content of the response obj which is a byte string representing a JSON object is converted to a dict
    #print(json_result)
    token = json_result["access_token"]
    #print('expires in : ', json_result["expires_in"]) # a generated token expires in 1 hour
    return token

def get_auth_header(token):
    return {"Authorization": "Bearer " + token} # Returns a dictionary with the Authorization header needed for every API requests.

def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search" # endpoint for searching an artist
    headers = get_auth_header(token)

    query = f"?q={artist_name}&type=artist&limit=1"
    query_url = url + query

    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["artists"]["items"]

    
    if len(json_result) == 0:
        print("No artist with this name exists...")
    else:
        return json_result[0]
    
def get_songs_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    return json_result["tracks"]


token = get_token() # a new token is generated each time you run this
print("\nToken :",token)
artist = search_for_artist(token, "weeknd")
artist_name = artist["name"]
artist_id = artist["id"]
print(f"Artist name : {artist_name}")
print(f"artist ID : {artist_id}")
songs = get_songs_by_artist(token, artist_id)

print("\n" + f"TOP 10 SONGS BY {artist_name.upper()}")
for idx, song in enumerate(songs):
    print(f"{idx + 1} {song["name"]}")