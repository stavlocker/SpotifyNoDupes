import sys
import re
import spotifyauth as sa

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)
VERSION = "1.0.0"

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


def set_playlist_by_name(tool, playlist, ignore_case=False):
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

def set_playlist(tool, playlist, ignore_case = False):
    return set_playlist_by_name(tool, playlist, ignore_case) or set_playlist_by_id(tool, playlist)

def get_playlists_by_input(user_playlists):
    print("Your playlists:")
    for i, item in enumerate(user_playlists):
        print("{}: {}".format(i + 1, item['name']))

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

                playlists.append({'id': user_playlists[pick - 1]['id'], 'name': user_playlists[pick - 1]['name']})
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
                    print("{blue}{}. {yellow}{} {purple}(#{}) by {}{end}".format(
                        i + 1, x['track']['name'], x['position'], x['track']['artists'][0]['name'],
                        blue = Color.BLUE, yellow = Color.YELLOW, purple = Color.PURPLE, end=Color.END
                    ))
            choice = input(
                Color.YELLOW + "All songs above are to be removed. Enter the #s separated by comma of the possible duplicates you wish to keep in the playlist, or 'CONTINUE' to remove all songs above: " + Color.END)
            if choice.lower() == 'continue':
                break
            to_remove = [] # So multi removing won't have it's numbers change in the middle of looping
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
                    to_remove.append(pick)

            removed_positions = []
            for pick in to_remove:
                for pos in removed_positions:
                    if pos < pick - 1:
                        pick -= 1
                print(Color.CYAN + "Removing {} from the list.".format(possible_duplicates[pick - 1]['track']['name']))
                possible_duplicates.remove(possible_duplicates[pick - 1])
                removed_positions.append(pick - 1)
        except ContinueIteration:
            prev_list_size = len(possible_duplicates)
            continue

def calculate_positions(tracks):
    return [{**x, 'position': i} for i, x in enumerate(tracks)]  # Update position for each track

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
    print(Color.BLUE+"-=== SpotifyNoDupes by "+Color.CYAN+"stavlocker"+Color.BLUE+" v{} ===-".format(VERSION)+Color.END)
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

    all_playlists = tool.get_user_playlists()

    if len(sys.argv) > 2:
        playlists_data = []
        for arg in sys.argv[2:]:
            found = None
            for playlist in all_playlists:
                if arg == playlist['name'] or arg == playlist['id']:
                    found = {'id': playlist['id'], 'name': playlist['name']}
            if not found:
                print(Color.RED + "ERROR: Playlist '{}' was not found.".format(arg) + Color.END)
            else:
                playlists_data.append(found)
    else:
        playlists_data = get_playlists_by_input(all_playlists)

    if playlists_data is None:
        return

    suspicion_idx = 1
    for playlist in playlists_data:
        possible_duplicates = []
        if not set_playlist(tool, playlist['id'], True):
            print(Color.RED + "ERROR: Playlist '{}' was not found.".format(playlist['name']) + Color.END)
            continue

        print(Color.BLUE + "Possible duplicates in {}: (Skipping songs that appear identical)".format(playlist['name']) + Color.END)
        tracks = tool.get_playlist_tracks()
        playlist_size = len(tracks)
        tracks = calculate_positions(tracks)
        # TODO Sort list by artist and only compare each song from the ones by the same artist for more efficiency
        for track in tracks:
            position = track['position']
            data = track['track']
            name = data['name']
            artist_id = data['artists'][0]['id']
            artist_name = data['artists'][0]['name']

            ok = True
            for dup in possible_duplicates:
                if dup == track:
                    ok = False

            if not ok:
                continue

            for other in tracks:
                if other == track or other['track']['artists'][0]['id'] != artist_id:
                    continue
                suspicion = are_songs_duplicates(track, other)
                if suspicion is not None:
                    possible_duplicates.append(other)
                    print("{blue}{}. {yellow}{: <28} {purple}(#{}) vs {yellow}{: <28}{purple} (#{}) by {}: {}{end}".format(
                        suspicion_idx, name, position + 1, other['track']['name'], other['position'] + 1, artist_name, suspicion,
                        blue=Color.BLUE, yellow=Color.YELLOW, purple=Color.PURPLE, end=Color.END))
                    suspicion_idx += 1
        if not possible_duplicates:
            print(Color.GREEN + "No duplicates found in {}.".format(playlist['name']) + Color.END)
            print()
        else:
            choice = input("Do you want to begin removing duplicates? [Y/n]")
            if choice.lower() != 'n':
                validate_songs_to_remove(possible_duplicates)
                # The list was finalized. Get removing!
                removed_positions = []
                for x in possible_duplicates:
                    print(Color.BLUE + "Removing {}...".format(x['track']['name']) + Color.END)
                    position = x['position']

                    # Update the position to match the modified list
                    for i, pos in enumerate(removed_positions):
                        if pos - i < position:
                            position -= 1

                    tool.remove_specific_track(x['track']['id'], position)
                    removed_positions.append(position)
                    tracks = calculate_positions(tool.get_playlist_tracks()) # Recalculate positions after removal
                print(Color.GREEN + "Successfully removed {} songs from {}.".format(str(playlist_size - len(tool.get_playlist_tracks())), playlist['name']))
                print()


if __name__ == "__main__":
    main()
