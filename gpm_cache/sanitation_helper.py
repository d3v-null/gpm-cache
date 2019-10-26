import re
from six import binary_type, iterbytes, text_type, u, unichr  # noqa: W0611

FILENAME_KEEP_CHARS = (' ', '.', '_')


def to_safe_print(thing, errors='backslashreplace'):
    """Take a stringable object of any type, returns a safe ASCII byte str."""
    if isinstance(thing, binary_type):
        thing = u"".join([(unichr(c) if (c in range(0x7f)) else "\\x%02x" % (c, ))
                          for c in iterbytes(thing)])
        # thing = thing.decode('ascii', errors=errors)
    elif not isinstance(thing, text_type):
        thing = text_type(thing)
    return thing.encode('ascii', errors=errors).decode('ascii')


def to_safe_filename(thing):
    """Take a stringable object and return an ASCII string safe for filenames."""
    thing = to_safe_print(thing, errors='ignore')
    re_keep_characters = "[%s]" % ("A-Za-z0-9" + re.escape("".join(FILENAME_KEEP_CHARS)))
    return "".join(c for c in thing if re.match(re_keep_characters, c)).rstrip()
