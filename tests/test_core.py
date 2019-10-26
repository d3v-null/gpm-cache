# -*- coding: utf8 -*-
"""
Basic tests for gpm_cache.
"""

from __future__ import print_function, unicode_literals

import json
import os
import shlex
import sys
import unittest
from tempfile import mkdtemp

from gmusicapi import Mobileclient
from six import MovedModule, add_move, b, u  # noqa: W0611

from . import REPO_ROOT, TEST_DATA_DIR

try:
    PATH = sys.path
    sys.path.insert(1, REPO_ROOT)
    from gpm_cache.core import main, get_local_filepath
    from gpm_cache.track_info import TrackInfo
    from gpm_cache.exceptions import BadLoginException, PlaylistNotFoundException
finally:
    sys.path = PATH

try:
    add_move(MovedModule('mock', 'mock', 'unittest.mock'))
    from six.moves import mock  # noqa: W0611
finally:
    from mock import patch


class TestCore(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(TEST_DATA_DIR, 'track_info.json')) as json_fp:
            self.track_info = json.load(json_fp)
        self.info_obj = TrackInfo(track_id=u'T6zn3up2um24dxoggvac6obj7ay',
                                  track_info=self.track_info)
        self.out_dir = mkdtemp()

    def test_get_local_filepath_artist_album(self):
        response = get_local_filepath(cache_location=self.out_dir,
                                      cache_heirarchy='artist_album',
                                      track_info=self.info_obj)
        expected = self.out_dir + '/Moonbase Commander/Southpaw EP 2015/0101  Southpaw.mp3'
        self.assertEqual(response, expected)

    def test_get_local_filepath_flat(self):
        response = get_local_filepath(cache_location=self.out_dir,
                                      cache_heirarchy='flat',
                                      track_info=self.info_obj)
        expected = self.out_dir + '/0101  Southpaw.mp3'
        self.assertEqual(response, expected)


class TestMainMocked(unittest.TestCase):
    dummy_argv = shlex.split("--email 'email' --pwd 'pass' --device-id 'devid' --playlist 'plist' "
                             "--debug-level 'critical'")

    def test_bad_login(self):
        with \
                patch.object(Mobileclient, 'perform_oauth', return_value=None), \
                patch.object(Mobileclient, 'oauth_login', return_value=None), \
                self.assertRaises(BadLoginException):
            main(self.dummy_argv)

    def test_good_login_bad_playlist_contents(self):
        with \
                patch.object(Mobileclient, 'perform_oauth', return_value=None), \
                patch.object(Mobileclient, 'oauth_login', return_value=True), \
                patch.object(Mobileclient, 'get_all_user_playlist_contents', return_value=[]), \
                self.assertRaises(PlaylistNotFoundException):
            main(self.dummy_argv)


if __name__ == '__main__':
    unittest.main()
