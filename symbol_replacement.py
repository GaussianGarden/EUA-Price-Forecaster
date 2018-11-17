replacement_dict = {
    128141: "ring",
    127876: "christmas tree",
    128039: "penguin",
    128031: "fish",
    129408: "crab",
    128587: "greet",
    128034: "slow",
    128561: "shocked",
    8987: "time",
    128663: "car",
    128266: "loud",
    128232: "mail",
    127873: "gift",
    128241: "smart phone",
    9201: "time",
    127942: "trophy",
    128197: "date",
    128201: "downwards trend",
    128202: "charts",
    128680: "alarm",
    127757: "worldwide",
    128338: "time",
    9889: "lightning",
    128200: "upwards trend",
    128077: "thumbs up",
    9989: "good"
}


def get_replacement(char):
    """
    Return the replacement value for the given character
    :param char: A unicode character
    :return: The textual representation of that character or, if not in the replacement dictionary, the character itself
    """
    if char == "":
        raise TypeError("Invalid character passed.")
    return replacement_dict.get(ord(char), char)


def replace_sentence(sentence):
    """
    Return a copy of a given sentence with all characters replaced by get_replacement
    :param sentence: A sentence
    :return: A copy of the sentence where each character has been modified by get_replacement. If a symbol is not
    preceded by a whitespace, this will be enforced here.
    """
    return "".join(["{}{}".format("" if i == 0 or sentence[i-1] == " " or ord(char) not in replacement_dict else " ",
                                  get_replacement(char)) for i, char in enumerate(sentence)])
