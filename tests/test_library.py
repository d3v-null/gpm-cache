"""
Tests for api_helper module.
"""

from __future__ import print_function, unicode_literals

import json
import os
import sys
import unittest

from six import MovedModule, add_move, b, u  # noqa: W0611

from . import REPO_ROOT, TEST_DATA_DIR

try:
    PATH = sys.path
    sys.path.insert(1, REPO_ROOT)
    from gpm_cache.library import Library
    from gpm_cache.exceptions import PlaylistNotFoundException
finally:
    sys.path = PATH


class TestApiHelper(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(TEST_DATA_DIR, 'library.json')) as library_json:
            self.library = Library(json.load(library_json))

    def test_find_existing_playist(self):

        self.assertTrue(self.library.find_playlist('Fake Playlist'))

    def test_not_find_nonexisting_playist(self):
        with self.assertRaises(PlaylistNotFoundException):
            self.library.find_playlist('Nonexistent Playlist')
