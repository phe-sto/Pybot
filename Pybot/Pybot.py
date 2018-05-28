"""
Pybot class can be used as Jython source to be used in sikuli IDE, not pure python or python3
Initialize the script by importing the required libraries for test (a.k.a unittest), subprocess and system to using
Windows commands
Lackey package provide a wrapper arround Sikuli
Source description
-> !!! Coding style is CamelCase for classes and lowercase_separated_by_underscores for methods and variables !!! <-
"""
import locale
import re
import sqlite3
# Import unittest in case of test automation
import unittest
from datetime import datetime
# To start program of command
from os import system, path, makedirs, remove
from shutil import copy, rmtree, move
from subprocess import check_output

import easygui
import pytesseract
from PIL import Image
from lackey import *

__author__ = "Christophe Brun"
__credits__ = ["Christophe Brun", "PapIT"]
__license__ = "No license"
__version__ = "1.0.0"
__maintainer__ = "Christophe Brun"
__email__ = "christophe.brun@papit.fr"
__status__ = "Development"

"""
Custom class to be used in as an abstraction layer to sikuli methods and corresponding exception
Can used command to start/stop program or use commands, access Android mirroring
Interpretation of GUI, access to windows system commands
"""

IMG_FOLDER = "img/"
IMAGE_EXT = ".png"
SQLITE3_EXT = "sqlite3"
SQLITE3_DATABASE = "pybot.sqlite3"
SCRCPY_FOLDER = "scrcpy-windows-v1.1"
SCRCPY_EXE = "scrcpy.exe"
TESSERACT_CMD = "tesseract"
# TODO all the tesseract languages available
TESSERACT_LANG = {
    "fr": "fra",
    "en": "eng",
    "ar": "ara",
    "ja": "jpn",
    "es": "spa",
    "de": "deu",
    "ru": "rus",
}


class PybotException(Exception):
    """Automation exception"""
    pass


class Pybot:
    """
    Something to automate on a computer a task, a test, etc"
    """

    def __init__(self, cache=True):
        """
        Constructor of the Pybot class

        Kwargs:
            cache: Call a caching method if True, which is the default value
        """
        if platform.system() != "Windows":
            raise PybotException(
                "Pybot class only for Windows platform at the moment")
        self.python_version = sys.version
        self.OS_type = platform.system()
        self.OS_version = platform.platform()
        self.machine = platform.machine()
        self.uname = platform.uname()
        self.computer = platform.node()
        self.screen = Screen()
        self.screen_width = self.screen.getBounds()[2]
        self.screen_height = self.screen.getBounds()[3]
        self.screen_bounds = self.screen.getBounds()
        self.num_screen = self.screen.getNumberScreens()
        self.database_directory = SQLITE3_EXT
        self.database = SQLITE3_DATABASE
        self.cache = cache
        self._cache_automaton_screen()
        self.locale_lang = locale.getdefaultlocale()[0]
        self.tesseract_lang = TESSERACT_LANG[self.locale_lang[0:2]]
        # init tesseract command
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

    def __repr__(self):
        """
        Description of the Pybot object
        """
        return "{0} automaton executed on {1}, a {2} computer".format(
            self.python_version, self.computer, self.OS_version)

    def purge_cache(self):
        """
        Deleting database

        Returns:
            True if cache is clear, False on contrary
        """
        rmtree(self.database_directory)
        return path.isdir(self.database_directory) is False

    def text(self, bounds=None, lang=None):
        """
        Retrievge the text on the screen, default is all the screen

        Kwargs:
            bounds: The bounds of the image to take, default is None, to get the all screen
            lang: Specify a lang for the image text

        Returns:
            The string decrypted from the screen

        Examples:
            test_automaton = Pybot()
            test_automaton.text(lang='eng') # get text of the full screen with english text description
        """
        text = screenshot(self, bounds=bounds, text=True, lang=lang)
        remove(path.join(IMG_FOLDER + text[1]))
        return text

    def screenshot(self, bounds=None, text=False, lang=None):
        """
        Taking a screenshot, default is all the screen

        Kwargs:
            bounds: The bounds of the image to take, default is None, to get the all screen
            text: Boolean True to discover text False on contrary
            lang: Specify a lang for the image text

        Returns:
            A tuple made of the boolean integer, image file and thetext discovered in the image

        Examples:
            test_automaton = Pybot()
            test_automaton.screenshot(lang='eng') # Screenshot of the full screen with english text description
        """
        if bounds is None:
            b = self.screen_bounds
        else:
            if isinstance(bounds, tuple) and len(bounds) == 4 * self.num_screen:
                b = bounds
            else:
                raise PybotException(
                    "Bound arg has to be a tuple with length of 4 multiply by the number of screen(s)")
        data = self.screen.capture(b)
        img_file = str(datetime.now().timestamp()).replace('.', '')
        img_file = "".join([img_file[2:15], IMAGE_EXT])
        img = Image.fromarray(data)
        img.save(img_file)
        move(img_file, IMG_FOLDER)
        del img
        if text is True:
            text_string = self.get_text_img(img_file, lang=lang)
        else:
            text_string = ''
        self._cache_screenshot(img_file, text=text_string)
        return int(path.isfile(path.join(IMG_FOLDER + img_file))), img_file, text_string

    def get_text_img(self, img_file, lang=None):
        """
        Retrieve text from an image

        Args:
            img_file: Name of the image file

        Kwargs:
            lang: None is default, those specify a language to tesseract

        Returns:
            String of the text decrypted

        Examples:
            test_automaton = Pybot()
            test_automaton.screenshot("1234567891012.png",lang='eng') # Retrieve text from 1234567891012.png with english text description
        """
        img = Image.open(path.join(IMG_FOLDER + img_file))
        if lang is None:
            text = pytesseract.pytesseract.image_to_string(img)
        else:
            text = pytesseract.pytesseract.image_to_string(img, lang=lang)
        return text

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

        Raises:
            PybotException

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
            raise PybotException(
                "n is the number of time to type the key, therefore must be an int or float")

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

    def start_android_gui(self, sleep_sec=5, fullscreen=True):
        """
        Start Android mirroring with SCRCPY_EXE if connected and full screen it

        Kwargs:
            sleep_sec: Number of seconds to eventually sleep after the click

        Returns:
             Boolean True if started, False on contrary
        """
        if self.android_number() == 1:
            rc = self.start_pgm(
                SCRCPY_EXE, wd=SCRCPY_FOLDER, sleep_sec=sleep_sec)
        else:
            rc = False
        if fullscreen is True:
            self.android_fullscreen()
        return rc

    def android_fullscreen(self):
        """
        Type the scrcpy shortcut to full screen f + CTRL
        """
        self.ctrl_shorcut('f')

    def android_resize_one_to_one(self):
        """
        resize window to 1:1 (pixel-perfect)
        """
        self.ctrl_shorcut('g')

    def android_remove_black_borders(self):
        """resize window to remove black borders"""
        self.ctrl_shorcut('x')

    def android_home(self):
        """click on HOME"""
        self.ctrl_shorcut('h')

    def android_back(self):
        """click on BACK"""
        self.ctrl_shorcut('b')

    def android_app_switch(self):
        """click on APP_SWITCH"""
        self.ctrl_shorcut('m')

    def android_volume_up(self):
        """click on VOLUME_UP"""
        self.ctrl_shorcut('+')

    def android_volume_down(self):
        """click on VOLUME_DOWN"""
        self.ctrl_shorcut('-')

    def turn_screen_on(self):
        """turn screen on"""
        rightClick()

    def android_power(self):
        """click on POWER"""
        self.ctrl_shorcut('p')

    def android_toggle_FPS_counter(self):
        """paste computer clipboard to device"""
        self.ctrl_shorcut('v')

    def android_toggle_FPS_counter(self):
        """enable/disable FPS counter (on stdout)"""
        self.ctrl_shorcut('i')

    def ctrl_shorcut(self, key):
        """
        Type a key with the key modifier CTRL

        Args:
            key: The key to type with the CTRL modifier
        """
        type(key, Key.CTRL)

    def check_android_gui(self):
        """
        Check that Android mirroring with SCRCPY_EXE is running

        Returns:
             Boolean True if mirroring, False on contrary
        """
        return self.check_pgm(SCRCPY_EXE)

    def stop_android_gui(self):
        """
        Stop SCRCPY_EXE processes

        Returns:
            Boolean True if command executed correctly, False on contrary
        """
        return self.kill_pgm(SCRCPY_EXE)

    def android(self):
        """
        Access connected Android device via adb.exe

        Returns:
            Tuple containing the Android Serial number and device type
        """
        adb_output = check_output(
            [path.join(SCRCPY_FOLDER, "adb.exe"), "devices"]).decode()
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

        Kwargs:
            wd: Working directory to start the program, with the .exe extension
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
        cmd = 'tasklist /nh /fi "imagename eq {0}" | find /i "{0}" > nul'.format(
            pgm)
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

    def start_web(self, url, sleep_sec=0):
        """
        Start a website on the default browser, wait 5 seconds for it to open and full screen it on Windows OS

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
        rt = self.exec_cmd(cmd, sleep_sec=5)
        sleep(sleep_sec)
        type(Key.F11)
        return rt

    def export_sikuli_class(self, project_name):
        """
        Export a sikuli project class to the Pybot package on Windows OS

        Args:
            project_name: Name of the project to export

        Returns:
            True if class file created, False on contrary

        Examples:
            test_automaton = Pybot()
            test_automaton.export_sikuli_class("tahomaBee")
        """
        return self._export_sikuli(project_name, "Pybot")

    def export_sikuli_script(self, project_name):
        """
        Export a sikuli project script to the script library ./ on Windows OS

        Args:
            project_name: Name of the project to export

        Returns:
            True if script file created, False on contrary

        Examples:
            test_automaton = Pybot()
            test_automaton.export_sikuli_script("tahomaBee")
        """
        return self._export_sikuli(project_name, "script")

    def _export_sikuli(self, project_name, directory):
        """
        Export a sikuli project class to the Pybot package on Windows OS

        Args:
            project_name: Name of the project to export

        Raises:
            PybotException if project not found

        Returns:
            True if class file created, False on contrary
        """
        directory_name = "sikuli_project/{0}.sikuli".format(project_name)
        file_name = "{0}.py".format(project_name)
        new_file = "{0}/{1}".format(directory, file_name)
        if path.isdir(directory_name) is False:
            raise PybotException(
                "Project {0} does not exists in the sikuli_project directory".format(project_name))

        file_to_export = open(path.join(directory_name, file_name), mode="r", encoding="utf-8")
        data_to_export = "".join(
            ["'''Generated by Pybot Framework'''\nfrom lackey import *\n", file_to_export.read()])
        data_to_export = re.sub(r'([0-9]{13}.png)', r'img/\1', data_to_export)
        file_to_export.close()
        file_to_write = open(new_file, mode="w", encoding="utf-8")
        file_to_write.write(data_to_export)
        file_to_write.close()
        project_files = os.listdir(directory_name)
        for file_name in project_files:
            if file_name.endswith(IMAGE_EXT):
                img = path.join(directory_name, file_name)
                copy(img, IMG_FOLDER)
        return path.isfile(new_file)

    def _check_n_sleep(self, s):
        """
        Internal method to check s, the number of second to sleep which as to be int or float

        Args:
            s: Number of seconds

        Raises:
            PybotException
        """
        if isinstance(s, (int, float)):
            sleep(s)
        else:
            raise PybotException(
                "sleep_sec KWARG is a time in to sleep after click, therefore must be an int or float")

    def _cache_automaton_screen(self):
        """Caching the computer and screen called if cache kwarg of the constructor is True (default)"""
        if self.cache is True:
            makedirs(self.database_directory, exist_ok=True)
            db = sqlite3.connect(path.join(self.database_directory, self.database))
            db.execute(
                'CREATE TABLE IF NOT EXISTS computer (node TEXT PRIMARY KEY, os_type TEXT, os_version TEXT, ts TIMESTAMP);')
            request = "INSERT OR REPLACE INTO computer VALUES(?, ?, ?, DATETIME('now', 'localtime'));"
            db.execute(request, (self.computer, self.OS_type, self.OS_version,))
            db.execute(
                'CREATE TABLE IF NOT EXISTS screen (node TEXT, width INT, height INT, ts TIMESTAMP);')
            request = "INSERT INTO screen VALUES(?, ?, ?, DATETIME('now', 'localtime'));"
            db.execute(request, (self.computer, self.screen_width, self.screen_height,))
            db.commit()
            request = 'SELECT COUNT (*) FROM (SELECT node, width, height FROM screen WHERE node = ? GROUP BY node, width, height);'
            cur = db.cursor()
            cur.execute(request, (self.computer,))
            res = cur.fetchone()[0]
            if res > 1:
                if easygui.ynbox(
                        'Various screens have been used by this computer.\nIt can mess with Sikuli image recognition.\nShall I continue?',
                        'Display warning', ('Yes', 'No')):
                    pass
                else:
                    sys.exit(0)
            cur.close()
            db.close()

    def _cache_screenshot(self, file_name, text=""):
        """
        Caching the the name of the screenshot image

        Args:
            file_name: Name of the image file to cache

        Kwargs:
            text: Text detected in the image
        """
        if self.cache is True:
            db = sqlite3.connect(path.join(self.database_directory, self.database))
            db.execute(
                'CREATE TABLE IF NOT EXISTS screenshot (image TEXT PRIMARY KEY, node TEXT, text TEXT, ts TIMESTAMP);')
            request = "INSERT OR REPLACE INTO screenshot VALUES(?, ?, ?, DATETIME('now', 'localtime'));"
            db.execute(request, (file_name, self.computer, text,))
            db.commit()
            db.close()


"""
PybotTest as unittest.Testcase to test the development of the Pybot class
test_B_Pybot_init: Test the initialization of the Pybot object
test_C_pgm: Test of the methods related to program management
test_D_android: Test of the methods related to Android connection and mirroring
test_E_web: Test the opening of a website in the default browser
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

    @unittest.skip("Shutdown the web radio...")
    def test_E_web(self):
        """Test the opening of a website in the default browser"""
        test_automaton = Pybot()
        test_automaton.start_web("https://papit.fr", sleep_sec=5)
        assert test_automaton.kill_pgm('Firefox.exe') is True

    def test_F_export_sikuli(self):
        """Test the export of a sikuli project class to the Pybot python package"""
        test_automaton = Pybot()
        assert test_automaton.export_sikuli_class("tahomaBee") is True

    def test_G_script_sikuli(self):
        """Test the export of a sikuli project script to the script library"""
        test_automaton = Pybot()
        assert test_automaton.export_sikuli_script("tahomaBee") is True

    @unittest.skip("In case we need the base for other tests")
    def test_H_script_sikuli(self):
        """Test the cache"""
        test_automaton = Pybot()
        assert test_automaton.purge_cache() is True
        test_automaton = Pybot(cache=False)
        assert test_automaton.purge_cache() is True

    def test_I_screenshot(self):
        """Test the screenshot method"""
        test_automaton = Pybot()
        assert test_automaton.screenshot()[2] == ''
        res = test_automaton.screenshot(text=True)
        assert res[0] == 1
        assert res[2] != ''
        res = test_automaton.screenshot(text=True, lang='eng')
        assert res[0] == 1
        assert res[2] != ''


"""
Start the tests of the Pybot class
"""
if __name__ == '__main__':
    unittest.main()
