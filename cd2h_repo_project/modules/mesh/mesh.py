"""MeSH term loader."""
import re


class RetainedMatch(object):
    """Retained Match. More convenient API around matching."""

    _prev_match = None  # act as short lived memento pattern

    @classmethod
    def match(cls, pattern, text):
        """Return re.match but save result until next `match` call."""
        cls._prev_match = re.match(pattern, text)
        return cls._prev_match

    @classmethod
    def group(cls, index):
        """Return matched group from saved match."""
        return cls._prev_match.group(index) if cls._prev_match else None


class MeSH(object):
    """MeSH term extractor."""

    filter_to_dc = {
        'all': '\d',
        'topics': '1',
        'types': '2',
        'check_tags': '3',
        'geographics': '4'
    }

    @classmethod
    def _pattern(cls, key):
        return r'{} = (.+)'.format(key)

    @classmethod
    def load(cls, filepath, filter='all'):
        """Return array of MeSH dict. Main method."""
        terms = []

        with open(filepath, 'r') as f:
            term = {}

            for l in f.readlines():
                if RetainedMatch.match(MeSH._pattern('MH'), l):
                    term['MH'] = RetainedMatch.group(1).strip()
                elif RetainedMatch.match(MeSH._pattern('DC'), l):
                    term['DC'] = RetainedMatch.group(1).strip()
                elif RetainedMatch.match(MeSH._pattern('UI'), l):
                    term['UI'] = RetainedMatch.group(1).strip()

                    if re.match(term['DC'], MeSH.filter_to_dc[filter]):
                        terms.append(term)

                    term = {}

        return terms
