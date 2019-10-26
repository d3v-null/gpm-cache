"""
Cache information about a GPM playlist using gmusicapi.
"""

from __future__ import absolute_import

import logging
import os
import sys
import re
import time
from argparse import ArgumentParser
from getpass import getpass
from pprint import pformat

import requests

import gmusicapi
import mutagen
from gmusicapi import Mobileclient
from mutagen.easyid3 import EasyID3
from six import binary_type, text_type, iterbytes, u, b, unichr  # noqa: W0611

DEBUG_LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}

FILENAME_KEEP_CHARS = (' ', '.', '_')


class PlaylistNotFoundException(UserWarning):
    pass


class BadLoginException(UserWarning):
    pass


class TrackInfo(object):
    """Helper class stores information about a track."""
    def __init__(self, track_id, track_info):
        track_info = track_info or {}
        self.track_id = track_id
        self.track_info = track_info

    @property
    def id3_meta(self):
        """Return the id3 tags for this object."""

        response = {}
        for meta_key, info_key, mapping_fn in [
            ('artist', 'artist', text_type),
            ('albumartist', 'albumArtist', text_type),
            ('title', 'title', text_type),
            ('album', 'album', text_type),
            ('genre', 'genre', text_type),
            ('tracknumber', 'trackNumber', text_type),
            ('discnumber', 'discNumber', text_type),
            ('date', 'year', text_type),
        ]:
            if self.track_info.get(info_key) is not None:
                response[meta_key] = mapping_fn(self.track_info.get(info_key))

        return response

    @property
    def filing_artist(self):
        """Return the artist under which this track should be filed."""
        filing_artists = \
            [
                self.track_info.get(key) for key in
                ['albumArtist', 'artist', 'composer']
                if self.track_info.get(key)
            ]
        return filing_artists[0] if filing_artists else "Unknown Artist"

    @property
    def filing_album(self):
        response = self.track_info.get('album') if self.track_info.get('album') else "Unkown Album"
        # if self.track_info.get('discNumber'):
        #     response = "%s - disc %s" % (response, self.track_info.get('discNumber'))
        if self.track_info.get('year'):
            response = "%s [%s]" % (response, self.track_info.get('year'))
        return response

    @property
    def filing_title(self):
        response = self.track_info.get('title') if self.track_info.get('title') else self.track_id
        if self.track_info.get('trackNumber') is not None:
            response = "%02d - %s" % (self.track_info.get('trackNumber'), response)
            if self.track_info.get('discNumber') is not None:
                response = "%02d:%s" % (self.track_info.get('discNumber'), response)
        return response


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
    parser.add_argument('--sleep-time',
                        help="Time to sleep in between requests",
                        default=10,
                        type=float)

    # TODO: implement playlist-cached

    parser.add_argument('--cache-location',
                        help="The location in the filesystem to store cached information",
                        default=os.path.join(os.path.expanduser("~"), "gpm-cache"))
    parser.add_argument('--debug-level',
                        help="The level above which debug statements are printed",
                        choices=list(DEBUG_LEVELS.keys()))
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


def to_safe_print(thing, errors='backslashreplace'):
    """Take a stringable object of any type, returns a safe ASCII byte str."""
    if isinstance(thing, binary_type):
        thing = u"".join([(unichr(c) if (c in range(0x7f)) else "\\x%02x" % (c, ))
                          for c in iterbytes(thing)])
        # thing = thing.decode('ascii', errors=errors)
    elif not isinstance(thing, text_type):
        thing = text_type(thing)
    return thing.encode('ascii', errors=errors).decode('ascii')


def to_safe_filename(thing):
    """Take a stringable object and return an ASCII string safe for filenames."""
    thing = to_safe_print(thing, errors='ignore')
    re_keep_characters = "[%s]" % ("A-Za-z0-9" + re.escape("".join(FILENAME_KEEP_CHARS)))
    return "".join(c for c in thing if re.match(re_keep_characters, c)).rstrip()


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


def get_local_filepath(parser_args, track_id, track_info=None):
    """
    Determine the best location to save the track on disk.

    Create dirs if necessary.
    """

    local_filepath = "%s.mp3" % to_safe_filename(track_info.filing_title)
    local_dir = os.path.expanduser(
        os.path.join(*[
            parser_args.cache_location,
            to_safe_filename(track_info.filing_artist),
            to_safe_filename(track_info.filing_album)
        ]))
    # local_dir = os.path.join(track_info.filing_artist, track_info.filing_album)
    # local_dir = os.path.join(parser_args.cache_location, local_dir)
    # local_dir = os.path.expanduser(local_dir)
    local_filepath = os.path.join(local_dir, local_filepath)

    logging.info("caching song: id %s; artist %s; album %s; title %s; path %s",
                 to_safe_print(track_id), to_safe_print(track_info.filing_artist),
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

    print("TODO: add extra meta here like 'cached by gpm-cache'")

    cache_url = api.get_stream_url(track_id)
    logging.info("cache_url: %s", to_safe_print(cache_url))

    req = requests.get(cache_url, stream=True)

    local_filepath = get_local_filepath(parser_args, track_id, info_obj)

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

    library = api.get_all_user_playlist_contents()

    target_playlist = None

    for playlist in library:
        logging.info('found %s %s', to_safe_print(playlist['name']), to_safe_print(playlist['id']))
        if re.match(parser_args.playlist, playlist['name'], re.I):
            logging.info("playlist matched", )
            target_playlist = playlist
            break
        else:
            logging.info("playlist (%s) did not match %s", repr(playlist['name']),
                         repr(parser_args.playlist))

    if target_playlist:
        logging.info("found target playlist %s", pformat(target_playlist))

        failed_tracks = []

        for track in target_playlist['tracks']:
            track_id = track['trackId']
            track_info = track.get('track')
            try:
                filename = cache_track(api, parser_args, track_id, track_info)
                logging.info("succesfully cacheed to %s", to_safe_print(filename))
            except gmusicapi.exceptions.CallFailure:
                logging.info(
                    "failed to get streaming url, "
                    "try updating your device id: "
                    "https://github.com/simon-weber/gmusicapi/issues/590"
                )
                exit()
            except Exception as exc:
                failed_tracks.append(track)
                logging.info("\n\n!!! failed to cache track, %s. info: %s, exception: %s", track_id,
                             track_info, exc)

        if failed_tracks:
            logging.warning("tracks that failed")
            for track in failed_tracks:
                logging.warning("-> %s %s", track.get('trackID'), track.get('track'))
    else:
        raise PlaylistNotFoundException("no playlist matched search string: %s",
                                        repr(parser_args.playlist))


#
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

        perform_oauth_args = {
            'open_browser': parser_args.oauth_browser
        }
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
