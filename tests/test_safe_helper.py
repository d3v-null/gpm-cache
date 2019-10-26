# -*- coding: utf8 -*-
import sys
import unittest

from . import REPO_ROOT

try:
    PATH = sys.path
    sys.path.insert(1, REPO_ROOT)
    from gpm_cache.sanitation_helper import to_safe_filename, to_safe_print
finally:
    sys.path = PATH


class TestSafeHelpers(unittest.TestCase):
    """Test safe helper module of gpm_cache."""
    def test_safe_print(self):
        response = to_safe_print("hello")
        self.assertEqual(response, "hello")

        response = to_safe_print(u"hëllo")
        self.assertEqual(response, "h\\xebllo")
        for char in list(response):
            self.assertLessEqual(ord(char), 128)

        response = to_safe_print(b"\x80abc")
        self.assertEqual(response, "\\x80abc")

        response = to_safe_print((b"\x80abc", u"\x80s"))
        for char in list(response):
            self.assertLessEqual(ord(char), 128)

    def test_safe_filename(self):
        response = to_safe_filename(u"hellö#my~baby")
        self.assertEqual(response, "hellmybaby")
