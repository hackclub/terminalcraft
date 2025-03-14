#!/usr/bin/env python3

"""
ZSH history convert script.

When you mistakenly type your password or quite bad command into ZSH,
you may want to remove the entry from the history.
The problem is, the .zsh_history is encoded in a weird format!
If you want to find a command with non-ASCII character, it'll be problematic.

Here is the small script to convert between .zsh_history and valid UTF-8 file.
You can follow the steps shown below to manipulate your .zsh_history.

$ python3 zshhist.py export > /tmp/exported
$ rm ~/.zsh_history
$ mv /tmp/exported ~/.zsh_history

Referring: http://www.zsh.org/mla/users/2011/msg00155.html

MIT License

Copyright (c) 2012-2023 Katsuaki Ikegami

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import os
import sys
from argparse import ArgumentParser, FileType as OriginalFileType


DEFAULT_ZSH_HIST_FILE = "/path/no/exists" # os.path.join(os.environ["HOME"], ".zsh_history")


class FileType(OriginalFileType):

    """Bug-fix to original argparse FileType factory.

    This Factory returns buffer IO wrapper when binary mode is set.
    """

    def __init__(self, *args, **kwargs):
        super(FileType, self).__init__(*args, **kwargs)

    def __call__(self, string):
        if string == '-' and 'b' in self._mode:
            if 'r' in self._mode: return sys.stdin.buffer
            if 'w' in self._mode: return sys.stdout.buffer
        return super(FileType, self).__call__(string)

def mapNotNone(function, iterable):
    return filter(lambda x: x is not None, map(function, iterable))


def ismeta(ch):
    return ((ch > 0x83 and ch < 0x9e)
            or ch == 0xa0 or ch == 0x83 or ch == 0)


def readhist(bs):
    change = False
    result = bytearray()
    for c in bs:
        if c != 0x83:
            if change:
                d = c ^ 32;
            else:
                d = c
            result.append(d)
            change = False
        else:
            change = True
    return bytes(result)


def writehist(bs):
    result = bytearray()
    for c in bs:
        if ismeta(c):
            d = 0x83
            result.append(d)
            d = c ^ 32
            result.append(d)
        else:
            result.append(c)
    return bytes(result)


class InvalidFormatError(Exception):
    def __init__(self, index, byte):
        self.index = index
        self.byte  = byte

    def __str__(self):
        return "InvalidFormatError(line={0.index}, byte={0.byte})".format(self)


def byte2u(index, bs, strict):
    try:
        return bs.decode("utf-8")
    except UnicodeDecodeError:
        if strict:
            raise InvalidFormatError(index, bs)
        else:
            return None


def handle_export(args):
    """Export ZSH history into valid UTF-8, emit to stdout.

    Parameters:
        args: object with following properties.
              * source (Reader): input ZSH history file.
              * strict (bool): True to make behavior strict.
    """

    def f(arg):
        i, x = arg
        return byte2u(i, readhist(x), args.strict)

    try:
        hists = mapNotNone(f, enumerate(args.source.readlines()))
    except InvalidFormatError as e:
        print("Invalid characters @ line {0}".format(e.index+1),
              file=stderr)
        exit(2)
    sys.stdout.write("".join(hists))


def handle_import(args):
    sys.stdout.buffer.write(writehist(args.source.read()))


def handle_unknown(parser, args):
    parser.print_help(sys.stderr)
    sys.exit(2)


def main():
    parser = ArgumentParser(description="zsh history UTF-8 converter")
    parser.set_defaults(func=lambda args: handle_unknown(parser, args))

    subparsers = parser.add_subparsers()

    parser_read = subparsers.add_parser("export",
                                        help="export zsh history file to UTF-8 text, emit to standard output.")
    parser_read.add_argument('--strict', action='store_true', default=False,
                             help="strict mode (default: no)")
    parser_read.add_argument('source', nargs='?', type=FileType("rb"),
                             default=DEFAULT_ZSH_HIST_FILE,
                             help="target file (default: $HOME/.zsh_history)")
    parser_read.set_defaults(func=handle_export)

    parser_write = subparsers.add_parser("import",
                                         help="import UTF-8 text into zsh history format, emit to standard output.")
    parser_write.add_argument('source', nargs='?', type=FileType("rb", 0),
                              default=sys.stdin.buffer,
                              help="target file (default: stdin)")
    parser_write.set_defaults(func=handle_import)

    args = parser.parse_args()
    args.func(args)

    return 0

if __name__ == "__main__":
    main()
