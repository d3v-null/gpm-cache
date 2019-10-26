from six import b, binary_type, iterbytes, text_type, u, unichr  # noqa: W0611


class TrackInfo(object):
    """Helper class stores information about a track."""
    def __init__(self, track_id, track_info):
        track_info = track_info or {}
        self.track_id = track_id
        self.track_info = track_info

    @property
    def id3_meta(self):
        """Return the id3 tags for this object."""

        response = {}
        for meta_key, info_key, mapping_fn in [
            ('artist', 'artist', text_type),
            ('albumartist', 'albumArtist', text_type),
            ('title', 'title', text_type),
            ('album', 'album', text_type),
            ('genre', 'genre', text_type),
            ('tracknumber', 'trackNumber', text_type),
            ('discnumber', 'discNumber', text_type),
            ('date', 'year', text_type),
        ]:
            if self.track_info.get(info_key) is not None:
                response[meta_key] = mapping_fn(self.track_info.get(info_key))

        return response

    @property
    def filing_artist(self):
        """Return the artist under which this track should be filed."""
        filing_artists = \
            [
                self.track_info.get(key) for key in
                ['albumArtist', 'artist', 'composer']
                if self.track_info.get(key)
            ]
        return filing_artists[0] if filing_artists else "Unknown Artist"

    @property
    def filing_album(self):
        response = self.track_info.get('album') if self.track_info.get('album') else "Unkown Album"
        # if self.track_info.get('discNumber'):
        #     response = "%s - disc %s" % (response, self.track_info.get('discNumber'))
        if self.track_info.get('year'):
            response = "%s [%s]" % (response, self.track_info.get('year'))
        return response

    @property
    def filing_title(self):
        response = self.track_info.get('title') if self.track_info.get('title') else self.track_id
        if self.track_info.get('trackNumber') is not None:
            response = "%02d - %s" % (self.track_info.get('trackNumber'), response)
            if self.track_info.get('discNumber') is not None:
                response = "%02d:%s" % (self.track_info.get('discNumber'), response)
        return response
