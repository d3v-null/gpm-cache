"""
Tests for api_helper module.
"""

from __future__ import print_function, unicode_literals

import json
import os
import sys
import unittest

from gmusicapi import Mobileclient
from six import MovedModule, add_move, b, u  # noqa: W0611

from . import REPO_ROOT, TEST_DATA_DIR

try:
    PATH = sys.path
    sys.path.insert(1, REPO_ROOT)
    from gpm_cache.api_helper import ApiHelper
finally:
    sys.path = PATH

try:
    add_move(MovedModule('mock', 'mock', 'unittest.mock'))
    from six.moves import mock  # noqa: W0611
finally:
    from mock import patch


class TestApiHelper(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(TEST_DATA_DIR, 'library.json')) as library_json:
            self.library = json.load(library_json)

        self.api = Mobileclient()

    @unittest.skip("not yet implemented")
    def test_find_playist(self):
        with \
                patch.object(Mobileclient, 'get_all_user_playlist_contents', return_value=self.library):
            self.assertTrue(ApiHelper.find_playlist(self.api, 'Fake Playlist'))
