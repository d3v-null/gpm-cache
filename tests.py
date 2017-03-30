# -*- coding: utf8 -*-
"""
Basic tests for gpm_cache.
"""

import unittest
from gpm_cache import to_safe_print, to_safe_filename

class TestHelpers(unittest.TestCase):
    """Test helper functions of gpm_cache."""

    def test_safe_print(self):
        response = to_safe_print("hello")
        self.assertEqual(response, "hello")

        response = to_safe_print(u"hëllo")
        self.assertEqual(response, "h\\xebllo")
        for char in list(response):
            self.assertLessEqual(char, 128)

        response = to_safe_print(b"\x80abc")
        self.assertEqual(response, "\\x80abc")

    def test_safe_filename(self):
        response = to_safe_filename(u"hellö#my~baby")
        self.assertEqual(response, "hellmybaby")

if __name__ == '__main__':
    unittest.main()
