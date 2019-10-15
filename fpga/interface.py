"""
This module handles communication of data to the FPGA once it has already been flashed.
"""

import os
import flash


def put_array(data):
    """Loads input data (in numpy array or other iterable form) onto the FPGA."""
    pass


def flash_from_file(filename): 
    """Given a bitstream stored in a file (*.bit), flashes the FPGA with the file contents."""
    # Call the Makefile containing the compile/flash statements
    os.sys("make prog")

