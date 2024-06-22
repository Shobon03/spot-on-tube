"""
spot-on-tube is a Python script that allows you to create YouTube 
playlists based on your Spotify playlists


Copyright (C) 2021 Shobon03

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

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



def terminateExecution(): 

  """
    Useful for the .exe file, as it automatically closes when the program finishes... 
    This ensures the user can read the last messages
  """
  input("\nPress ENTER to terminate...")



def getSpotifyPlaylistTracks():

  def replaceCharacters(playlistName):

    invalidCharacters = ["<", ">", ":", '"', "/", "\\", "|", "?", "*"]
    for characterIndex in range(len(invalidCharacters)): # Replaces invalid filename characters...
      playlistName = playlistName.replace(invalidCharacters[characterIndex], "-")

    while playlistName[0] not in string.ascii_letters: # ...and removes whitespaces in the first index
      if playlistName[0] == " ":
        playlistName = playlistName[1:]
      
      else:
        break

    return playlistName

  

  try: # Checks if the user has made a login before
    open(".cache", "r")
  
  except FileNotFoundError:
    print("\nThis script will generate a YouTube playlist based on your Spotify playlist. \nFor that, you'll be prompted to login into your Spotify account and to accept that your app can access your data.")

  print("\nCollecting data...")
  spotifyAuth = spotipy.Spotify(
    auth_manager = SpotifyOAuth(
      scope = "playlist-read-private",
      client_id = spotifyClientID,
      client_secret = spotifyClientSecret,
      redirect_uri = "http://localhost:3000/callback/"
    )
  )

  allPlaylistsFromUser = spotifyAuth.current_user_playlists()["items"]  
  playlistID = 0 # Give the playlist an ID to be choosed later
  print("Done!")


  print("\nYour saved playlists are: \n(Notation: PLAYLIST_ID. PLAYLIST_NAME)")
  for playlist in allPlaylistsFromUser:
    playlistName = replaceCharacters(playlist["name"])
    
    print(f"\n\t{playlistID}. {playlistName}")
    
    playlistID += 1
    time.sleep(0.20)


  while True:
    try: # Ensures the input it's a number...
      selectedPlaylistID = int(input("\nSelect a playlist: "))
    
    except ValueError:
      print("Please input a number...")
      continue

    try: # ...and ensures that it's within the bounds
      allPlaylistsFromUser[selectedPlaylistID]
      
    except IndexError:
      print(f"Please input a number between 0 and {playlistID - 1}...")
      continue

    else:
      break

  selectedSpotifyPlaylistID = allPlaylistsFromUser[selectedPlaylistID]["id"]
  selectedSpotifyPlaylistName = replaceCharacters(allPlaylistsFromUser[selectedPlaylistID]["name"])
  print(f"\nPlaylist: {selectedSpotifyPlaylistName}")

  print("\nCollecting tracks...")
  """ 
  Append all tracks from playlist on an array of dicts
  Notation:
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
  playlist = {
    "name": selectedSpotifyPlaylistName, 
    "tracks": []
  }
  offsetNumber = 0
  lastTrackID = 0
  while True:
    tracksFromPlaylist = spotifyAuth.playlist_tracks(
      selectedSpotifyPlaylistID, 
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
      print("All tracks collected successfully!")

      choice = input("\nWould you like to generate a file containing all tracks? (y/n) ")
      if choice == "y" or choice == "Y" or choice == "":
        try:
          os.mkdir("./tracks-from-playlists", 777)

        except FileExistsError:
          pass

        allTracksFile = open(
          f"./tracks-from-playlists/Tracks from = {selectedSpotifyPlaylistName}.json", 
          "w", 
          encoding = "utf-8"
        )
        allTracksFile.write(
          json.dumps(
            playlist, 
            ensure_ascii = False, 
            indent = 2
          )
        )
        allTracksFile.close()

        print("File generated successfully! Check the folder 'tracks-from-playlsit/' to see it!")

      break

  return playlist



def searchTracks():
  
  playlist = getSpotifyPlaylistTracks()

  try: # Checks if tracks were previously searched
    open(f"./videos-searched/Videos collected from = {playlist['name']}.json", "r")

  except FileNotFoundError:
    print("\nCollecting videos from YouTube... (please note that this can take a while)")
    pass

  else:
    searchedVideos = json.load(
      open(
        f"./videos-searched/Videos collected from = {playlist['name']}.json", 
        "r"
      )
    )

    print("\nThere are videos searched before from this playlist, ", end = "") 
    if searchedVideos[0]["trackID"] == 0:
      print("so this script will create a YouTube playlist...")

    else:
      print("so this script will now append the remaining videos into the YouTube playlist...")

    return playlist["name"]
    

  """ 
  Query videos and apppend their ID on an array of dicts
  Notation:
    videos = [
      {
        "trackID": <track id>
        "name": <track + artist>,
        "youtubeID": <id>
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

    try: # If YoutubeSearch() gets a "KeyError: 'sectionListRenderer'", try to search the same video again
      queryResult = YoutubeSearch(
        f"{trackArtist} - Topic - {trackName}", 
        max_results = 1
      ).to_dict()
    
      video = {
        "trackID": trackID, 
        "name": f"{trackName} - {trackArtist}", 
        "youtubeID": queryResult[0]["id"]
      }
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

  collectedVideosFile = open(
    f"./videos-searched/Videos collected from = {playlist['name']}.json", 
    "w"
  )
  collectedVideosFile.write(
    json.dumps(
      videos, 
      ensure_ascii = False, 
      indent = 2
    )
  )
  collectedVideosFile.close()
  print("File generated successfully!")


  return playlist["name"]


def insertIntoYoutubePlaylist():

  spotifyPlaylistName = searchTracks() 
  quotaUnitsLeft = 10000

  os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "0"

  print("\nGoogle will now ask your permission, which will allow the app to access your YouTube account information...")
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
    
    if currentYoutubePlaylistName == spotifyPlaylistName:
      print("\nPlaylist found!")
      
      youtubePlaylistID = youtubePlaylists[playlist]["id"]
      youtubePlaylistExists = True
      
      break


  if youtubePlaylistExists is False:
    print("\nPLaylist not found! Creating one...")
    requestPlaylistCreation = youtube.playlists().insert(
      part = "snippet",
      body = {
        "snippet": {
          "title": spotifyPlaylistName,
          "description": "Playlist created via SpotOnTube script! 😎",
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


  print("\nAppending videos into the YouTube playlist...")
  videos = json.load(
    open(
      f"./videos-searched/Videos collected from = {spotifyPlaylistName}.json", 
      "r"
    )
  )
 
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
        print("\nAll quota used!")
        break

      quotaUnitsLeft -= 50

      del videos[0]
      
  print("Done!")


  if videos != []:
    videosNotInsertedFile = open(
      f"./videos-searched/Videos collected from = {spotifyPlaylistName}.json", 
      "w"
    )
    videosNotInsertedFile.write(
      json.dumps(
        videos, 
        ensure_ascii = False, 
        indent = 2
      )
    )
    videosNotInsertedFile.close()

    print(f"\nNot all tracks could be added to the playlist because of the API quota limit. \nExecute this script with another Google app, or execute it tomorrow, for it will be added the rest of the videos. Select the same playlist you've selected before. \nA list of remaining videos was created. Check the file 'Videos collected from = {spotifyPlaylistName}.json' in the folder 'videos-searched/' to see them and *DO NOT DELETE* the folder nor the file, otherwise it will start from the beggining again and you'll duplicate the YouTube playlist items.")
    terminateExecution()

  else:
    print("\nAll videos inserted! \nRemoving the JSON file with all the videos...")
    os.remove(f"./videos-searched/Videos collected from = {spotifyPlaylistName}.json")
    print("Done!")
    terminateExecution()
  


""" ===== MAIN PROGRAM ===== """
try:
  spotifyCredentials = json.load(
    open(
      "./credentials/spotifyCredentials.json", 
      "r"
    )
  )
  spotifyClientID = spotifyCredentials["data"]["client_id"]
  spotifyClientSecret = spotifyCredentials["data"]["client_secret"]


  youtubeCredentials = json.load(
    open(
      "./credentials/youtubeCredentials.json", 
      "r"
    )
  )
  youtubeClientID = youtubeCredentials["installed"]["client_id"]
  youtubeClientSecret = youtubeCredentials["installed"]["client_secret"]

except FileNotFoundError:
  print("\nERROR: The Spotify/Google credentials file(s) was(were) not found.")
  print("Please refer to the README.md file, under 'Getting your credentials from Spotify/Google', to see how the file must be created.")
  terminateExecution()

else:
  try:
    print("----- Welcome to SpotOnTube -----")
    if spotifyClientID != "" and spotifyClientSecret != "" and youtubeClientID != "" and youtubeClientSecret != "":
      insertIntoYoutubePlaylist()
    
    else:
      print("ERROR: Some client id and client secret strings are empty.")
      print("Please refer to the README.md file, to see how to get your credentials in place.")
      terminateExecution()

  except KeyboardInterrupt:
    print("\n\n\tBye bye!")
    terminateExecution()