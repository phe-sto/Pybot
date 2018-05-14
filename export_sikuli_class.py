"""
Script exporting sikuli class to the Pybot package
"""

import sys

from Pybot.Pybot import Pybot

test_automaton = Pybot()
test_automaton.export_sikuli_class(sys.argv[1])
sys.exit(0)
