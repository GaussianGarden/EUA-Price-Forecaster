from unittest import TestCase, main

from twitter_grabber.symbol_replacement import get_replacement, replace_sentence


class TestSymbolReplacement(TestCase):

    def setUp(self):
        self.corpus = [
            "I usually go to work by 🚗.",
            "Good morning!",
            "This is my🚗.",
            "Wow, 👍, that was really ✅."
        ]
        self.chars = [
            "😱",
            "",
            "h"
        ]

    def test_get_replacement(self):
        self.assertEqual(get_replacement("😱"), "shocked")
        with self.assertRaises(TypeError):
            get_replacement("")
        self.assertEqual(get_replacement("h"), "h")

    def test_replace_sentence(self):
        expected_result = [
            "I usually go to work by car.",
            "Good morning!",
            "This is my car.",
            "Wow, thumbs up, that was really good."
        ]
        for actual, expected in zip([replace_sentence(sentence) for sentence in self.corpus], expected_result):
            self.assertEqual(actual, expected)


if __name__ == "__main__":
    main()
