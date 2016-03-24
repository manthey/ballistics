#!/usr/bin/python
"""
Text formatting functions.
"""


def line_break(text, line_len=79, indent=1):
    """Split some text into an array of lines.
    Enter: text: the text to split.
           line_len: the maximum length of a line.
           indent: hoe much to indent all but the first line.
    Exit:  lines: an array of lines."""
    lines = [text.rstrip()]
    while len(lines[-1]) > line_len:
        pos = lines[-1].rfind(' ', 0, line_len)
        if pos < 0:
            pos = line_len
        lines[-1:] = [lines[-1][:pos].rstrip(), ' '*indent+lines[-1][
            pos:].strip()]
    return lines
