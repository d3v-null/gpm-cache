"""
Cache information about a GPM playlist using gmusicapi.
"""

from __future__ import absolute_import
import os
import re
import time
import logging
from pprint import pformat
from builtins import str #pylint: disable=redefined-builtin

import requests
from argparse import ArgumentParser
from gmusicapi import Mobileclient

import mutagen
from mutagen.easyid3 import EasyID3

DEBUG_LEVELS = {
    'debug':logging.DEBUG,
    'info':logging.INFO,
    'warning':logging.WARNING,
    'error':logging.ERROR,
    'critical':logging.CRITICAL
}

FILENAME_KEEP_CHARS = (' ', '.', '_')

# pprint(EasyID3.valid_keys.keys())
def get_parser_args():
    """Parse arguments from cli, env and config files."""

    parser = ArgumentParser(
        description="cache information about a playlist from Google Play Music",
        fromfile_prefix_chars="@"
    )
    parser.add_argument(
        '--email',
        help="The Google Authentication email",
        required=True
    )
    parser.add_argument(
        '--pwd',
        help="The Google Authentication password",
        required=True
    )
    parser.add_argument(
        '--playlist',
        help="The name of the GPM playlist to cache info from",
        required=True
    )

    parser.add_argument(
        '--sleep-time',
        help="Time to sleep in between requests",
        default=10
    )

    # TODO: implement playlist-cached

    parser.add_argument(
        '--cache-location',
        help="The location in the filesystem to store cached information",
        default=os.path.join(os.path.expanduser("~"), "gpm-cache")
    )
    parser.add_argument(
        '--debug-level',
        help="The level above which debug statements are printed",
        choices=list(DEBUG_LEVELS.keys())
    )

    parser_args = parser.parse_args()

    return parser_args

def to_safe_print(thing):
    """Take a stringable object of any type, returns a safe ASCII str."""
    if isinstance(thing, bytes):
        thing = thing.decode('ascii', errors='backslashreplace')
    else:
        thing = str(thing)
    return thing.encode('ascii', errors='backslashreplace')

def to_safe_filename(thing):
    """Take a stringable object and return an ASCII string safe for filenames."""
    return "".join(c for c in str(thing) if c.isalnum() or c in FILENAME_KEEP_CHARS).rstrip()

def save_meta(local_filepath, track_info):
    """Save meta associated with track to the given file."""

    try:
        meta = EasyID3(local_filepath)
    except mutagen.id3.ID3NoHeaderError:
        meta = mutagen.File(local_filepath, easy=True)
        meta.add_tags()

    for meta_key, info_key in [
            ('artist', 'artist'),
            ('albumartist', 'albumArtist'),
            ('title', 'title'),
            ('album', 'album'),
            ('genre', 'genre')
    ]:
        if track_info.get(info_key) is not None:
            meta[meta_key] = track_info.get(info_key)

    # if track_info.get('trackNumber') is not None:
    #     meta['tracknumber'] = track_info.get('trackNumber')
    # if track_info.get('discNumber') is not None:
    #     meta['discnumber'] = track_info.get('discNumber')
    # TODO: meta['date']
    meta.save()

def cache_track(api, parser_args, track_id, track_info=None):
    """
    Cache a single track from the API.
    """

    if not track_info:
        track_info = {}

    filing_artists = \
        [
            track_info.get(key) for key in \
            ['albumArtist', 'artist', 'composer'] \
            if track_info.get(key)
        ]
    filing_artist = filing_artists[0] if filing_artists else "Unknown Artist"
    filing_album = track_info.get('album') if track_info.get('album') else "Unkown Album"
    filing_title = track_info.get('title') if track_info.get('title') else track_id

    local_filepath = "%s.mp3" % to_safe_filename(filing_title)
    if track_info.get('trackNumber') is not None:
        local_filepath = "%02d - %s" % (track_info.get('trackNumber'), local_filepath)
    if track_info.get('discNumber') is not None and track_info.get('trackNumber') is not None:
        local_filepath = "%02d:%s" % (track_info.get('discNumber'), local_filepath)
    local_dir = os.path.join(filing_artist, filing_album)
    local_dir = os.path.join(parser_args.cache_location, local_dir)
    local_dir = os.path.expanduser(local_dir)
    local_filepath = os.path.join(local_dir, local_filepath)

    logging.info(
        "caching song: id %s; artist %s; album %s; title %s; path %s",
        to_safe_print(track_id),
        to_safe_print(filing_artist),
        to_safe_print(filing_album),
        to_safe_print(filing_title),
        to_safe_print(local_filepath)
    )

    if not os.path.exists(local_dir):
        os.makedirs(local_dir)

    cache_url = api.get_stream_url(track_id)
    logging.info("cache_url: %s", to_safe_print(cache_url))

    req = requests.get(cache_url, stream=True)

    with open(local_filepath, 'wb') as loc_file:
        for chunk in req.iter_content(chunk_size=1024):
            if chunk: # filter out keep-alive new chunks
                loc_file.write(chunk)
        logging.info("wrote file %s", loc_file.name)
        loc_file.flush()

    save_meta(local_filepath, track_info)

    logging.info("taking a nap")
    time.sleep(parser_args.sleep_time)

    return local_filepath

def cache_playlist(api, parser_args):
    """
    Cache an entire playlist from the API.
    """
    library = api.get_all_user_playlist_contents()

    target_playlist = None

    for playlist in library:
        logging.info('found %s %s', to_safe_print(playlist['name']), to_safe_print(playlist['id']))
        if re.match(parser_args.playlist, playlist['name'], re.I):
            logging.info("playlist matched",)
            target_playlist = playlist
            break
        else:
            logging.info(
                "playlist (%s) did not match %s",
                repr(playlist['name']),
                repr(parser_args.playlist)
            )

    if target_playlist:
        logging.info("found target playlist %s", pformat(target_playlist))

        for track in target_playlist['tracks']:
            track_id = track['trackId']
            track_info = track.get('track')
            filename = cache_track(api, parser_args, track_id, track_info)
            logging.info("succesfully cacheed to %s", to_safe_print(filename))
    else:
        logging.warning("no playlist matched search string: %s", repr(parser_args.playlist))

#
def main():
    """
    Parse arguments, set up debugging and cache metadata.
    """
    api = Mobileclient()

    parser_args = get_parser_args()

    logging_args = {
        'format':'%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        'datefmt':'%m-%d %H:%M'
    }
    if parser_args.debug_level:
        logging_args['level'] = DEBUG_LEVELS[parser_args.debug_level]

    logging.basicConfig(**logging_args)

    for item, value in list(vars(parser_args).items()):
        logging.info("Parser arg: %15s = %s", item, value)

    logging.info("logging in to api")

    logging.info(
        'types of email and pwd: %s, %s',
        type(parser_args.email),
        type(parser_args.pwd)
    )

    response = api.login(
        parser_args.email,
        parser_args.pwd,
        Mobileclient.FROM_MAC_ADDRESS
    )
    if response:
        logging.info("api response: %s", response)
    else:
        logging.info("no api response")

    cache_playlist(api, parser_args)

if __name__ == '__main__':
    main()
