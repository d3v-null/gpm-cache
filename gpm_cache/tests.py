# -*- coding: utf8 -*-
"""
Basic tests for gpm_cache.
"""

from __future__ import print_function, unicode_literals

import shlex
import unittest
import sys

from gmusicapi import Mobileclient
from .core import (PlaylistNotFoundException, BadLoginException, TrackInfo, to_safe_filename,
                       to_safe_print, main)
from six import MovedModule, add_move, b, u

if True:
    add_move(MovedModule('mock', 'mock', 'unittest.mock'))
    from six.moves import mock

    from mock import patch



class TestMainMocked(unittest.TestCase):
    dummy_argv = shlex.split(
        "--email 'email' --pwd 'pass' --device-id 'devid' --playlist 'plist' "
        "--debug-level 'critical'"
    )

    def test_bad_login(self):
        with \
            patch.object(Mobileclient, 'login', return_value=None), \
            self.assertRaises(BadLoginException) \
        :
            main(self.dummy_argv)

    def test_good_login_bad_playlist_contents(self):
        with \
            patch.object(Mobileclient, 'login', return_value=True), \
            patch.object(Mobileclient, 'get_all_user_playlist_contents', return_value=[]), \
            self.assertRaises(PlaylistNotFoundException) \
        :
            main(self.dummy_argv)


class TestHelpers(unittest.TestCase):
    """Test helper functions of gpm_cache."""

    def test_safe_print(self):
        response = to_safe_print("hello")
        self.assertEqual(response, "hello")

        response = to_safe_print(u"hëllo")
        self.assertEqual(response, "h\\xebllo")
        for char in list(response):
            self.assertLessEqual(ord(char), 128)

        response = to_safe_print(b"\x80abc")
        self.assertEqual(response, "\\x80abc")

        response = to_safe_print((b"\x80abc",u"\x80s"))
        for char in list(response):
            self.assertLessEqual(ord(char), 128)

    def test_safe_filename(self):
        response = to_safe_filename(u"hellö#my~baby")
        self.assertEqual(response, "hellmybaby")

class TestTrackInfo(unittest.TestCase):
    """Test TrackInfo helper class."""

    track_info = {
        u'album': u'Southpaw EP',
        u'albumArtRef': [
            {
                u'aspectRatio': u'1',
                u'autogen': False,
                u'kind': u'sj#imageRef',
                u'url': \
(u'http://lh3.googleusercontent.com/'
 u'JPIzh3RwQ8E3tuW9iiCd8SSA7xSDGwHeplgP2d903AmibiDpX5_zkPa2rDFsYheTkeyi_nA7lw')
            }
        ],
        u'albumArtist': u'Moonbase Commander',
        u'albumAvailableForPurchase': False,
        u'albumId': u'B52ucw7kgew7axvye5vldk6rxty',
        u'artist': u'Moonbase Commander',
        u'artistArtRef': [
            {
                u'aspectRatio': u'2',
                u'autogen': True,
                u'kind': u'sj#imageRef',
                u'url': \
(u'http://lh3.googleusercontent.com/'
 u'Y7bfPNOK1Y2besTzlMMPq_IbMyxf0B3lP_nNfa41CCxaF0MyBYDknVxu6cZO-RrPEXVrrAJRyg')
            },
            {
                u'aspectRatio': u'1',
                u'autogen': True,
                u'kind': u'sj#imageRef',
                u'url': \
(u'http://lh3.googleusercontent.com/'
 u'qa82ufTF4bZLbveox1RoR93yCwM60hbXO5NvUH91gjR8KLLSHCeNnxXbjU_TtQTYiFQyPA_voQ')
            }
        ],
        u'artistId': [u'Aefmiddcllvc6xda7wyj7w3r3yy'],
        u'composer': u'',
        u'discNumber': 1,
        u'durationMillis': u'213000',
        u'estimatedSize': u'8557841',
        u'explicitType': u'2',
        u'genre': u'Dance/Electronic',
        u'kind': u'sj#track',
        u'nid': u'6zn3up2um24dxoggvac6obj7ay',
        u'playCount': 1,
        u'storeId': u'T6zn3up2um24dxoggvac6obj7ay',
        u'title': u'Southpaw',
        u'trackAvailableForPurchase': True,
        u'trackAvailableForSubscription': True,
        u'trackNumber': 1,
        u'trackType': u'7',
        u'year': 2015
    }

    def test_basic(self):
        info_obj = TrackInfo(
            track_id=u'T6zn3up2um24dxoggvac6obj7ay',
            track_info=self.track_info
        )

        self.assertEquals(
            info_obj.id3_meta,
            {
                'album': 'Southpaw EP',
                'title': 'Southpaw',
                'artist': 'Moonbase Commander',
                'albumartist': 'Moonbase Commander',
                'date': '2015',
                'genre': 'Dance/Electronic',
                'discnumber': '1',
                'tracknumber': '1'
            }
        )
        self.assertEqual(
            info_obj.filing_album,
            'Southpaw EP [2015]'
        )
        self.assertEqual(
            info_obj.filing_artist,
            'Moonbase Commander'
        )
        self.assertEqual(
            info_obj.filing_title,
            '01:01 - Southpaw'
        )

if __name__ == '__main__':
    unittest.main()
