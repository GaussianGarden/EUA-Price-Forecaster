from unittest import TestCase, main

from text_preparation import extract_hashtags


class TestTextPreparation(TestCase):

    def test_extract_hashtags(self):
        s1 = ""
        self.assertEqual(extract_hashtags(s1), set())
        s2 = "hello #world"
        self.assertEqual(extract_hashtags(s2), {"world"})
        s3 = "##"
        self.assertEqual(extract_hashtags(s3), set())
        s4 = "I love #Python! #Python for #President!"
        self.assertEqual(extract_hashtags(s4), {"Python", "Python", "President"})


if __name__ == "__main__":
    main()
