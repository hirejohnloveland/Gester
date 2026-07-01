import pytest

from gester.infrastructure.simple_utils import (
    celsius_to_fahrenheit,
    count_words,
    reverse_string,
)


class TestReverseString:
    def test_reverses_simple_word(self):
        assert reverse_string("hello") == "olleh"

    def test_reverses_sentence_with_spaces(self):
        assert reverse_string("hello world") == "dlrow olleh"

    def test_empty_string_returns_empty_string(self):
        assert reverse_string("") == ""

    def test_single_character_is_unchanged(self):
        assert reverse_string("a") == "a"

    def test_palindrome_is_unchanged(self):
        assert reverse_string("racecar") == "racecar"

    def test_reverses_string_with_punctuation_and_numbers(self):
        assert reverse_string("abc123!?") == "?!321cba"

    def test_reverses_unicode_characters(self):
        assert reverse_string("héllo") == "olléh"

    def test_double_reverse_returns_original(self):
        text = "The quick brown fox"
        assert reverse_string(reverse_string(text)) == text


class TestCountWords:
    def test_counts_words_in_simple_sentence(self):
        assert count_words("hello world") == 2

    def test_counts_single_word(self):
        assert count_words("hello") == 1

    def test_empty_string_has_zero_words(self):
        assert count_words("") == 0

    def test_whitespace_only_string_has_zero_words(self):
        assert count_words("   ") == 0

    def test_collapses_multiple_spaces_between_words(self):
        assert count_words("hello    world") == 2

    def test_ignores_leading_and_trailing_whitespace(self):
        assert count_words("  hello world  ") == 2

    def test_counts_words_separated_by_newlines_and_tabs(self):
        assert count_words("hello\nworld\tfoo") == 3

    def test_counts_many_words(self):
        sentence = "the quick brown fox jumps over the lazy dog"
        assert count_words(sentence) == 9


class TestCelsiusToFahrenheit:
    def test_freezing_point_of_water(self):
        assert celsius_to_fahrenheit(0) == 32

    def test_boiling_point_of_water(self):
        assert celsius_to_fahrenheit(100) == 212

    def test_body_temperature(self):
        assert celsius_to_fahrenheit(37) == pytest.approx(98.6)

    def test_negative_temperature(self):
        assert celsius_to_fahrenheit(-40) == -40

    def test_fractional_celsius_value(self):
        assert celsius_to_fahrenheit(36.6) == pytest.approx(97.88)

    def test_returns_numeric_type_for_int_input(self):
        result = celsius_to_fahrenheit(20)
        assert isinstance(result, (int, float))
        assert result == pytest.approx(68)