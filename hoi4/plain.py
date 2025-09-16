"""Functions for parsing plain text .hoi4 files."""

import re
from itertools import chain

# A robust regex that correctly finds:
# 1. Quoted strings (and preserves the quotes)
# 2. Braces and equals signs as single tokens
# 3. Any other sequence of non-whitespace characters
TOKEN_REGEX = re.compile(r'"(?:\\.|[^"\\])*"|[{}=]|\S+')

def filestring_to_dict(filestring):
    """
    Takes a plain text HOI4 filestring and creates a Python dictionary
    representation of it.
    """
    # The strip_down function is no longer needed as the new tokenizer is more powerful.
    tokens = TOKEN_REGEX.findall(filestring)

    # Create an iterator for efficient token consumption
    token_iterator = iter(tokens)

    # Begin parsing
    return parse_token_stream(token_iterator)

def parse_token_stream(token_iterator):
    """
    Parses a stream of tokens from an iterator into a dictionary or list.
    This acts as the main recursive descent parser.
    """
    # Peek at the first token to decide if we are in list or dict mode
    try:
        first_token = next(token_iterator)
    except StopIteration:
        return {} # Empty block

    # Look ahead one more token to determine structure
    try:
        second_token = next(token_iterator)
    except StopIteration:
        # Block has only one item, can be a list or a dict with a flag
        # e.g. { item } or { flag= } (though the latter is unlikely)
        return [strip_quotes(first_token)]

    # We have at least two tokens, put them back to be processed by the main loop
    token_iterator = chain([first_token, second_token], token_iterator)

    # A block is a list if the second token is NOT an equals sign
    is_list_mode = second_token != '='

    if is_list_mode:
        return list(parse_list(token_iterator))
    else:
        return dict(parse_dict(token_iterator))

def parse_list(token_iterator):
    """Parses tokens as a list of values."""
    for token in token_iterator:
        if token == '{':
            yield parse_token_stream(token_iterator)
        elif token == '}':
            return
        else:
            yield strip_quotes(token)

def parse_dict(token_iterator):
    """Parses tokens as key-value pairs."""
    while True:
        try:
            key_token = next(token_iterator)
            if key_token == '}':
                return

            equals_token = next(token_iterator)
            if equals_token != '=':
                # Handle boolean flags (key with no value)
                yield (strip_quotes(key_token), True)
                if equals_token == '}': # The flag was the last item
                    return
                # The token we thought was '=' is actually the next key
                key_token = equals_token
                equals_token = next(token_iterator)


            value_token = next(token_iterator)

            key = strip_quotes(key_token)

            if value_token == '{':
                yield key, parse_token_stream(token_iterator)
            else:
                yield key, strip_quotes(value_token)

        except StopIteration:
            return

def strip_quotes(token):
    """Removes quotes from the start and end of a token if they exist."""
    if token.startswith('"') and token.endswith('"'):
        return token[1:-1]
    return token