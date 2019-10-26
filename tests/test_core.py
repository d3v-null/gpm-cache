# -*- coding: utf8 -*-
"""
Basic tests for gpm_cache.
"""

from __future__ import print_function, unicode_literals

import shlex
import sys
import unittest

from gmusicapi import Mobileclient
from six import MovedModule, add_move, b, u  # noqa: W0611

from . import REPO_ROOT

try:
    PATH = sys.path
    sys.path.insert(1, REPO_ROOT)
    from gpm_cache.core import main
    from gpm_cache.exceptions import BadLoginException, PlaylistNotFoundException
finally:
    sys.path = PATH

try:
    add_move(MovedModule('mock', 'mock', 'unittest.mock'))
    from six.moves import mock  # noqa: W0611
finally:
    from mock import patch


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
