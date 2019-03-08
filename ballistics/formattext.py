#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright David Manthey
#
# Licensed under the Apache License, Version 2.0 ( the "License" ); you may
# not use this file except in compliance with the License.  You may obtain a
# copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.   See the
# License for the specific language governing permissions and limitations
# under the License.

"""
Text formatting functions.
"""


def line_break(text, line_len=79, indent=1):
    """
    Split some text into an array of lines.

    Enter: text: the text to split.
           line_len: the maximum length of a line.
           indent: how much to indent all but the first line.
    Exit:  lines: an array of lines.
    """
    lines = [text.rstrip()]
    while len(lines[-1]) > line_len:
        pos = lines[-1].rfind(' ', 0, line_len)
        if pos < 0:
            pos = line_len
        lines[-1:] = [lines[-1][:pos].rstrip(), ' '*indent+lines[-1][
            pos:].strip()]
    return lines
