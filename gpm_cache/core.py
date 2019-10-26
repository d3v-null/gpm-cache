"""
Cache information about a GPM playlist using gmusicapi.
"""

from __future__ import absolute_import

import logging
import os
import sys
import time
from argparse import ArgumentParser

import gmusicapi
import mutagen
import requests
from gmusicapi import Mobileclient
from mutagen.easyid3 import EasyID3
from six import b, binary_type, iterbytes, text_type, u, unichr  # noqa: W0611

from .sanitation_helper import to_safe_filename, to_safe_print
from .library import Library
from .track_info import TrackInfo
from .exceptions import BadLoginException, PlaylistNotFoundException

DEBUG_LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}


# pprint(EasyID3.valid_keys.keys())
def get_parser_args(argv=None):
    """Parse arguments from cli, env and config files."""
    argv = sys.argv[1:] if argv is None else argv

    parser = ArgumentParser(description="cache information about a playlist from Google Play Music",
                            fromfile_prefix_chars="@")
    parser.add_argument('--email', help="The Google Authentication email", required=True)
    parser.add_argument('--pwd', help="The Google Authentication password")
    parser.add_argument('--device-id',
                        help=("The Device ID used to log in "
                              "(Use a GSF ID that has already been registered with GPM)"),
                        required=True)
    parser.add_argument('--playlist',
                        help="The name of the GPM playlist to cache info from",
                        required=True)
    parser.add_argument('--playlist-cached',
                        help="The name of the GPM playlist to add cached songs to.",
                        default=None)
    parser.add_argument('--clear-playlist',
                        help=("Clear the source playlist once all files have been saved to the "
                              "cached playlist."),
                        default=True)
    parser.add_argument('--sleep-time',
                        help="Time to sleep in between requests",
                        default=10,
                        type=float)
    parser.add_argument('--cache-location',
                        help="The location in the filesystem to store cached information",
                        default=os.path.join(os.path.expanduser("~"), "gpm-cache"))
    parser.add_argument('--cache-heirarchy',
                        help="The structure in which the output files are organised",
                        choices=['artist_album', 'flat'],
                        default='artist_album')
    parser.add_argument('--debug-level',
                        help="The level above which debug statements are printed",
                        choices=list(DEBUG_LEVELS.keys()),
                        default='warning')
    parser.add_argument('--oauth-creds-file',
                        help=("location to store the oauth credentials file. "
                              "If not provided, a file will be created for you in "
                              "[Appdir](https://pypi.org/project/appdirs/) `user_data_dir` "
                              "by default"),
                        default=None)
    parser.add_argument('--oauth-browser',
                        help=("open the oauth flow in your browser"),
                        default=True)

    parser_args = parser.parse_args(argv)

    return parser_args


def save_meta(local_filepath, track_info=None):
    """Save meta associated with track to the given file."""
    try:
        meta = EasyID3(local_filepath)
    except mutagen.id3.ID3NoHeaderError:
        meta = mutagen.File(local_filepath, easy=True)
        meta.add_tags()

    for meta_key, meta_val in track_info.id3_meta.items():
        meta[meta_key] = meta_val

    meta.save()


def get_local_filepath(cache_location, cache_heirarchy, track_info=None):
    """
    Determine the best location to save the track on disk.

    Create dirs if necessary.
    """

    local_filepath = "%s.mp3" % to_safe_filename(track_info.filing_title)
    path_components = [
        cache_location,
    ]
    if cache_heirarchy == 'artist_album':
        path_components.extend(
            [to_safe_filename(track_info.filing_artist),
             to_safe_filename(track_info.filing_album)])

    local_dir = os.path.expanduser(os.path.join(*path_components))

    local_filepath = os.path.join(local_dir, local_filepath)

    logging.info("caching song: id %s; artist %s; album %s; title %s; path %s",
                 to_safe_print(track_info.track_id), to_safe_print(track_info.filing_artist),
                 to_safe_print(track_info.filing_album), to_safe_print(track_info.filing_title),
                 to_safe_print(local_filepath))

    if not os.path.exists(local_dir):
        os.makedirs(local_dir)

    return local_filepath


def cache_track(api, parser_args, track_id, track_info=None):
    """
    Cache a single track from the API.
    """

    info_obj = TrackInfo(track_id, track_info)

    cache_url = api.get_stream_url(track_id)
    logging.info("cache_url: %s", to_safe_print(cache_url))

    req = requests.get(cache_url, stream=True)

    local_filepath = get_local_filepath(parser_args.cache_location, parser_args.cache_heirarchy,
                                        info_obj)

    with open(local_filepath, 'wb') as loc_file:
        for chunk in req.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                loc_file.write(chunk)
        logging.info("wrote file %s", loc_file.name)
        loc_file.flush()

    save_meta(local_filepath, info_obj)

    logging.info("taking a nap")
    time.sleep(float(parser_args.sleep_time))

    return local_filepath


def cache_playlist(api, parser_args):
    """
    Cache an entire playlist from the API.
    """

    library = Library(api.get_all_user_playlist_contents())
    source_playlist = library.find_playlist(parser_args.playlist)

    cached_playlist = None
    if parser_args.playlist_cached:
        try:
            cached_playlist = library.find_playlist(parser_args.playlist_cached)
        except PlaylistNotFoundException:
            cached_playlist = {
                'name': parser_args.playlist_cached,
                'id': api.create_playlist(parser_args.playlist_cached)
            }

    failed_tracks = []

    for track in source_playlist['tracks']:
        track_id = track['trackId']
        track_info = track.get('track')
        try:
            filename = cache_track(api, parser_args, track_id, track_info)
            logging.info("succesfully cached to %s", to_safe_print(filename))

            if parser_args.playlist_cached:
                response = api.add_songs_to_playlist(cached_playlist['id'], [track_id])
                logging.info("added song to cached playlist %s with name %s. response: %s",
                             repr(cached_playlist['name']),
                             repr(cached_playlist['id']),
                             repr(response))
        except gmusicapi.exceptions.CallFailure:
            logging.info("failed to get streaming url, "
                         "try updating your device id: "
                         "https://github.com/simon-weber/gmusicapi/issues/590")
            exit()
        except Exception as exc:
            failed_tracks.append(track)
            logging.info("\n\n!!! failed to cache track, %s. info: %s, exception: %s", track_id,
                         track_info, exc)

    if failed_tracks:
        logging.warning("tracks that failed")
        for track in failed_tracks:
            logging.warning("-> %s %s", track.get('trackID'), track.get('track'))
    elif parser_args.clear_playlist and parser_args.playlist_cached:
        api.remove_entries_from_playlist([
            entry['id'] for entry in source_playlist['tracks']
        ])


def main(argv=None):
    """
    Parse arguments, set up debugging and cache metadata.
    """
    api = Mobileclient()

    parser_args = get_parser_args(argv)

    logging_args = {
        'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        'datefmt': '%m-%d %H:%M'
    }
    if parser_args.debug_level:
        logging_args['level'] = DEBUG_LEVELS[parser_args.debug_level]

    logging.basicConfig(**logging_args)

    for item, value in list(vars(parser_args).items()):
        if item == "pwd":
            continue
        logging.info("Parser arg: %15s = %s", item, value)

    if not os.path.exists(api.OAUTH_FILEPATH):
        logging.info("performing oauth")

        perform_oauth_args = {'open_browser': parser_args.oauth_browser}
        if parser_args.oauth_creds_file:
            perform_oauth_args['storage_filepath'] = parser_args.oauth_creds_file
        api.perform_oauth(**perform_oauth_args)

    logging.info("logging in to api")
    response = api.oauth_login(device_id=parser_args.device_id)

    if response:
        logging.info("api response: %s", response)
        cache_playlist(api, parser_args)
    else:
        raise BadLoginException("Bad login. Check creds and internet")


if __name__ == '__main__':
    main()
