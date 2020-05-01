import re

_TAGS = ['x', 'y', 'z', 'j', 'q', 'v', 'w', 'r']

def _normalize_numbers(sentence: str) -> str:
    """ Normalize the numbers in the sentence so that they match a standard format.
    Removes trailing zeros from decimal places

    >>> _normalize_numbers("123.0001")
    '123.0001'
    >>> _normalize_numbers("123.000")
    '123'
    >>> _normalize_numbers("12.10")
    '12.1'
    """
    return re.sub(r"\.(\d*?)0+\b", lambda m: f".{m[1]}" if len(m[1]) else "", sentence)


class NumberTag():
    """ Used to tag MWPs, replacing numbers from the equation with specific tags
    so that the network doesn't get hung up on specific numeric values.

    >>> nt = NumberTag("What is 123.0 added to 1.5 ?", "x = 123.0 + 1.5")
    >>> nt.get_originals()
    ('What is 123 added to 1.5 ?', 'x = 123 + 1.5')
    >>> masked = nt.get_masked(); masked
    ('What is <x> added to <y> ?', 'x = <x> + <y>')
    >>> nt.unmask_sentence(masked[0])
    'What is 123 added to 1.5 ?'

    """
    def __init__(self, sentence, equation):
        self.__original_sentence = _normalize_numbers(sentence)
        self.__original_equation = _normalize_numbers(equation)

        self.__tagged_sentence, self.__tagged_equation, self.__lookup_table = self.__map_numbers(
            self.__original_sentence,
            self.__original_equation)

    def __map_numbers(self, sentence, equation):
        # Replaces numbers in a sentence with keyed tags
        sentence_list = sentence.split()
        equation_list = equation.split()
        lookup_dict = {}

        for i, word in enumerate(sentence_list):
            try:
                maybe_number = float(word)
            except ValueError:
                continue
            # If this throws, we want to know about it so we add more variables to _TAGS.
            key = f"<{_TAGS[len(lookup_dict)]}>"
            lookup_dict[key] = word
            sentence_list[i] = key

        # Invert the lookup_dict to allow fast lookup of words.
        adjust_dict = { v: k for k, v in lookup_dict.items() }

        for i, word in enumerate(equation_list):
            if word in adjust_dict:
                equation_list[i] = adjust_dict[word]
                del adjust_dict[word]

        return " ".join(sentence_list), " ".join(equation_list), lookup_dict

    def get_originals(self):
        return self.__original_sentence, self.__original_equation

    def get_masked(self):
        return self.__tagged_sentence, self.__tagged_equation

    def unmask_sentence(self, sentence):
        """ Unmask a given sentence according to the map created from the original inputs. """
        words = sentence.split()

        for i, word in enumerate(words):
            if word in self.__lookup_table:
                words[i] = self.__lookup_table[word]

        return " ".join(words)

    def __repr__(self):
        return f"NumberTag({repr(self.__original_sentence[:15])}, {repr(self.__original_equation)}, {repr(self.__lookup_table)})"


if __name__ == "__main__":
    import doctest
    doctest.testmod()
