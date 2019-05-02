"""Test FAST extractor."""

from os.path import dirname, join, realpath

from cd2h_repo_project.modules.mesh.fast import FAST


class TestFAST(object):
    """Test FAST extractor."""
    filename = 'fast_test_file.nt'

    @classmethod
    def filepath(cls):
        return join(dirname(realpath(__file__)), cls.filename)

    def test_load_topics(self):

        topics = FAST.load(TestFAST.filepath())

        assert topics == [
            {
                'prefLabel': 'Civil defense--Safety measures',
                'identifier': 862474,
            },
            {
                'prefLabel': 'Architecture, Regency',
                'identifier': 813916,
            },
            {
                'prefLabel': 'Broad beechfern',
                'identifier': 1738210,
            },
            {
                'prefLabel': 'Onions--Diseases and pests--Control',
                'identifier': 1045901,
            },
        ]

    def test_load_zipped_topics(self):
        tmp_filename = TestFAST.filename
        FAST.filename = 'fast_test_file.nt.zip'

        topics = FAST.load(TestFAST.filepath())

        assert topics == [
            {
                'prefLabel': 'Civil defense--Safety measures',
                'identifier': 862474,
            },
            {
                'prefLabel': 'Architecture, Regency',
                'identifier': 813916,
            },
            {
                'prefLabel': 'Broad beechfern',
                'identifier': 1738210,
            },
            {
                'prefLabel': 'Onions--Diseases and pests--Control',
                'identifier': 1045901,
            },
        ]

        FAST.filename = tmp_filename
