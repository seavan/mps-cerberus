# encoding: utf-8

import mutaget

def parse_metadata(filename):
    result = {
        "album": None,
        "artist": None,
        "title": None
    }

    f = mutagen.File(filename)
    result['artist'] = f['TPE1']
    result['title' = f['TIT2']
    result['album'] = f['TALB']

    return result
