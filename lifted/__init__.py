"""Parser combinator framework."""

from collections import namedtuple

class Error(Exception):
  """Module error class."""

class ParserError(Error):
  """Likely an error exists in the parser."""

# The current location of the parser.
ParseState = namedtuple('ParseState', ['text', 'pos'])

# A value from a parser, and the next parse state.
Parsing = namedtuple('Parsing', ['value', 'parse_state'])

def parse_string(parse_state, s):
  """Parse a specific string."""
  pos = parse_state.pos
  len_input = len(parse_state.text)
  if pos + len(s) > len_input:
    return None
  i = 0
  len_s = len(s)
  while i < len_s and parse_state.text[pos] == s[i]:
    pos += 1
    i += 1

  if pos - parse_state.pos == len_s:
    return Parsing(parse_state.text[parse_state.pos:pos],
                   ParseState(parse_state.text, pos))

def compose(f, g):
  """1-arity function composition."""
  return lambda x: f(g(x))

def mconcat(xs):
  """Concatenate strings that are not None from a sequence."""
  return ''.join([x for x in xs if x is not None])

def constant(x):
  """Always return the given value, ignoring the input."""
  return lambda _: x

def first(xs):
  """Grab the first item from a list-like thing."""
  return xs[0]

def second(xs):
  """Grab the second item from a list-like thing."""
  return xs[1]

def third(xs):
  """Grab the third item from a list-like thing."""
  return xs[2]

def end_of_input(parse_state):
  """Match the end of text, return a value of None."""
  if len(parse_state.text) == parse_state.pos:
    return Parsing(None, parse_state)
  return None

def digits(parse_state):
  """Parse digits."""
  pos = parse_state.pos
  while pos < len(parse_state.text) and str.isdigit(parse_state.text[pos]):
    pos += 1
  if pos != parse_state.pos:
    return Parsing(parse_state.text[parse_state.pos:pos],
                   ParseState(parse_state.text, pos))
  else:
    return None

def whole(parser):
  def fn(parse_state):
    parsing = parser(parse_state)
    if parsing:
      if end_of_input(parsing.parse_state):
        return parsing
    return None
  return fn

def option(parser, otherwise=None):
  """Create a parser that succeeds even when the given parser does not.

  If nothing was parsed, then the value that was parsed is |otherwise|.
  """
  def fn(parse_state):
    """Parse with parser, return value of None if parser fails."""
    parsing = parser(parse_state)
    if parsing:
      return parsing
    else:
      return Parsing(otherwise, parse_state)
  return fn

def whitespace(parse_state):
  """Parse 1+ whitespaces, value is just a single space."""
  pos = parse_state.pos
  while pos < len(parse_state.text) and str.isspace(parse_state.text[pos]):
    pos += 1
  if pos != parse_state.pos:
    return Parsing(' ', ParseState(parse_state.text, pos))
  else:
    return None

def skip_space(parser, fail_without_whitespace=True):
  """Creates a new parser that skips the space before the given parse."""
  def fn(parse_state):
    """A function which will skip space before parsing."""
    parsing = whitespace(parse_state)
    if not parsing:
      if fail_without_whitespace:
        return None
    else:
      parse_state = parsing.parse_state
    return parser(parse_state)
  return fn

chomp_space = lambda parser: skip_space(parser, fail_without_whitespace=False)

def char(ch):
  assert len(ch) == 1
  """Return a parser for a specific char."""
  def fn(parse_state):
    """Parse the next character."""
    if parse_state.pos < len(parse_state.text):
      if parse_state.text[parse_state.pos] == ch:
        return Parsing(ch, ParseState(parse_state.text, parse_state.pos+1))
    return None
  return fn

def not_char(ch):
  assert len(ch) == 1
  """Return a parser for anything but a specific char."""
  def fn(parse_state):
    """Parse the next character."""
    if parse_state.pos < len(parse_state.text):
      if parse_state.text[parse_state.pos] != ch:
        return Parsing(parse_state.text[parse_state.pos],
                       ParseState(parse_state.text, parse_state.pos+1))
    return None
  return fn

def take_while(match_char_fn):
  def fn(parse_state):
    """Parse text while match_char_fn returns True."""
    len_input = len(parse_state.text)
    pos = parse_state.pos
    while pos < len_input and match_char_fn(parse_state.text[pos]):
      pos += 1
    if pos != parse_state.pos:
      return Parsing(parse_state.text[parse_state.pos:pos],
                     ParseState(parse_state.text, pos))
    return None
  return fn

def until(match_char_fn):
  """Return a parser that matches until the given predicate matches."""
  return take_while(lambda x: not match_char_fn(x))

def string(s):
  """Return a parser for a specific string."""
  return lambda parse_state: parse_string(parse_state, s)

def lift(fn, parser):
  """Like fmap for a parser."""
  def lifted_parser(parse_state):
    """Lift this parser to pass its successful output through."""
    parsing = parser(parse_state)
    if parsing:
      return Parsing(fn(parsing.value), parsing.parse_state)
    return None
  return lifted_parser

def many(parser, sep_by=None):
  """Kleene star."""
  if isinstance(sep_by, str):
    parse_separator = string(sep_by)
  else:
    parse_separator = sep_by

  def fn(parse_state):
    """Parsers with parser 0+ times."""
    results = []
    prior_parse_state = parse_state
    while True:
      parsing = parser(parse_state)
      if parsing:
        parse_state = parsing.parse_state
        results.append(parsing.value)
        if parse_separator:
          # Handle  string
          parsing = parse_separator(parse_state)
          if not parsing:
            break
          else:
            prior_parse_state = parse_state
            parse_state = parsing.parse_state
        else:
          prior_parse_state = parse_state
      else:
        return Parsing(results, prior_parse_state)
    return Parsing(results, parse_state)
  return fn

def many1(parser, sep_by=None):
  """Kleene plus."""
  parser = many(parser, sep_by=sep_by)
  def fn(parse_state):
    parsing = parser(parse_state)
    if parsing and parsing.value:
      return parsing
    return None
  return fn

def any_of(parsers):
  """Return a parser that will succeed for any of the given parsers.

  Note that parsing attempts are still ordered. So, if multiple parsers could
  succeed, the first to succeed still wins.
  """
  def fn(parse_state):
    """Parse one of a set of given parsers."""
    for parser in parsers:
      parsing = parser(parse_state)
      if parsing:
        assert parsing.parse_state.pos > parse_state.pos
        return parsing
    return None
  return fn

def sequence(parsers):
  """Return a parser for the given sequence."""
  def fn(parse_state):
    """Parse a sequence of parsers. Must succeed with all."""
    results = []
    for parser in parsers:
      parsing = parser(parse_state)
      if not parsing:
        return None
      results.append(parsing.value)
      parse_state = parsing.parse_state
    return Parsing(results, parsing.parse_state)
  return fn

def strings(*args):
  """Return a parser that passes for the given string options."""
  def fn(parse_state):
    """Parse the closed-over |args| as strings."""
    for arg in args:
      parsing = parse_string(parse_state, arg)
      if parsing:
        return parsing
    return None
  return fn

parse_until_colon_or_whitespace = until(lambda ch: ch == ':' or str.isspace(ch))
