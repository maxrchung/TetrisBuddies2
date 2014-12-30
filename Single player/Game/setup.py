from cx_Freeze import setup, Executable



setup(name = 'TetrisBuddy', 
      version='3.1.4', 
      description='Single-player Tetris',
      executables = [Executable(script = 'TetrisBuddy.py', base='Win32GUI')])
