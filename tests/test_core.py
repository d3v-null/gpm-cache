# -*- coding: utf8 -*-
"""
Basic tests for gpm_cache.
"""

from __future__ import print_function, unicode_literals

import json
import os
import shlex
import shutil
import sys
import unittest
from tempfile import mkdtemp
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC

from gmusicapi import Mobileclient
from six import MovedModule, add_move, b, u  # noqa: W0611

from . import REPO_ROOT, TEST_DATA_DIR

try:
    PATH = sys.path
    sys.path.insert(1, REPO_ROOT)
    import gpm_cache
    from gpm_cache.core import main, get_local_filepath, maybe_download_album_art, save_meta
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

    def test_maybe_download_album_art(self):
        # Given
        expected = self.out_dir + "/B52ucw7kgew7axvye5vldk6rxty.jpg"

        # When
        with patch.object(gpm_cache.core, 'write_stream_to_disk'):
            result = maybe_download_album_art(self.info_obj, self.out_dir)

        # Then
        self.assertEqual(expected, result)

    def test_save_meta(self):
        # Given
        audio_src = os.path.join(TEST_DATA_DIR, 'file_example_MP3_700KB.mp3')
        audio_dst = os.path.join(self.out_dir, 'test.mp3')
        art_srt = os.path.join(TEST_DATA_DIR, 'SampleJPGImage_50kbmb.jpg')
        shutil.copy(audio_src, audio_dst)

        # When
        save_meta(audio_dst, self.info_obj, art_srt)

        # Then
        meta = EasyID3(audio_dst)
        for meta_key, meta_val in self.info_obj.id3_meta.items():
            self.assertEqual(meta[meta_key][0], meta_val)

        meta = ID3(audio_dst)
        self.assertTrue(meta['APIC:Cover'])


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
