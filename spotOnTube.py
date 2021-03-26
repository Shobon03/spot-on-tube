import os
import json
import time
import string
import spotipy
import google_auth_oauthlib as googleAuth
import googleapiclient.discovery as googleDiscovery
import googleapiclient.errors
from spotipy.oauth2 import SpotifyOAuth
from youtube_search import YoutubeSearch


def terminateExecution(): # Useful for the .exe file, as it automatically closes when the program finishes. This ensures the user can read the messages
  print(input("\nPress ENTER to terminate..."))

def getSpPlaylistTracks():

  ### Replaces invalid filename characters and removes whitespaces that are in the first index
  def replaceCharacters(playlistName):
    invalidCharacters = ["<", ">", ":", '"', "/", "\\", "|", "?", "*"]
    for characterIndex in range(len(invalidCharacters)):
      playlistName = playlistName.replace(invalidCharacters[characterIndex], "-")

    while playlistName[0] not in string.ascii_letters:
      if playlistName[0] == "":
        playlistName = playlistName[1:]
      
      else:
        break

    return playlistName


  ### Checks if the user has made a login before
  try:
    open(".cache", "r")
  
  except FileNotFoundError:
    print("\nThis script will generate a YouTube playlist based on your Spotify playlist. \nFor that, you'll be prompted to login into your Spotify account and to accept that your app can access your data.")


  auth = spotipy.Spotify(
    auth_manager = SpotifyOAuth(
      scope = "playlist-read-private",
      client_id = spotifyClientID,
      client_secret = spotifyClientSecret,
      redirect_uri = "http://localhost:3000/callback/"
    ) 
  )

  
  print("\nCollecting data...")
  results = auth.current_user_playlists()["items"]
  playlistID = 0 # Give the playlist an ID to be chosen later
  print("Done!")


  print("\nYour saved playlists are:")
  print("(Notation: PLAYLIST_ID. PLAYLIST_NAME)")
  for playlist in results:
    currentPlaylistName = replaceCharacters(playlist["name"])
    
    print(f"\n{playlistID}. {currentPlaylistName}")
    
    playlistID += 1
    time.sleep(0.25)


  while True:
    #### Ensures the input it's a number...
    try:
      selectedPlaylistID = int(input("\nSelect a playlist ID: "))
    
    except ValueError:
      print("This playlist doesn't exist. Please input a number...")
      continue

    #### ...and ensures the number is within the bounds
    try:
      results[selectedPlaylistID]
      
    except IndexError:
      print("This playlist doesn't exist. Please input a lower number...")
      continue

    else:
      break

  selectedPlaylistSpotifyID = results[selectedPlaylistID]["id"] # Picks the Spotify playlist ID
  selectedPlaylistName = replaceCharacters(results[selectedPlaylistID]["name"])
  print(f"\nPlaylist chosen: {selectedPlaylistName}")


  print("\nCollecting tracks...")
  ### Select all tracks from a Spotify playlist, appending them on an array of dicts
  """ Notation:
        playlist = {
          name: <playlist name>, 
          tracks: [
            {
              id: <track id>,
              title: <track title>,
              artist: <track artist> 
            },
            ...
          ],
          totalTracks: <number of tracks>
        }
  """
  offsetNumber = 0
  lastTrackID = 0
  
  playlist = {
    "name": selectedPlaylistName, 
    "tracks": []
  }

  while True:
    tracksFromPlaylist = auth.playlist_tracks(
      selectedPlaylistSpotifyID, 
      limit = 100, 
      offset = offsetNumber
    )["items"]

    if len(tracksFromPlaylist) != 0:
      currentTrackID = lastTrackID

      for tracks in tracksFromPlaylist:
        if tracks["track"]["name"] != "":
          trackDetails = {
            "id": currentTrackID, 
            "title": tracks["track"]["name"], 
            "artist": tracks["track"]["artists"][0]["name"]
          }

          playlist["tracks"].append(trackDetails)
          currentTrackID += 1
        
      offsetNumber += 100
      lastTrackID = currentTrackID

    else:
      playlist["totalTracks"] = lastTrackID

      time.sleep(0.75)
      print("All tracks collected successfully!")


      #### Creates a JSON file with all playlist tracks
      choice = input("\nWould you like to generate a JSON file containing all tracks? (y/n) ")
      if choice == "y" or choice == "Y" or choice == "":
        try:
          os.mkdir("./tracks-from-playlists", 777)

        except FileExistsError:
          pass

        allTracksFile = open(f"./tracks-from-playlists/Tracks from = {selectedPlaylistName}.json", "w", encoding = "utf-8")
        allTracksFile.write(json.dumps(playlist, ensure_ascii = False, indent = 2))
        allTracksFile.close()

        time.sleep(0.75)
        print("File generated successfully!")

      break

  return playlist



def searchTracks():
  
  playlist = getSpPlaylistTracks()


  ### Checks if the tracks were previously searched
  try:
    open(f"./videos-searched/Videos collected from = {playlist['name']}.json", "r")

  except FileNotFoundError:
    print("\nCollecting videos from YouTube... \n(please note that this can take a while)")
    pass

  else:
    print("\nThis playlist was searched before. This script will now insert the remaining videos into the playlist.")
    return [json.load(open(f"./videos-searched/Videos collected from = {playlist['name']}.json", "r")), playlist['name']]


  ### Query videos and return their YouTube ID, appending them on an array of dicts
  """ Notation:
      videos = [
        {
          "name": <track + artist>,
          "youtubeID": <video id on youtube>
        },
        ...
      ]
  """
  videos = []
  previousTrack = playlist["tracks"][0]
  for track in playlist["tracks"]:
    trackName = track["title"]
    trackArtist = track["artist"]
    trackID = track["id"]

    
    try: # If YoutubeSearch() gets a "KeyError: 'sectionListRenderer'", try and search the video again
      result = YoutubeSearch(
        f"{trackName} {trackArtist}", 
        max_results = 1
      ).to_dict()
    
      video = {"trackID": trackID, "name": f"{trackName} - {trackArtist}", "youtubeID": result[0]["id"]}
      videos.append(video)

      previousTrack = track

    except KeyError:
      track = previousTrack
      continue

  print("\nAll videos collected successfully!")


  print("\nGenerating a JSON file with all videos...")
  try:
    os.mkdir("./videos-searched", 777)

  except FileExistsError:
    pass

  collectedVideosFile = open(f"./videos-searched/Videos collected from = {playlist['name']}.json", "w")
  collectedVideosFile.write(json.dumps(videos, ensure_ascii = False, indent = 2))
  collectedVideosFile.close()
  
  time.sleep(0.75)
  print("Done!")


  return [videos, playlist['name']]



def insertIntoYtPlaylist():

  contents = searchTracks()
  videos = contents[0]
  spotifyPlaylistName = contents[1] 
  quotaUnitsLeft = 10000


  os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "0"

  print("\nGoogle will now ask your permission, which will allow the app access your YouTube information.\n")
  authorization = googleAuth.flow.InstalledAppFlow.from_client_secrets_file(
    "./credentials/youtubeCredentials.json", # Credentials file
    "https://www.googleapis.com/auth/youtube" # Scope
  )
  credentials = authorization.run_console()
  youtube = googleDiscovery.build(
    "youtube", 
    "v3", 
    credentials = credentials
  )
  

  requestAllPlaylists = youtube.playlists().list(
    part = "snippet, contentDetails",
    maxResults = 50,
    mine = True
  )
  youtubePlaylists = requestAllPlaylists.execute()["items"]
  quotaUnitsLeft -= 1


  youtubePlaylistExists = False
  for playlist in range(len(youtubePlaylists)):
    currentYoutubePlaylistName = youtubePlaylists[playlist]["snippet"]["localized"]["title"]
    if currentYoutubePlaylistName == spotifyPlaylistName: # Checks the name of the playlist
      print("\nPlaylist found!")
      
      youtubePlaylistID = youtubePlaylists[playlist]["id"]
      youtubePlaylistExists = True
      
      break


  if youtubePlaylistExists is False:
    print("\nPLaylist not found! \n\nCreating one...")
    requestPlaylistCreation = youtube.playlists().insert(
      part = "snippet",
      body = {
        "snippet": {
          "title": spotifyPlaylistName,
          "description": "Playlist created via the SpotOnTube script! 😎",
          "tags": [
            "playlist",
            "API call"
          ],
          "defaultLanguage": "en",
          "status": {
            "privacyStatus": "private"
          }
        }
      }
    )
    youtubePlaylist = requestPlaylistCreation.execute()
    youtubePlaylistID = youtubePlaylist["id"]

    print("Playlist created successfully!")

    quotaUnitsLeft -= 50


  print("\nInserting videos into the YouTube playlist...")
  videos = json.load(open(f"Videos collected from = {spotifyPlaylistName}.json", "r"))
  for videoIndex in range(len(videos)):
    if quotaUnitsLeft != 0:
      try:
        requestPlaylistItemInsert = youtube.playlistItems().insert(
          part = "contentDetails, id, snippet",
          body = {
            "snippet": {
              "playlistId": youtubePlaylistID,
              "resourceId": {
                "kind": "youtube#video",
                "videoId": videos[0]["youtubeID"]
              }
            }
          }
        )
        requestPlaylistItemInsert.execute()      
      except googleapiclient.errors.HttpError:
        continue

      quotaUnitsLeft -= 50

      del videos[0]
      
  print("Done!")


  if videos != []:
    videosNotInsertedFile = open(f"Videos collected from = {spotifyPlaylistName}.json", "w")
    videosNotInsertedFile.write(json.dumps(videos, ensure_ascii = False, indent = 2))
    videosNotInsertedFile.close()

    print(f"\nNot all tracks could be added to the playlist because of the API quota limit. \nExecute this script with another app, or execute it tomorrow, for it will be added the rest of the videos. Select the same playlist you've selected before. \nA list of remaining videos was created. Check the file 'Videos collected from = {spotifyPlaylistName}.json' in the folder 'videos-searched' to see them and *DO NOT DELETE* the folder, nor the file, otherwise it will be added all the previously searched videos.")
    terminateExecution()

  else:
    print("\nAll videos inserted!")
    print("\nRemoving the JSON file with all the videos...")
    os.remove(f"./videos-searched/Videos collected from = {spotifyPlaylistName}.json")
    print("Done!")
    terminateExecution()



def main():
  print("----- Welcome to SpotOnTube -----")
  if spotifyClientID != "" and spotifyClientSecret != "" and youtubeClientID != "" and youtubeClientSecret != "":
    insertIntoYtPlaylist()
  else:
    print("ERROR: Some client id and client secret strings are empty.")
    print("If you want to know how to gather those those credentials, please read the README.md for details.")
    terminateExecution()


try:
  spotifyClientID = json.load(open("./credentials/spotifyCredentials.json", "r"))["data"]["client_id"]
  spotifyClientSecret = json.load(open("./credentials/spotifyCredentials.json", "r"))["data"]["client_secret"]

except FileNotFoundError:
  print("\nThe file 'spotifyCredentials.json' was not found. \nPlease refer to the README.md file, under 'Getting your credentials from Spotify', to see how the file must be created.")
  terminateExecution()

else:
  try:
    youtubeClientID = json.load(open("./credentials/youtubeCredentials.json", "r"))["installed"]["client_id"]
    youtubeClientSecret = json.load(open("./credentials/youtubeCredentials.json", "r"))["installed"]["client_secret"]

  except FileNotFoundError:
    print("\nThe file 'youtubeCredentials.json' was not found. \nPlease refer to the README.md file, under 'Getting your credentials from Google', to see how the file must be created.")
    terminateExecution()

  else:
    main()