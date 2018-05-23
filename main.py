import sys
import re
import spotifyauth as sa

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)


class Color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'


class ContinueIteration(Exception):
    pass


def set_playlist_by_name(tool, playlist, ignore_case = False):
    try:
        tool.set_playlist_by_name(playlist, ignore_case)
    except sa.NotFound:
        return False
    return True

def set_playlist_by_id(tool, playlist):
    try:
        tool.set_playlist_by_id(str(playlist))
    except sa.NotFound:
        return False
    return True

def set_playlist(tool, playlist):
    return set_playlist_by_name(tool, playlist) or set_playlist_by_id(tool, playlist)

def get_playlists_by_input(spotifytool):
    user_playlists = [x['name'] for x in spotifytool.get_all_playlists()]
    print("User playlists:")
    for i, item in enumerate(user_playlists):
        print("{}: {}".format(i + 1, item))

    while True:
        picks = input("Enter the # of the playlist(s), separated by comma, or 'cancel' to cancel: ")

        if picks.lower() == "cancel":
            print("Goodbye!")
            return None

        playlists = []

        for pick in picks.split(","):
            pick = pick.strip()

            if not re.match("^[0-9]+$", pick):
                print('Invalid number "{}"!'.format(pick))
                continue
            else:
                pick = int(pick)

                if pick < 1 or pick > len(user_playlists):
                    print("The number must be between {}-{}.".format(1, len(user_playlists)))
                    continue

                playlists.append(user_playlists[pick - 1])
        break

    return playlists

def validate_songs_to_remove(possible_duplicates):
    ok = False
    prev_list_size = 0
    while not ok:
        try:
            print()
            if prev_list_size != len(possible_duplicates):
                for i, x in enumerate(possible_duplicates):
                    print(Color.BLUE + str(i + 1) + ". " + Color.YELLOW + x['track']['name'] + Color.PURPLE + " by " +
                          x['track']['artists'][0]['name'] + Color.END)
            choice = input(
                Color.YELLOW + "All songs above are to be removed. Enter the #s of the possible duplicates you wish to keep in the playlist, or 'CONTINUE' to remove all songs above: " + Color.END)
            if choice.lower() == 'continue':
                break
            for pick in choice.split(","):
                pick = pick.strip()

                if not re.match("^[0-9]+$", pick):
                    print(Color.RED + 'ERROR: Invalid number "{}"!'.format(pick) + Color.END)
                    raise ContinueIteration()
                else:
                    pick = int(pick)

                    if pick < 1 or pick > len(possible_duplicates):
                        print(Color.RED + "ERROR: The number {} is not between {}-{}.".format(pick, 1, len(
                            possible_duplicates)) + Color.END)
                        raise ContinueIteration()
                    print(Color.CYAN + "Removing #{} ({}) from the list.".format(pick,
                                                                                 possible_duplicates[pick - 1]['track'][
                                                                                     'name']))
                    possible_duplicates.remove(possible_duplicates[pick - 1])
        except ContinueIteration:
            prev_list_size = len(possible_duplicates)
            continue

# Returns the suspicion message or None if there is no suspicion the songs are the same.
def are_songs_duplicates(s1, s2):
    if s1['track']['id'] == s2['track']['id'] and s1['track']['id'] is not None:
        return Color.RED + "IDENTICAL SONGS!"
    elif s1['track']['name'] == s2['track']['name']:
        return Color.RED + "Identical " + Color.CYAN + "names"
    elif s1['track']['duration_ms'] == s2['track']['duration_ms']:
        return Color.RED + "Identical " + Color.BLUE + "duration"
    return None

def main():
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        username = input("Please type in your username: ")

    try:
        auth = sa.SpotifyAuth(username)
        auth.wait_for_auth()
    except sa.FailedAuth as e:
        print(Color.RED + "Authentication failed: {}".format(e) + Color.END)
        sys.exit()
    auth.stop_server()

    print(Color.GREEN + "Successfully authenticated user {}.".format(username) + Color.END)

    tool = sa.SpotifyTool(username, auth.get_spotify())

    if len(sys.argv) > 2:
        playlists = sys.argv[2:]
    else:
        playlists = get_playlists_by_input(tool)

    if playlists is None:
        return

    suspicion_idx = 1
    for playlist in playlists:
        possible_duplicates = []
        print(Color.BLUE + "Possible duplicates in {}: (Skipping songs that appear identical)".format(playlist) + Color.END)
        if not set_playlist(tool, playlist):
            print(Color.RED + "WARNING: Playlist {} was not found".format(playlist) + Color.END)
            continue
        tool.set_playlist_by_name(playlist)
        tracks = tool.get_playlist_tracks()
        playlist_size = len(tracks)
        # TODO Sort list by artist and only compare each song from the ones by the same artist for more efficiency
        for track in tracks:
            data = track['track']
            name = data['name']
            artist_id = data['artists'][0]['id']
            artist_name = data['artists'][0]['name']

            ok = True
            for dup in possible_duplicates:
                if are_songs_duplicates(track, dup):
                    ok = False

            if not ok:
                continue

            for other in tracks:
                if other == track or other['track']['artists'][0]['id'] != artist_id:
                    continue
                suspicion = are_songs_duplicates(track, other)
                if suspicion is not None:
                    possible_duplicates.append(track)
                    print(Color.BLUE + "|-- {}. ".format(suspicion_idx) + Color.YELLOW + name + Color.PURPLE + " VS " + Color.YELLOW + other['track']['name'] + Color.PURPLE + " by {}: {}".format(artist_name, suspicion) + Color.END)
                    suspicion_idx += 1
        if not possible_duplicates:
            print(Color.GREEN + "No duplicates found in {}.".format(playlist) + Color.END)
            print()
        else:
            choice = input("Do you want to begin removing duplicates? [Y/n]")
            if choice.lower() != 'n':
                validate_songs_to_remove(possible_duplicates)
                # The list was finalized. Get removing!
                for x in possible_duplicates:
                    print(Color.BLUE + "Removing {}...".format(x['track']['name']) + Color.END)
                    print(str(x['track'])+Color.GREEN+" and "+Color.END+str(x['track']['id']))
                    tool.remove_all_tracks_but_one_by_id(x['track']['id'])
                print(Color.GREEN + "Successfully removed {} songs from {}.".format(str(playlist_size - len(tool.get_playlist_tracks())), playlist))
                print()


if __name__ == "__main__":
    main()
