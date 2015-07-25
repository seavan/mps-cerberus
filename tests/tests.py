#!/usr/bin/env python
# encoding: utf-8

import os
import sys
import unittest

from os.path import join

sys.path.append(os.path.abspath(join(
  os.path.dirname(os.path.realpath(__file__)), '..')))

from cerberus.audio import *

content_dir = join(os.path.dirname(os.path.realpath(__file__)), 'content')

class TestGetMetadata(unittest.TestCase):

    def test_mp3_with_en_metadata(self):
        expected = {
          'artist': 'Protest the Hero',
          'album': 'Fortress',
          'title': 'Untitled'
        }

        metadata = get_metadata(join(content_dir, 'mp3_with_en_metadata.mp3'))
        self.assertEqual(expected, metadata)

    def test_mp3_with_ru_utf8_metadata(self):
        expected = {
          'artist': u'ГАМОРА',
          'album': u'Персо.ножи',
          'title': u'Кислород'
        }

        metadata = get_metadata(join(content_dir, 'mp3_with_utf-16_with_BOM_metadata.mp3'))
        self.assertEqual(expected, metadata)

    def test_mp3_with_ru_cp1251_metadata(self):
        self.maxDiff = None
        expected = {
          'artist': u'BRUTTO',
          'album': u'Воины света (Single)',
          'title': u'Воины света ( Cover version )'
        }

        metadata = get_metadata(join(content_dir, 'mp3_with_cp1251_metadata.mp3'))
        self.assertEqual(expected, metadata)

    def test_flac_with_en_metadata(self):
        expected = {
          'artist': 'The Sixteen - Harry Christophers',
          'album': 'Messiah',
          'title': 'Hallelujah (Chorus)'
        }

        metadata = get_metadata(join(content_dir, 'flac_with_en_metadata.flac'))
        self.assertEqual(expected, metadata)

if __name__ == '__main__':
    unittest.main()
