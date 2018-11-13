from unittest import TestCase, main

from text_preparation import extract_hashtags, extract_hashtags_from_corpus


class TestTextPreparation(TestCase):

    def setUp(self):
        self.corpus = [
            "",
            "hello #world",
            "##",
            "I love #Python! #Python for #President!",
            "Using #Sklearn for text processing",
            "Mathematics is fun!"
        ]

    def test_extract_hashtags(self):
        self.assertSetEqual(extract_hashtags(self.corpus[0]), set())
        self.assertSetEqual(extract_hashtags(self.corpus[1]), {"world"})
        self.assertSetEqual(extract_hashtags(self.corpus[2]), set())
        self.assertSetEqual(extract_hashtags(self.corpus[3]), {"Python", "Python", "President"})
        self.assertSetEqual(extract_hashtags(self.corpus[4]), {"Sklearn"})
        self.assertSetEqual(extract_hashtags(self.corpus[5]), set())

    def test_extract_hashtags_from_corpus(self):
        expected_result = (
            set(),
            {"world"},
            set(),
            {"Python", "Python", "President"},
            {"Sklearn"},
            set()
        )
        for actual, expected in zip(extract_hashtags_from_corpus(self.corpus), expected_result):
            self.assertSetEqual(actual, expected)


if __name__ == "__main__":
    main()
