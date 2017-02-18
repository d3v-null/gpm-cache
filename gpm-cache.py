import sys
import os
import re
import time
from gmusicapi import Mobileclient
from pprint import pprint
import requests
from argparse import ArgumentParser

import mutagen
from mutagen.easyid3 import EasyID3

import logging

# pprint(EasyID3.valid_keys.keys())

api = Mobileclient()

debug_levels = {
    'debug':logging.DEBUG,
    'info':logging.INFO,
    'warning':logging.WARNING,
    'error':logging.ERROR,
    'critical':logging.CRITICAL
}

parser = ArgumentParser(description="cache information about a playlist from Google Play Music")
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
    '--cache-location',
    help="The location in the filesystem to store cached information",
    default=os.path.join(os.path.expanduser("~"), "gpm-cache")
)
parser.add_argument(
    '--debug-level',
    help="The level above which debug statements are printed",
    choices=debug_levels.keys()
)

parser_args = parser.parse_args()

logging_args = {
    'format':'%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
    'datefmt':'%m-%d %H:%M'
}
if parser_args.debug_level:
    logging_args['level'] = debug_levels[parser_args.debug_level]

logging.basicConfig(**logging_args)

for item, value in vars(parser_args).items():
    logging.info("Parser arg: %15s = %s", item, value)

logging.info("logging in to api")
response = api.login(parser_args.email, parser_args.pwd, Mobileclient.FROM_MAC_ADDRESS)
if response:
    logging.info("api response: %s", response)
else:
    logging.info("no api response")
# => True

def to_safe_print(thing):
    return unicode(thing).encode('ascii', errors='backslashreplace')

filenameKeepCharacters = (' ','.','_')
def to_safe_filename(thing):
    return "".join(c for c in unicode(thing) if c.isalnum() or c in filenameKeepCharacters).rstrip()

def cache_track(track_id, track_info={}):
    track_artist = track_info.get('artist')
    track_album = track_info.get('album')
    track_album_artist = track_info.get('albumArtist')
    track_composer = track_info.get('composer')
    track_disc_number = track_info.get('discNumber')
    track_genre = track_info.get('genre')
    track_title = track_info.get('title')
    track_number = track_info.get('trackNumber')
    track_year = track_info.get('year')

    try:
        filing_artist = filter(None, [track_album_artist, track_artist, track_composer])[0]
    except:
        filing_artist = "Unknown Artist"

    filing_album = track_album if track_album else "Unkown Album"
    filing_title = track_title if track_title else track_id

    local_filename = "%s.mp3" % to_safe_filename(filing_title)
    if track_number is not None:
        local_filename = "%02d - %s" % (track_number, local_filename)
    if track_disc_number is not None and track_number is not None:
        local_filename = "%02d:%s" % (track_disc_number, local_filename)
    local_dir = os.path.join(filing_artist, filing_album)
    local_dir = os.path.join(parser_args.cache_location, local_dir)
    local_filepath = os.path.join(local_dir, local_filename)

    logging.info( "caching song: id %s; artist %s; album %s; title %s; path %s",
        to_safe_print(track_id),
        to_safe_print(filing_artist),
        to_safe_print(filing_album),
        to_safe_print(filing_title),
        to_safe_print(local_filepath)
    )

    cache_url = api.get_stream_url(track_id)
    logging.info( "cache_url: %s" % to_safe_print(cache_url))

    r = requests.get(cache_url, stream=True)

    if not os.path.exists(local_dir):
        os.makedirs(local_dir)

    with open(local_filepath, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk: # filter out keep-alive new chunks
                logging.info( "writing chunk")
                f.write(chunk)
                #f.flush() commented by recommendation from J.F.Sebastian

        f.flush()

    try:
        meta = EasyID3(local_filepath)
    except mutagen.id3.ID3NoHeaderError:
        meta = mutagen.File(local_filepath, easy=True)
        meta.add_tags()

    if track_artist is not None:
        meta['artist'] = track_artist
    if track_album_artist is not None:
        meta['albumartist'] = track_album_artist
    if track_title is not None:
        meta['title'] = track_title
    if track_album is not None:
        meta['album'] = track_album
    if track_genre is not None:
        meta['genre'] = track_genre
    # if track_number is not None:
    #     meta['tracknumber'] = track_number
    # if track_disc_number is not None:
    #     meta['discnumber'] = track_disc_number
    # TODO: meta['date']
    meta.save()

    logging.info("taking a nap")
    time.sleep(10)

    return local_filepath

def cache_playlist(playlist_name):
    library = api.get_all_user_playlist_contents()

    target_playlist = None

    for playlist in library:
        logging.info( 'found %s %s', to_safe_print(playlist['name']), to_safe_print(playlist['id']))
        if re.match(playlist_name, playlist['name'], re.I):
            target_playlist = playlist

    if target_playlist:
        logging.info("found target playlist %s", pprint(target_playlist))

        for track in target_playlist['tracks']:
            track_id = track['trackId']
            track_info = track['track']
            filename = cache_track(track_id, track_info)
            print "succesfully cacheed to", to_safe_print(filename)

cache_playlist(parser_args.playlist)
