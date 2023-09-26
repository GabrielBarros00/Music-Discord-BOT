# Music Bot Discord

A Discord bot with the sole function of playing videos/music and/or certain types of streams, such as YouTube, SoundCloud, Spotify, Twitch, and HTTP Stream.

## Installation

Clone the project

```bash
  git clone https://github.com/GabrielBarros00/Music-Discord-BOT
```

```bash
  cd Music-Discord-BOT
```


Tested on Python version 3.11.5 (Recommended 3.10 or higher).
```bash
python -m venv venv
```

Activate the virtual environment and install the necessary libraries for execution.

Linux:
```bash
source venv/bin/activate
```

Windows:
```bat
.\venv\Scripts\activate
```
Then, install the required libraries:

```bash
pip install -r requirements.txt
```

Download and run Lavalink before running the bot. Tested on LavaLink version 3.7.8.
Lavalink Github Link: https://github.com/lavalink-devs/Lavalink/releases

## Fixing error in WaveLink version 2.6.4

Inside the venv folder, you need to open the following file:

On Linux
```bash
venv/lib/python3.11/site-packages/wavelink/tracks.py
```

On Windows:
```bat
venv\Lib\site-packages\tracks.py
```

Change line 205 to:
```python
if str(check.host) == 'youtube.com' or str(check.host) == 'www.youtube.com' and check.query.get("list") and not check.query.get("v") or \
```

Change line 210 to:
```python
elif str(check.host) == 'soundcloud.com' and 'sets' in check.parts and check.query.get("in") == None or str(check.host) == 'www.soundcloud.com' and 'sets' in check.parts and check.query.get("in") == None:
```

## Environment Variables

To run this project, you will need to add the following environment variables to your .env file:

`SPOTIFY_CLIENT_ID`

`SPOTIFY_CLIENT_SECRET`

`BOT_TOKEN`

`LAVALINK_URL`

`LAVALINK_PASSWORD`


## Running Locally

With the venv activated, you can now start the bot using the following command in the project's root folder:

```bash
python __main__.py
```
