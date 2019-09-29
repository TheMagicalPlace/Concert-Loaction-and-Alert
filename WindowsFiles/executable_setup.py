import sys
import cx_Freeze

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

cx_Freeze.setup(  name = "ConcertLocator",
        version = "0.1",
        description = "null!",
        options = {"build_exe": build_exe_options},
        executables = [cx_Freeze.Executable("main.py", base=base)])