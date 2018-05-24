# SpotifyNoDupes
Detect and remove possible duplicates in your playlists.
This program can detect possible duplicates in your playlists and remove them for you. The program suspects that two songs are the same ones if:
 1. They have the same ID (meaning they are the exact same song), making it a 100% sure case
 2. They have the same name and they are from the same artist (which isn't for 100% but is very likely)
 3. They are from the same artist and they have the exact same duration (which again can't be 100% sure but it is very likely)
The program finds those duplicates in your playlist and presents them to you. If you'd like, you can remove those suspected duplicates and you can even choose which songs out of the possible duplicates to remove.

_Why?_ Because...
 1. Some songs on spotify are released multiple times under different albums / names / languages which causes Spotify to not notice they are in fact the same song.
 2. A collaborative playlist is very hard to keep clean from duplicates, and this plugin helps prevent them - even the ones Spotify doesn't notice.
 3. Keep your playlists clean with zero duplicates - even the ones that Spotify doesn't notice.

## Screenshots
![image](https://user-images.githubusercontent.com/30472563/39255472-4c0c4f20-48b5-11e8-9d36-3adc0bed5f0a.png)
<sup>*\* The web server after authenticating. This only needs to be done once (per user).*</sup>

![image](https://user-images.githubusercontent.com/30472563/39919348-fe84c430-551b-11e8-85b5-0398e4b461e5.png)
![image](https://user-images.githubusercontent.com/30472563/40512222-d1c96b00-5faa-11e8-9aba-78cc123d7104.png)
<sup>*\* The program output for the following playlist "My Playlist".</sup>

## Required packages
This program uses Python 3. To use SpotifyNoDupes, you need [spotipy](https://github.com/plamere/spotipy). You can install it using `pip`: `pip install spotipy`
If you know how to use `virtualenv`s it is recommended you use one:
```
mkvirtualenv spotifynodupes
pip install spotipy
```
## Setup

1. Create a spotify application so you can use `spotipy`. You can do this at the [Spotify developer website](https://developer.spotify.com/my-applications/).
2. Put your client ID & client secret into `spotifyauth.py`. The default redirect URL is `http://localhost:14523` for the local webserver.
3. You're done - you can basically change anything else you'd like.

## Run

The script can be ran by executing the file `main`, and using the CLI interface to use the program. In this case, the program will ask you for your username and the playlist(s) you want to de-dupe.

The usage for the program is `main.py [username] [Playlist1 Playlist2 Playlist3...]` where the two arguments are optional. _Note that you can't enter playlists without a username - the first argument has to be the username._
 - `Username`: Your username
 - `Playlist1, Playlist2, Playlist3...` - As many playlists as you like, as the playlist's ID or name. Notice that these playlists must be owned by you
 
For every user that uses the program for the first time, authorization through the Spotify website is required. A window will open, asking you to copy the redirected URL back to the program. After you've done this for the first time for that specific user, the program will save your credentials. _Note: The program doesn't have access to your Spotify account password and doesn't use it anywhere. It is simply storing the authorization you gave to Spotify in order to communicate with the Spotify web API._


## FAQ
**Q:** Which permissions do I need to give the program access on Spotify to, and why?

**A:** The program uses four permissions to work:
* [`playlist-read-private`](https://beta.developer.spotify.com/documentation/general/guides/scopes/#playlist-read-private) - Read access to user's private playlists, to check for duplicates.
* [`playlist-read-collaborative`](https://beta.developer.spotify.com/documentation/general/guides/scopes/#playlist-read-collaborative) - A permission to allow the program to also view collaborative playlists, which it can't access by default.
* [`playlist-modify-public`](https://beta.developer.spotify.com/documentation/general/guides/scopes/#playlist-modify-public) - Write access to a user's public playlists, to remove duplicates in the user's public playlists.
* [`playlist-modify-private`](https://beta.developer.spotify.com/documentation/general/guides/scopes/#playlist-modify-private) - Write access to a user's private playlists, to remove duplicates in the user's private playlists.

## Contributing
There's a reason this repository is open source. You are very welcome to contribute - if you want to squash a bug, make an improvement, or anything - feel free to fork the repository and create a pull request. Just make sure that your code is clean, and matches the rest of the code in the repository syntax-wise.

You are also very welcome to submit issues about bugs, improvements, ideas, questions and anything you'd like about this repository.

## See also
If you liked SpotifyNoDupes, you'll love [`SpotifyRandomizer`](https://github.com/DanielsWrath/SpotifyRandomizer), a python script to finally truly randomize your playlists (which I contributed a lot to :wink:). Thanks [@DanielsWrath](https://github.com/DanielsWrath) for inspiration from the [`SpotifyRandomizer`](https://github.com/DanielsWrath/SpotifyRandomizer) repository.
