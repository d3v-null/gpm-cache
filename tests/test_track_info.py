# -*- coding: utf8 -*-
import json
import os
import sys
import unittest

from . import REPO_ROOT, TEST_DATA_DIR

try:
    PATH = sys.path
    sys.path.insert(1, REPO_ROOT)
    from gpm_cache.track_info import TrackInfo
finally:
    sys.path = PATH


class TestTrackInfo(unittest.TestCase):
    """Test TrackInfo helper class."""
    def setUp(self):
        with open(os.path.join(TEST_DATA_DIR, 'track_info.json')) as json_fp:
            self.track_info = json.load(json_fp)

    def test_basic(self):
        info_obj = TrackInfo(track_id=u'T6zn3up2um24dxoggvac6obj7ay', track_info=self.track_info)

        self.assertEquals(
            info_obj.id3_meta, {
                'album': 'Southpaw EP',
                'title': 'Southpaw',
                'artist': 'Moonbase Commander',
                'albumartist': 'Moonbase Commander',
                'date': '2015',
                'genre': 'Dance/Electronic',
                'discnumber': '1',
                'tracknumber': '1'
            })
        self.assertEqual(info_obj.filing_album, 'Southpaw EP [2015]')
        self.assertEqual(info_obj.filing_artist, 'Moonbase Commander')
        self.assertEqual(info_obj.filing_title, '01:01 - Southpaw')
