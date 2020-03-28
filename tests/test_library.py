# -*- coding: utf8 -*-
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
    PATH = sys.path[:]
    sys.path.insert(1, REPO_ROOT)
    from gpm_cache.library import Library
    from gpm_cache.exceptions import PlaylistNotFoundException
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
            data = json.load(library_json)
            with patch.object(Mobileclient, 'get_all_user_playlist_contents', return_value=data):
                self.library = Library(Mobileclient())

    def test_find_existing_playist(self):
        self.assertTrue(self.library.find_playlist('Fake Playlist'))

    def test_not_find_nonexisting_playist(self):
        with self.assertRaises(PlaylistNotFoundException):
            self.library.find_playlist('Nonexistent Playlist')

    def test_find_or_create_playlist_finds_existing_playlist(self):
        self.assertTrue(self.library.find_or_create_playlist('Fake Playlist'))

    def test_find_or_create_playlist_creates_nonexisting_playlist(self):
        new_name = 'Nonexistent Playlist'
        new_id = 'new_id'
        with patch.object(Mobileclient, 'create_playlist', return_value=new_id):
            self.assertEqual(self.library.find_or_create_playlist(new_name), {
                'name': new_name,
                'id': new_id
            })
