import logging
import re
from pprint import pformat

from .exceptions import PlaylistNotFoundException
from .sanitation_helper import to_safe_print


class ApiHelper:
    cached_library = None

    @classmethod
    def find_playlist(cls, api, playlist_name):
        if not cls.cached_library:
            cls.cached_library = api.get_all_user_playlist_contents()

        for playlist in cls.cached_library:
            logging.debug('found %s %s', to_safe_print(playlist['name']),
                          to_safe_print(playlist['id']))
            if re.match(playlist_name, playlist['name'], re.I):
                logging.info("found target playlist %s", pformat(playlist))
                return playlist

        raise PlaylistNotFoundException("no playlist matched search string: %s",
                                        repr(playlist_name))
