"""Test MeSH extractor."""

from os.path import dirname, join, realpath

from cd2h_repo_project.modules.mesh.mesh import MeSH


class TestMeSH(object):
    """Test MeSH extractor."""
    filename = 'descriptors_test_file.txt'
    filepath = join(dirname(realpath(__file__)), filename)

    def test_load_topics(self):

        topics = MeSH.load(TestMeSH.filepath, filter='topics')

        assert topics == [
            {
                'MH': 'Abnormalities, Multiple',
                'DC': '1',
                'UI': 'D000015'
            },
            {
                'MH': 'Seed Bank',
                'DC': '1',
                'UI': 'D000068098'
            },
            {
                'MH': 'Filariasis',
                'DC': '1',
                'UI': 'D005368'
            },
            {
                'MH': 'Congenital Abnormalities',
                'DC': '1',
                'UI': 'D000013'
            },
            {
                'MH': 'Abdominal Injuries',
                'DC': '1',
                'UI': 'D000007'
            },
            {
                'MH': 'Abdominal Neoplasms',
                'DC': '1',
                'UI': 'D000008'
            },
            {
                'MH': 'Abbreviations as Topic',
                'DC': '1',
                'UI': 'D000004'
            },
            {
                'MH': 'Abdomen',
                'DC': '1',
                'UI': 'D000005'
            }
        ]
