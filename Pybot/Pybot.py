"""
########################################################################################################################
# Pybot class can be used as Jython source to be used in sikuli IDE, not pure python or python3
# Initialize the script by importing the required libraries for test (a.k.a unittest), subprocess and system to using
# Windows commands
# Lackey package provide a wrapper arround Sikuli
# Source description
# -> !!! Coding style is CamelCase for classes and lowercase_separated_by_underscores for methods and variables !!! <-
########################################################################################################################
"""
import re
# Import unittest in case of test automation
import unittest
# To start program of command
from os import system
from subprocess import check_output

# Lackey library, a sikuli wrapper
from lackey import *

__author__ = "Christophe Brun"
__credits__ = ["Christophe Brun", "PapIT"]
__license__ = "No license"
__version__ = "1.0.0"
__maintainer__ = "Christophe Brun"
__email__ = "christophe.brun@papit.fr"
__status__ = "Development"

"""
########################################################################################################################
# Custom class to be used in as an abstraction layer to sikuli methods and corresponding exception
# Can used command to start/stop program or use commands, access Android mirroring
# Interpretation of GUI, access to windows system commands
########################################################################################################################
"""


class PybotException(Exception):
    """Automation exception"""
    pass


class Pybot:
    """
    Something to automate on a computer a task, a test, etc"
    """

    def __init__(self):
        """
        Constructor of the Pybot class
        """
        if platform.system() != "Windows":
            raise PybotException("Pybot class only for Windows platform at the moment")
        self.python_version = sys.version
        self.OS_type = platform.system()
        self.OS_version = platform.platform()
        self.machine = platform.machine()
        self.uname = platform.uname()

    def __repr__(self):
        """
        Description of the Pybot object
        """
        return "{0} automaton executed on a {1} computer".format(self.python_version, self.OS_version)

    def check_click(self, img, sleep_sec=0, after_click=None):
        """
        Method checking if button exist and clicking on it, return True is clicked False on contrary. Eventually sleep
        sleep_sec seconds after

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
        Method that wait for a button to appear and click on it. Eventually sleep sleep_sec seconds after

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

        Examples:
            test_automaton = Pybot()
            test_automaton.type_n_time(5, Key.11)
        """
        if isinstance(n, (int, float)):
            i = 0
            while (i < n):
                type(key)
                self._check_n_sleep(sleep_sec)
                i += 1
        else:
            raise PybotException("n is the number of time to type the key, therefore must be an int or float")

    def exec_cmd(self, cmd, sleep_sec=0):
        """
        Execute command on Windows OS

        Args:
            cmd: Command to execute passed a string

        Kwargs:
            sleep_sec: Number of seconds to eventually sleep after the click

        Returns:
            True if return code of the command is 0, false on contrary

        Examples:
            test_automaton = Pybot()
            test_automaton.exec_cmd("DIR")
        """
        rt = system("{0}".format(cmd))
        self._check_n_sleep(sleep_sec)
        return rt == 0

    def start_android_gui(self, sleep_sec=0):
        """
        Start Android mirroring with scrcpy.exe if connected

        Kwargs:
            sleep_sec: Number of seconds to eventually sleep after the click

        Returns:
             Boolean True if started, False on contrary
        """
        if self.android_number() == 1:
            return self.start_pgm("scrcpy.exe", wd="scrcpy-windows-v1.1", sleep_sec=sleep_sec)
        else:
            return False

    def check_android_gui(self):
        """
        Check that Android mirroring with scrcpy.exe is running

        Returns:
             Boolean True if mirroring, False on contrary
        """
        return self.check_pgm("scrcpy.exe")

    def stop_android_gui(self):
        """
        Stop scrcpy.exe processes

        Returns:
            Boolean True if command executed correctly, False on contrary
        """
        return self.kill_pgm("scrcpy.exe")

    def android(self):
        """
        Access connected Android device via adb.exe

        Returns:
            Tuple containing the Android Serial number and device type
        """
        adb_output = check_output(["scrcpy-windows-v1.1/adb.exe", "devices"]).decode()
        tup = re.findall("\n([\w]*)\t([\w]*)\r", adb_output)
        android_arr = []
        if tup is not None:
            l = len(tup)
            i = 0
            while i < l:
                android_arr.append({"type": tup[i][1], "num": tup[i][0]})
                i += 1
        return android_arr

    def android_connected(self):
        """
        Check if an Android is connected

        Returns:
            True if command Android connected, False on contrary
        """
        return len(self.android()) != 0

    def android_number(self):
        """
        Calculate the number of Android device connected

        Returns:
            int corresponding to the number of Android device
        """
        return len(self.android())

    def start_pgm(self, pgm, wd=None, pgm_arg=None, sleep_sec=0):
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

        Examples:
            test_automaton = Pybot()
            test_automaton.start_pgm('node.exe', wd='server', sleep_sec=5)
        """
        if wd is None:
            prefix = ""
        else:
            prefix = "cd {0} && ".format(wd)

        if pgm_arg is None:
            suffix = ""
        else:
            suffix = " {0}".format(pgm_arg)

        cmd = "{0}START /B {1}{2}".format(prefix, pgm, suffix)
        rt = self.exec_cmd(cmd)
        self._check_n_sleep(sleep_sec)
        return rt

    def check_pgm(self, pgm):
        """
        Check if a program is running

        Args:
            pgm: Program to check, with the .exe extension

        Returns:
            True if program running, false on contrary

        Examples:
            test_automaton = Pybot()
            test_automaton.check_pgm("Firefox.exe")
        """
        cmd = 'tasklist /nh /fi "imagename eq {0}" | find /i "{0}" > nul'.format(pgm)
        return self.exec_cmd(cmd, sleep_sec=0)

    def kill_pgm(self, pgm, sleep_sec=0):
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
        rt = self.exec_cmd(cmd, sleep_sec=0)
        self._check_n_sleep(sleep_sec)
        return rt

    def _check_n_sleep(self, s):
        """
        Internal method to check s, the number of second to sleep which as to be int or float

        Args:
            s: Number of seconds
        """
        if isinstance(s, (int, float)):
            sleep(s)
        else:
            raise PybotException("sleep_sec KWARG is a time in to sleep after click, therefore must be an int or float")

    def start_web(self, url, sleep_sec=0):
        """
        Start a website on the default browser and full screen it on Windows OS

        Args:
            url: URL of the website

        Kwargs:
            sleep_sec: Number of seconds of seconds to eventually sleep after the click

        Returns:
            True if return code of the command is 0, false on contrary

        Examples:
            test_automaton = Pybot()
            test_automaton.start_web("https://papit.fr")
        """
        cmd = "START {0}".format(url)
        rt = self.exec_cmd(cmd)
        self._check_n_sleep(sleep_sec)
        type(Key.F11)
        return rt


"""
########################################################################################################################
# PybotTest as unittest.Testcase to test the development of the Pybot class
# test_B_Pybot_init: Test the initialization of the Pybot object
# test_C_pgm: Test of the methods related to program management
# test_D_android: Test of the methods related to Android connection and mirroring
# test_E_web: Test the opening of a website in the default browser
########################################################################################################################
"""


class PybotTest(unittest.TestCase):
    """PybotTest as unittest.Testcase to test the development of the Pybot class"""
    def setUp(self):
        """Executed before each test, nothing to do yet"""
        pass

    def tearDown(self):
        """Executed after each test, nothing to do yet"""
        pass

    @unittest.skip("Initialization of the test not necessary")
    def test_A_(self):
        """Nothing to do yet"""
        pass

    def test_B_Pybot_init(self):
        """Test the init of Pybot class"""
        test_automaton = Pybot()
        assert test_automaton != ""
        assert test_automaton.python_version != ""
        assert test_automaton.OS_type != ""
        assert test_automaton.OS_version != ""
        assert test_automaton.machine != ""
        assert test_automaton.uname != ""

    def test_C_pgm(self):
        """Test the method wrapping cmd.exe"""
        test_automaton = Pybot()
        assert test_automaton.start_pgm('node.exe', sleep_sec=5) is True
        assert test_automaton.check_pgm('node.exe') is True
        assert test_automaton.kill_pgm('node.exe') is True

    def test_D_android(self):
        """Test the method necessary to automate Android task"""
        test_automaton = Pybot()
        assert test_automaton.start_android_gui(sleep_sec=6) == True
        assert test_automaton.check_android_gui() == True
        assert test_automaton.stop_android_gui() == True
        assert test_automaton.android_connected() == True
        assert test_automaton.android_number() == 1

    def test_E_web(self):
        """Test the opening of a website in the default browser"""
        test_automaton = Pybot()
        test_automaton.start_web("https://papit.fr",sleep_sec=5)
        assert test_automaton.kill_pgm('Firefox.exe') is True


"""
########################################################################################################################
# Start the tests of the Pybot class
########################################################################################################################
"""
if __name__ == '__main__':
    unittest.main()
