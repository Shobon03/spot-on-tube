<h1 align="center" style="display: flex; align-items: center; justify-content: center; gap: 10px;"> <img width=30 src="./images/logos/logo.png" /> spot-on-tube!</h1>

<h4 align="center" style="font-weight: bold;">A simple CLI that creates a YouTube playlist based on a Spotify playlist</h4>

<h6 align="center" style="font-weight: bold; font-style: italic;">PUBLIC ARCHIVE AS OF 22-06-2024</h6>

<h2 align="center">Table of contents</h2>

- [About](#about)
  - [Read this before doing anything](#read-this-before-doing-anything)
- [Dependencies](#dependencies)
  - [List](#list)
  - [Installing](#installing)
- [Limitations](#limitations)
  - [YouTube API](#youtube-api)
  - [youtube_search library](#youtube-search-library)
- [Executing](#executing)
- [Privacy](#privacy)
- [Logos](#logos)
- [License](#license)

## About

spot-on-tube is a Python script that creates YouTube playlists based on your saved Spotify playlists.

The script can also generate a `.json` file containing all songs from the selected Spotify playlist, if the user wants to see them.

### Read this before doing anything

I'm still testing this app to track some errors and bugs and I'm changing some things on the code constantly, such as messages and stuff. If you want to test it and give some feedback, I would much appreciate it!

## Dependencies

spot-on-tube was made using Python 3.9.

My plan was to use the raw _Spotify Web API_ and _YouTube Data API_ but I couldn't set them properly. After some research, I came across two Python libraries. They are: [spotipy](https://github.com/plamere/spotipy) and [youtube-search](https://github.com/joetats/youtube_search).

They helped me so much, as they simplified some things and then I was able to give this project some light.

I want to thank all the people involved in those projects, for they brought these libraries to their existence. **You guys are awesome** 😎

For YouTube authorization:

- google-api-python-client
- google-auth-oauthlib

And, for the .exe file, it was used the [pyinstaller](https://github.com/pyinstaller/pyinstaller) library.

### List

- spotipy
- youtube-search
- google-api-python-client
- google-auth-oauthlib
- pyinstaller

### Installing

You'll need `pip` to install them. Make sure that you have it installed on your system.

On your terminal, install:

```
pip install spotipy youtube-search google-api-python-client google-auth-oauthlib
```

## Limitations

### YouTube API

In the _YouTube API Daily Quota_ (you can see the cost for each request [here](https://developers.google.com/youtube/v3/determine_quota_cost?hl=en)), we have only **10,000 units**, in which we can do operations with. The cost of each YouTube search is **100 units**, but because the youtube_search library is being used, this isn't a problem.

The script does these operations:

- List a user's playlists: **50 units** (only called once)
- Create a playlist: **1 unit** (only called once and if the playlist doesn't exist)
- Insert videos into the playlist: **50 units** (called per video that will be inserted). So, the maximum limit of videos it can insert per app is **199** (**198** if the playlist needs to be created). This will be, unfortunately, the limit of songs that the script will be able to do with per app or daily (as the quota resets every day at Pacific Time).

The script will automatically detect if there are videos that didn't get to be inserted, and will insert them if the user selects the same playlist, upon executing the program again (this, of course, if the user created another app, or executed the script on another day).

### [youtube-search](https://github.com/joetats/youtube_search) library

This library is a crawler, therefore not all results will be the same. This depends of where you live and which video is being search. Maybe some of the videos will not be the one you want, but the script does its best to find the match. And maybe a video will not be found, so it won't be added in the final playlist.

## Executing

How to execute steps on: [EXECUTING.md](./docs/EXECUTING.md).

## Privacy

spot-on-tube **_doesn't_** collect your personal data.

It only creates a YouTube playlist based on your selected Spotify playlist.

## Logos

The spot-on-tube logo was made in [LibreSprite](https://github.com/LibreSprite/LibreSprite).

## License

![](./images/license-logo.png)\
spot-on-tube is released under the [GPL-3.0](./LICENSE) license.

```
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
```
