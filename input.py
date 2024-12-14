# -----------------------------------------------------------------------------
# Copyright (c) by Anton Ivanov.
# This information is the confidential and proprietary property of Anton Ivanov
# and the possession or use of this file requires a written license from him.
# -----------------------------------------------------------------------------

from commands import Commands
from display import Display

class Input:
    """
    Get input from the terminal and/or other connected input devices and decode it
    """

    def get_cmd(timeout=None):
        cmd = None
        while not cmd:
            try:
                with Display.term.cbreak():
                    cmd = Input.__decode_inkey(Display.term.inkey(timeout=timeout))
            except Exception as e: # Any exception just quit
                return 'quit'
            except: # Everything else that is bad, including CTRL-C (KeyboardInterrupt), just quit
                return 'quit'
        return cmd

    def __decode_inkey(keystroke):
        if keystroke == '':
            return 'timeout'
        cmd_name = keystroke.name if keystroke.is_sequence else keystroke
        matching_cmds = [k for k in Commands.CMDS.keys() if cmd_name in Commands.CMDS[k]['keys']]
        cmd = next(iter(matching_cmds), None)
        cmd = cmd_name if cmd=='#' else cmd
        return cmd
