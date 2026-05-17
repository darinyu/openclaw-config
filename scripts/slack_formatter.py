#!/usr/bin/env python3
"""
Slack Formatter — global italic-to-bold enforcement.

Reads text from stdin or a file, and converts ALL italic to bold:
  - *single asterisk italic*   -> **bold**
  - _underscore italic_        -> **bold**

Preserves:
  - Already-bold **text**
  - Inline code spans (`...`)
  - Fenced code blocks (```...```)

Usage:
  echo "some *italic* text" | python3 slack_formatter.py
  python3 slack_formatter.py < input.txt
  python3 slack_formatter.py --file /tmp/slack_msg.txt > output.txt
"""

import re
import sys
import argparse


def convert_italic_to_bold(text: str) -> str:
    """
    Convert *italic* and _italic_ to **bold** in non-code text.
    Preserves triple-backtick code blocks and inline `code spans`.
    """

    def _replace_in_code_free(segment: str) -> str:
        if not segment:
            return segment

        # *single asterisk italic* -> **bold**
        # Negative lookbehind/ahead prevent matching **already bold**
        segment = re.sub(
            r'(?<!\*)\*(?!\*)([^*\*]+?)(?<!\*)\*(?!\*)',
            r'**\1**',
            segment,
        )

        # _underscore italic_ -> **bold**
        # Negative lookbehind/ahead prevent matching __already bold__
        segment = re.sub(
            r'(?<!_)_(?!_)([^_]+?)(?<!_)_(?!_)',
            r'**\1**',
            segment,
        )

        return segment

    result = []
    pos = 0

    while pos < len(text):
        # Check for fenced code block: ```...```
        if text.startswith('```', pos):
            end = text.find('```', pos + 3)
            if end == -1:
                # Unclosed code block — treat rest as code
                result.append(text[pos:])
                break
            result.append(text[pos:end + 3])
            pos = end + 3
            continue

        # Check for inline code span: `...`
        if text[pos] == '`':
            end = pos + 1
            while end < len(text) and text[end] != '`':
                # Skip escaped backticks
                if text[end] == '\\' and end + 1 < len(text) and text[end + 1] == '`':
                    end += 2
                else:
                    end += 1
            if end < len(text):
                end += 1  # include closing backtick
                result.append(text[pos:end])
                pos = end
                continue
            else:
                # Unclosed backtick — treat rest as code
                result.append(text[pos:])
                break

        # Regular character — find next code boundary
        next_code_start = len(text)
        fenced = text.find('```', pos)
        inline = text.find('`', pos)
        if fenced != -1 and fenced < next_code_start:
            next_code_start = fenced
        if inline != -1 and inline < next_code_start:
            # Only if it's not part of a fenced block already found
            if text[inline:inline + 3] != '```':
                next_code_start = inline

        chunk = text[pos:next_code_start]
        result.append(_replace_in_code_free(chunk))
        pos = next_code_start

    return ''.join(result)


def main():
    parser = argparse.ArgumentParser(
        description='Convert italic to bold in Slack-formatted text.',
    )
    parser.add_argument(
        '--file', '-f',
        help='Read from FILE instead of stdin.',
    )
    args = parser.parse_args()

    if args.file:
        with open(args.file, 'r') as f:
            text = f.read()
    else:
        text = sys.stdin.read()

    converted = convert_italic_to_bold(text)
    sys.stdout.write(converted)


if __name__ == '__main__':
    main()
