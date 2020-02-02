"""Test the parsing library."""
import subprocess

from parsing import (many, string, ParseState, mconcat, lift, chomp_space)

def test_many():
    """Test many."""
    parse_many = many(string('a'))
    assert lift(len, parse_many)(ParseState('a' * 6, 0)).value == 6

def test_chomp_space():
    """Test chomp_space."""
    parse_many_xs = lift(mconcat, many(chomp_space(string('x'))))
    assert lift(len, parse_many_xs)(ParseState(' x xxx x', 0)).value == 5

def test_parsing_lint():
    """Lint the main source file."""
    print(subprocess.check_output(['pylint', 'parsing.py']))
