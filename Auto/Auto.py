"""
###########################################################################################################################################
# Jython source to be used in sikuli, not pure python or python3
# Initialize the script by importing the required libraries for test (a.k.a unittest) and system to using windows commands.
# Source description
# -> !!! Coding style is CamelCase for classes and lowercase_separated_by_underscores for methods and variables !!! <-
###########################################################################################################################################
"""
# Import unittest in case of test automation
import unittest
# To start program of command
from os import system
# Lackey library, a sikuli wrapper
from lackey import *
import platform
import sys

__author__ = "Christophe Brun"
__credits__ = ["Christophe Brun", "PapIT"]
__license__ = "No license"
__version__ = "1.0.0"
__maintainer__ = "Christophe Brun"
__email__ = "christophe.brun@papit.fr"
__status__ = "Developpement"

"""
###########################################################################################################################################
# Custom class to be used in as an abstraction layer to sikuli methods and corresponding exception.
# Can used command to start/stop program or use commands.
# Interpretation of GUI, access to windows sytem commands
###########################################################################################################################################
"""


class AutoException(Exception):
    """Automation problem with exception"""
    pass


class Auto:
    """
    Something to automate on a computer a task, a test, etc"
    """

    def __init__(self):
        """
        Constructor of the Auto class
        """
        if platform.system() != "Windows":
            AutoException("Auto class only ru on windows platform at the moment")
        self.python_version = sys.version
        self.OS_type = platform.system()
        self.OS_version = platform.platform()
        self.machine = platform.machine()
        self.uname = platform.uname()


    def __repr__(self):
        """
        Description of the auto object
        """
        return "{0} automaton executed on a {1} computer".format(self.python_version, self.OS_version)


    def check_click(self, img, sleep_sec=0, after_click=None):
        """
        Method checking if bouton exist and clicking on it, return True is clicked False on contrary. Eventually sleep sleep_sec seconds after

        Args:
            img: Image to check and click

        Kwargs:
            sleep_sec: Number of seconds of seconds to eventually sleep after the click
            after_click: Another image to eventually click after the first click and before the sleep

        Returns:
            True if img was found and clicked, False on contrary
        """
        if exists(img) is None:
            return False
        else:
            click(img)
            if after_click is not None and exists(after_click) is not None:
                click(after_click)
            self._check_n_sleep(sleep_sec)
            return True

    def wait_click(self, img, sleep_sec=0):
        """
        Method that wait for a bouton to appear and click on it. Eventually sleep sleep_sec seconds after

        Args:
            img: Image to wait for and click

        Kwargs:
            sleep_sec: Number of seconds of seconds to eventually sleep after the click
        """
        wait(img)
        click(img)
        self._check_n_sleep(sleep_sec)

    def type_n_time(self, n, key, sleep_sec=0):
        """
        Type n time the desired key. Eventually sleep sleep_sec seconds

        Args:
            n: Number of time to type the key
            key: Key to type

        Kwargs:
            sleep_sec: Number of seconds of seconds to eventually sleep after the click
        """
        if isinstance(n, (int, float)):
            i = 0
            while (i < n):
                type(key)
                self._check_n_sleep(sleep_sec)
                i += 1
        else:
            AutoException("n is the number of time to type the key, therefore must be an int or float")

    def exec_win_cmd(self, cmd, sleep_sec=0):
        """
        Execute command on Windows OS

        Args:
            cmd: Command to execute passed a string

        Kwargs:
            sleep_sec: Number of seconds to eventually sleep after the click

        Returns:
            True if return code of the command is 0, false on contrary
        """
        rt = system("CMD /C {0}".format(cmd))
        self._check_n_sleep(sleep_sec)
        return rt == 0

    def start_win_pgm(self, pgm, wd=None , pgm_arg=None, sleep_sec=0):
        """
        Start a program in background in a given directory on Windows OS

        Args:
            pgm: Program to start
            wd: Working directory to start the program, with the .exe extension

        Kwargs:
            pgm_arg: Eventual argument of the program to start
            sleep_sec: Number of seconds of seconds to eventually sleep after the click

        Returns:
            True if return code of the command is 0, false on contrary
        """
        if wd is None:
            prefix = ""
        else:
            prefix  = "cd {0} && ".format(wd)

        if wd is None:
            suffix = ""
        else:
            suffix  = " {0}".format(pgm_arg)

        cmd = "START /B {1}{2}".format(prefix, pgm, suffix)
        rt = self.exec_win_cmd(cmd)
        self._check_n_sleep(sleep_sec)
        return rt

    def check_win_pgm(self, pgm):
        """
        Check if a program is running

        Args:
            pgm: Program to check, with the .exe extension

        Returns:
            True if program running, false on contrary
        """
        cmd = 'tasklist /nh /fi "imagename eq {0}" | find /i "{0}" > nul'.format(pgm)
        return self.exec_win_cmd(cmd, sleep_sec=0)

    def kill_win_pgm(self, pgm, sleep_sec=0):
        """
        Kill a program

        Args:
            pgm: Program to kill, with the .exe extension

        Kwargs:
            sleep_sec: Number of seconds of seconds to eventually sleep after the click

        Returns:
            True if return code of the command is 0, false on contrary
        """
        cmd = "Taskkill /IM {0} /F".format(pgm)
        rt = self.exec_win_cmd(cmd, sleep_sec=0)
        self._check_n_sleep(sleep_sec)
        return rt


    def _check_n_sleep(self, s):
        """
        Internal method tocheck s, the number of second to sleep which as to be int or float

        Args:
            s: Number of seconds
        """
        if isinstance(s, (int, float)):
            sleep(s)
        else:
            AutoException("sleep_sec KWARG is a time in to sleep after click, therefore must be an int or float")


class AutoTest(unittest.TestCase):
    def setUp(self):
        """Executed before each test, nothing to do yet"""
        pass

    def tearDown(self):
        """Executed after each test, nothing to do yet"""
        pass

    def test_A_Auto_init(self):
        """Test the init of Auto class"""
        test_automaton = Auto()
        assert test_automaton != ""
        assert test_automaton.python_version != ""
        assert test_automaton.OS_type != ""
        assert test_automaton.OS_version != ""
        assert test_automaton.machine != ""
        assert test_automaton.uname != ""

    def test_B_manage_pgm(self):
        """Test the method wrapping cmd.exe"""
        test_automaton = Auto()
        assert test_automaton.start_win_pgm('node.exe', sleep_sec=5) is True
        assert test_automaton.check_win_pgm('node.exe') is True
        assert test_automaton.kill_win_pgm('node.exe') is True


########################################################################################################################################
# Start test, and produce the XML and print the errors
###########################################################################################################################################
if __name__ == '__main__':
    unittest.main()
