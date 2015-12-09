from __future__ import unicode_literals

import os
import subprocess
import sys

from pre_commit import color
from pre_commit import five


# TODO: smell: import side-effects
try:
    if not os.environ.get('TERM'):  # pragma: no cover (dumb terminal)
        raise OSError('Cannot determine width without TERM')
    else:  # pragma no cover (windows)
        COLS = int(
            subprocess.Popen(
                ('tput', 'cols'), stdout=subprocess.PIPE,
            ).communicate()[0] or
            # Default in the case of no terminal
            80
        )
except OSError:  # pragma: no cover (windows)
    COLS = 80


def get_hook_message(
        start,
        postfix='',
        end_msg=None,
        end_len=0,
        end_color=None,
        use_color=None,
        cols=COLS,
):
    """Prints a message for running a hook.

    This currently supports three approaches:

    # Print `start` followed by dots, leaving 6 characters at the end
    >>> print_hook_message('start', end_len=6)
    start...............................................................

    # Print `start` followed by dots with the end message colored if coloring
    # is specified and a newline afterwards
    >>> print_hook_message(
        'start',
        end_msg='end',
        end_color=color.RED,
        use_color=True,
    )
    start...................................................................end

    # Print `start` followed by dots, followed by the `postfix` message
    # uncolored, followed by the `end_msg` colored if specified and a newline
    # afterwards
    >>> print_hook_message(
        'start',
        postfix='postfix ',
        end_msg='end',
        end_color=color.RED,
        use_color=True,
    )
    start...........................................................postfix end
    """
    if bool(end_msg) == bool(end_len):
        raise ValueError('Expected one of (`end_msg`, `end_len`)')
    if end_msg is not None and (end_color is None or use_color is None):
        raise ValueError(
            '`end_color` and `use_color` are required with `end_msg`'
        )

    if end_len:
        return start + '.' * (cols - len(start) - end_len - 1)
    else:
        return '{0}{1}{2}{3}\n'.format(
            start,
            '.' * (cols - len(start) - len(postfix) - len(end_msg) - 1),
            postfix,
            color.format_color(end_msg, end_color, use_color),
        )


stdout_byte_stream = getattr(sys.stdout, 'buffer', sys.stdout)


def sys_stdout_write_wrapper(s, stream=stdout_byte_stream):
    stream.write(five.to_bytes(s))