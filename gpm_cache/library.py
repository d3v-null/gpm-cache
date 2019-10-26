import logging
import re
from pprint import pformat

from .exceptions import PlaylistNotFoundException
from .sanitation_helper import to_safe_print


class Library:

    def __init__(self, data):
        self.data = data

    def find_playlist(self, playlist_name):

        for playlist in self.data:
            logging.debug('found %s %s', to_safe_print(playlist['name']),
                          to_safe_print(playlist['id']))
            if re.match(playlist_name, playlist['name'], re.I):
                logging.info("found target playlist %s", pformat(playlist))
                return playlist

        raise PlaylistNotFoundException("no playlist matched search string: %s",
                                        repr(playlist_name))
