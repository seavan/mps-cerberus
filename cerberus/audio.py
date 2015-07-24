# encoding: utf-8

import mutagen

def get_vorbis_comment(obj, key):
    try:
        value = obj[key][0]
    except (KeyError, ValueError) as e:
        return None

    return value

def get_id3_tag(obj, key):
    try:
        value = obj.tags[key].text[0]
    except Exception as e:
        return None

    return value

def get_metadata(filename):
    result = {
        "album": None,
        "artist": None,
        "title": None
    }

    f = mutagen.File(filename)

    if isinstance(f, mutagen.mp3.MP3):
        result['artist'] = get_id3_tag(f, 'TPE1')
        result['title'] = get_id3_tag(f, 'TIT2')
        result['album'] = get_id3_tag(f, 'TALB')

    elif isinstance(f, mutagen.flac.FLAC):
        result['artist'] = get_vorbis_comment(f, 'artist')
        result['title'] = get_vorbis_comment(f, 'title')
        result['album'] = get_vorbis_comment(f, 'album')

    return result
