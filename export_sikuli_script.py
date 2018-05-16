"""
Script exporting sikuli script to the script library ./script
"""

import sys

from Pybot.Pybot import Pybot

test_automaton = Pybot()
test_automaton.export_sikuli_script(sys.argv[1])
sys.exit(0)
