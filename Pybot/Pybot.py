"""
=====
Pybot
=====
   Pybot class can be used as Jython source to be used in sikuli IDE, not pure python or python3.
   Initialize the script by importing the required libraries for test (a.k.a unittest), subprocess and system to using
   Windows commands.
   Lackey package provide a wrapper arround Sikuli. Contain sources description.
   Custom class to be used in as an abstraction layer to sikuli methods and corresponding exception.
   Can used command to start/stop program or use commands, access Android mirroring.
   Interpretation of GUI, access to windows system commands.

   .. warning:: Coding style is CamelCase for classes and lowercase_separated_by_underscores A.K.A snake_case for
      methods and variables.
"""
import locale
import re
import sqlite3
import subprocess
# Import unittest in case of test automation
import unittest
from datetime import datetime
# To start program of command
from os import path, makedirs, remove, listdir, system
from shutil import copy, rmtree, move
from time import sleep

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

IMG_FOLDER = "img/"
IMAGE_EXT = ".png"
SQLITE3_EXT = "sqlite3"
SQLITE3_DATABASE = "pybot.sqlite3"
SCRCPY_FOLDER = "scrcpy-windows-v1.1"
SCRCPY_EXE = "scrcpy.exe"
TESSERACT_CMD = "tesseract"
ADB_CMD = "adb.exe"
COMMANDS = {
    "kill_process": {"Windows": "taskkill /im {0} /f",
                     "Darwin": "pkill {0}",  # TODO be tested
                     "Linux": "pkill {0}"},  # TODO add linux compatibility and test
    "check_process": {"Windows": 'tasklist /FI "IMAGENAME eq {0}" 2>NUL | find /I /N "{0}">NUL',
                     "Darwin": "pkill {0}",  # TODO be tested
                     "Linux": "pkill {0}"},  # TODO be tested
}
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
    Something to automate on a computer a task, a test, etc..."
    """

    def __init__(self, cache=True):
        """
        Constructor of the Pybot class.
           :param cache: Call a caching method if True, which is the default value.
           :raise PybotException: in case of platform compatibility.
           :raise TypeError: TypeError if kwarg cache is not a boolean.
        """
        if isinstance(cache, bool) is True:
            self.cache = cache
        else:
            raise TypeError("Kwarg cache must be a boolean type, True or False.")
        if platform.system() == "Windows":
            self.python_version = sys.version
            self.os_type = platform.system()
            self.os_version = platform.platform()
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
        else:
            raise PybotException(
                "Pybot class only for Windows platform at the moment.")

    def __repr__(self):
        """
        Description of the Pybot object.
        """
        return "{0} automaton executed on {1}, a {2} computer".format(
            self.python_version, self.computer, self.os_version)

    def __del__(self):
        """
        On Pybot object deletion or end of execution or garbage collecting.
        """
        self.stop_android_gui()

    def purge_cache(self):
        """
        Deleting cache database.
           :return: True if cache is clear, False on contrary.
        """
        rmtree(self.database_directory)
        return path.isdir(self.database_directory) is False

    def text(self, bounds=None, lang=None):
        """
        Retrieve the text on the screen, default is all the screen.
           :param bounds: The bounds of the image to take, default is None, to get the all screen.
           :param lang: Specify a lang for the image text by tesseract.
           :return: The string decrypted from the screen.
           :raise TypeError: If wrong bounds kwarg type. Default is None.
           :raise PybotException: If wrong tesseract lang kwarg (tesseract language). Default is None.
           :example:
              .. code-block:: python

                 test_automaton = Pybot()
                 test_automaton.text(lang='eng') # get text of the full screen with english text description
        """
        if lang in TESSERACT_LANG.values() or lang is None:
            if isinstance(bounds, tuple) and len(bounds) == 4 * self.num_screen or bounds is None:
                _, _, text = self.screenshot(bounds=bounds, text=True, lang=lang)
                remove(path.join(IMG_FOLDER + text))
                return text
            else:
                raise TypeError('Kwarg bounds must be tuple type (of bounds).')
        else:
            raise PybotException("Kwarg lang must be in tesseract language list values or None.")

    def screenshot(self, bounds=None, text=False, lang=None):
        """
        Taking a screenshot, default is all the screen.
           :param bounds: The bounds of the image to take, default is None, to get the all screen.
           :param text: Boolean True to discover text, False on contrary.
           :param lang: Specify a lang for the image text. Default is None.
           :return: A tuple made of the boolean integer, image file and thetext discovered in the image.
           :raise TypeError: If wrong bounds kwarg type.
           :raise PybotException: If wrong tesseract lang kwarg (tesseract language).
           :example:
              .. code-block:: python

                 test_automaton = Pybot()
                 test_automaton.screenshot(lang='eng') # Screenshot of the full screen with english text description
        """
        if bounds is None:
            desired_bounds = self.screen_bounds
        elif isinstance(bounds, tuple) is False:
            raise TypeError('Kwarg bounds must be tuple type (of bounds)')
        else:
            if isinstance(bounds, tuple) and len(bounds) == 4 * self.num_screen:
                desired_bounds = bounds
            else:
                raise TypeError(
                    "Bound kwarg has to be a tuple with length of 4 multiply by the number of screen(s).")
        if lang in TESSERACT_LANG.values() or lang is None:
            if isinstance(text, bool) is True:
                data = self.screen.capture(desired_bounds)
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
            else:
                raise TypeError("text kwarg has to be a boolean")
        else:
            raise PybotException("Kwarg lang must be in tesseract language list values or None")

    def get_text_img(self, img_file, lang=None):
        """
        Retrieve text from an image.
           :param img_file: Name of the image file.
           :param lang: None is default, this parameter specify a language to tesseract.
           :return: String of the text decrypted
           :raise TypeError: If wrong bounds kwarg type.
           :raise PybotException: If wrong tesseract lang kwarg (tesseract language). Default is None.
           :examples:
              .. code-block:: python

                 test_automaton = Pybot()
                 test_automaton.screenshot("1234567891012.png",lang='eng')
        """
        if isinstance(img_file, str) is True:
            img = Image.open(path.join(IMG_FOLDER + img_file))
            if lang in TESSERACT_LANG.values() or lang is None:
                pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD
                if lang is None:
                    text = pytesseract.pytesseract.image_to_string(img)
                else:
                    text = pytesseract.pytesseract.image_to_string(img, lang=lang)
                return text
            else:
                raise PybotException("Kwarg lang must be in tesseract language list values or None")
        else:
            raise TypeError("First argument img_file has to be a string being the image file name")

    def check_click(self, img, sleep_sec=0, after_click=None):
        """
        Method checking if button exist and clicking on it, return True is clicked False on contrary. Eventually sleep.
           :param img: Image path to work on. Check if exist and click.
           :param sleep_sec: Number of seconds of seconds to eventually sleep after the click.
           :param after_click: Another image to eventually click after the first click and before the sleep.
           :return: True if img was found and clicked, False on contrary.
           :raise TypeError: If arg (img) or kwarg (after_click) are not string type.
           :raise PybotException: If img or after_click file path does not exist.
        """
        if isinstance(img, str) is True:
            if path.isfile(img) is True:
                if exists(img) is None:
                    return False
                else:
                    click(img)
                    if isinstance(after_click, str) is True:
                        if path.isfile(after_click) is True:
                            if after_click is not None and exists(after_click) is not None:
                                click(after_click)
                            self._check_n_sleep(sleep_sec)
                            return True
                        else:
                            raise PybotException('Kwarg after_click file path does not exist.')
                    else:
                        raise TypeError('Kwarg after_click must be a string.')
            else:
                raise PybotException('First argument img file path does not exist.')
        else:
            raise TypeError('First argument img must be a string.')

    def wait_click(self, img, sleep_sec=0):
        """
        Method that wait for a button to appear and click on it. Eventually sleep sleep_sec seconds after.
           :param img: Image to wait for and click.
           :param sleep_sec: Number of seconds of seconds to eventually sleep after the click.
           :raise TypeError: If first argument img is not string type.
           :raise PybotException: If first argument img file path does not exist.
        """
        if isinstance(img, str) is True:
            if path.isfile(img) is True:
                wait(img)
                click(img)
                self._check_n_sleep(sleep_sec)
            else:
                raise PybotException('First argument img file path does not exist.')
        else:
            raise TypeError('First argument img must be a string.')

    def type_n_time(self, n, key, sleep_sec=0):
        """
        Type n time the desired key. Eventually sleep sleep_sec seconds.
           :param n: Number of time to type the key.
           :param key: Key to type.
           :param sleep_sec: Number of seconds of seconds to eventually sleep after the click.
           :raise TypeError: n must be an integer or float type.

           :examples:
              .. code-block:: python

                test_automaton = Pybot()
                test_automaton.type_n_time(5, Key.11)
        """
        if isinstance(n, (int, float)):
            i = 0
            while i < n:
                type(key)
                self._check_n_sleep(sleep_sec)
                i += 1
        else:
            raise TypeError(
                "n is the number of time to type the key, therefore must be an int or float.")

    def exec_cmd(self, cmd, sleep_sec=0):
        """
        Execute command on Windows OS.
           :param cmd: Command to execute passed a string.
           :param sleep_sec: Number of seconds to eventually sleep after the click.
           :return: True if return code of the command is 0, false on contrary.
           :raise TypeError: If first argument cmd is not a string type.
           :examples:
              .. code-block:: python

                 test_automaton = Pybot()
                 test_automaton.exec_cmd("DIR")
        """
        if isinstance(cmd, str) is True:
            rt = system(cmd)
            self._check_n_sleep(sleep_sec)
            return rt == 0
        else:
            raise TypeError('First argument cmd must be an str type.')

    def start_android_gui(self, sleep_sec=5, fullscreen=True):
        """
        Start Android mirroring with SCRCPY_EXE if connected and full screen it.
           :param sleep_sec: Number of seconds to eventually sleep after the click.
           :param fullscreen: If True, start android scrcpy in fullscreen.
           :raise TypeError: If kwarg fullscreen is not an boolean type.
           :return: Boolean True if started, False on contrary.
        """
        if isinstance(fullscreen, bool) is True:
            if self.android_number() == 1:
                return_code = self.start_pgm(
                    SCRCPY_EXE, working_directory=SCRCPY_FOLDER, sleep_sec=sleep_sec)
            else:
                return_code = False
            if fullscreen is True:
                self.android_fullscreen()
            return return_code
        else:
            raise TypeError('Kwarg fullscreen must an boolean, True or False.')

    def android_fullscreen(self):
        """
        Type the scrcpy shortcut to full screen f + CTRL.
        """
        self.ctrl_shorcut('f')

    def android_resize_one_to_one(self):
        """
        resize window to 1:1 (pixel-perfect).
        """
        self.ctrl_shorcut('g')

    def android_remove_black_borders(self):
        """
        resize window to remove black borders.
        """
        self.ctrl_shorcut('x')

    def android_home(self):
        """
        click on HOME.
        """
        self.ctrl_shorcut('h')

    def android_back(self):
        """
        click on BACK.
        """
        self.ctrl_shorcut('b')

    def android_app_switch(self):
        """
        click on APP_SWITCH.
        """
        self.ctrl_shorcut('m')

    def android_volume_up(self):
        """
        click on VOLUME_UP.
        """
        self.ctrl_shorcut('+')

    def android_volume_down(self):
        """
        click on VOLUME_DOWN.
        """
        self.ctrl_shorcut('-')

    def turn_screen_on(self):
        """
        turn screen on.
        """
        rightClick()

    def android_power(self):
        """
        click on POWER.
        """
        self.ctrl_shorcut('p')

    def android_paste_clipboard(self):
        """paste computer clipboard to device2
        """
        self.ctrl_shorcut('v')

    def android_toggle_fps_counter(self):
        """
        enable/disable FPS counter (on stdout)2
        """
        self.ctrl_shorcut('i')

    def ctrl_shorcut(self, key):
        """
        Type a key with the key modifier CTRL.
           :param key: The key to type with the CTRL modifier.
        """
        type(key, Key.CTRL)

    def check_android_gui(self):
        """
        Check that Android mirroring with SCRCPY_EXE is running.
           :return: Boolean True if mirroring, False on contrary.
        """
        return self.check_pgm(SCRCPY_EXE)

    def stop_android_gui(self):
        """
        Stop SCRCPY_EXE processes.
           :return: Boolean True if command executed correctly, False on contrary.
        """
        return self.kill_pgm(SCRCPY_EXE)

    def android(self):
        """
        Access connected Android device via adb.exe.
           :return: Tuple containing the Android Serial number and device type.
        """
        adb_output = subprocess.check_output(
            [path.join(SCRCPY_FOLDER, ADB_CMD), "devices"]).decode()
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
        Check if an Android is connected.
           :return: True if command Android connected, False on contrary.
        """
        return len(self.android()) != 0

    def android_number(self):
        """
        Calculate the number of Android device connected.
           :return: Integer corresponding to the number of Android device(s).
        """
        return len(self.android())

    def start_pgm(self, pgm, working_directory=None, pgm_arg=None, sleep_sec=0):
        """
        Start a program in background in a given directory on Windows OS.
           :param pgm: Program to start.
           :param working_directory: Working directory to start the program, with the .exe extension.
           :param pgm_arg: Eventual argument of the program to start.
           :param sleep_sec: Number of seconds of seconds to eventually sleep after the click.
           :return: True if return code of the command is 0, false on contrary.
           :raise TypeError: If kwarg pgm_arg or working_direcory kwarg are not None or string type.
           :examples:
              .. code-block:: python
              
                 test_automaton = Pybot()
                 test_automaton.start_pgm('node.exe', working_directory='server', sleep_sec=5)
        """
        if isinstance(pgm_arg, str) is True or pgm_arg is None:
            if isinstance(working_directory, str) is True or pgm_arg is None:
                if working_directory is None:
                    prefix = ""
                else:
                    prefix = "cd {0} && ".format(working_directory)

                if pgm_arg is None:
                    suffix = ""
                else:
                    suffix = " {0}".format(pgm_arg)

                cmd = "{0}START /B {1}{2}".format(prefix, pgm, suffix)
                rt = self.exec_cmd(cmd)
                self._check_n_sleep(sleep_sec)
                return rt
            else:
                raise TypeError('Kwarg working_directory must a string type.')
        else:
            raise TypeError('Kwarg pgm_arg must a string type.')

    def check_pgm(self, pgm):
        """
        Check if a program is running.
           :param pgm: Program to check, with the .exe extension.
           :return: True if program running, false on contrary.
           :raise TypeError: If only argument pgm is not a string.

           :examples:
              .. code-block:: python

                 test_automaton = Pybot()
                 test_automaton.check_pgm("Firefox.exe")
        """
        if isinstance(pgm, str) is True:

            cmd = 'tasklist /FI "IMAGENAME eq {0}" 2>NUL | find /I /N "{0}">NUL'.format(
                pgm)
            return self.exec_cmd(cmd, sleep_sec=0)
        else:
            raise TypeError('First argument pgm must be a string type.')

    def kill_pgm(self, pgm, sleep_sec=0):
        """
        Kill a program
           :param pgm: Program to kill, with the .exe extension.
           :param sleep_sec: Number of seconds of seconds to eventually sleep after the click.
           :return: True if return code of the command is 0, false on contrary.
           :raise TypeError: If kwarg pgm_arg or working_direcory kwarg are not None or string type.
        """
        if isinstance(pgm, str) is True:
            cmd = COMMANDS["kill_process"][self.os_type].format(pgm)
            return_code = self.exec_cmd(cmd, sleep_sec=0)
            self._check_n_sleep(sleep_sec)
            return return_code
        else:
            raise TypeError('First argument pgm must a string type.')

    def start_web(self, url, sleep_sec=0):
        """
        Start a website on the default browser, wait 5 seconds for it to open and full screen it on Windows OS.
           :param url: URL of the website.
           :param sleep_sec: Number of seconds of seconds to eventually sleep after the click.
           :return: True if return code of the command is 0, false on contrary.
           :raise TypeError: If only argument url is not a string.
           :examples:
              .. code-block:: python

                 test_automaton = Pybot()
                 test_automaton.start_web("https://papit.fr")
        """
        if isinstance(url, str) is True:
            cmd = "START {0}".format(url)
            return_code = self.exec_cmd(cmd, sleep_sec=5)
            sleep(sleep_sec)
            type(Key.F11)
            return return_code

        else:
            raise TypeError('First argument url must a string type.')

    def export_sikuli_class(self, project_name):
        """
        Export a sikuli project class to the Pybot package on Windows OS.
           :param project_name: Name of the project to export.
           :return: True if class file created, False on contrary.
           :examples:
              .. code-block:: python

                 test_automaton = Pybot()
                 test_automaton.export_sikuli_class("tahomaBee")
        """
        return self._export_sikuli(project_name, "Pybot")

    def export_sikuli_script(self, project_name):
        """
        Export a sikuli project script to the script library ./ on Windows OS.
           :param project_name: Name of the project to export.
           :return: True if script file created, False on contrary.
           :examples:
              .. code-block:: python

                 test_automaton = Pybot()
                 test_automaton.export_sikuli_script("tahomaBee")
        """
        return self._export_sikuli(project_name, "script")

    def _export_sikuli(self, project_name, directory):
        """
        Export a sikuli project class to the Pybot package on Windows OS.
           :param project_name: Name of the project to export.
           :param  directory: Export directory of the sikuli project.
           :raise PybotException: If project not found.
           :return: True if class file created, False on contrary.
        """
        directory_name = "sikuli_project/{0}.sikuli".format(project_name)
        if path.isdir(directory_name) is True:
            file_name = "{0}.py".format(project_name)
            new_file = "{0}/{1}".format(directory, file_name)
            file_to_export = open(path.join(directory_name, file_name), mode="r", encoding="utf-8")
            data_to_export = "".join(
                ["'''Generated by Pybot Framework'''\nfrom lackey import *\n", file_to_export.read()])
            data_to_export = re.sub(r'([0-9]{13}.png)', r'img/\1', data_to_export)
            file_to_export.close()
            file_to_write = open(new_file, mode="w", encoding="utf-8")
            file_to_write.write(data_to_export)
            file_to_write.close()
            project_files = listdir(directory_name)
            for file_name in project_files:
                if file_name.endswith(IMAGE_EXT):
                    img = path.join(directory_name, file_name)
                    copy(img, IMG_FOLDER)
            return path.isfile(new_file)
        else:
            raise PybotException(
                "Project {0} does not exists in the sikuli_project directory.".format(project_name))

    def _check_n_sleep(self, second):
        """
        Internal method to check second, the number of second(s) to sleep, which as to be int or float.
           :param second: Number of seconds.
           :raise TypeError: First argument second must be an integer or a float.
        """
        if isinstance(second, (int, float)):
            sleep(second)
        else:
            raise TypeError(
                "sleep_sec kwarg is a time in to sleep after click, therefore must be an int or float.")

    def _cache_automaton_screen(self):
        """Caching the computer and screen, called if cache kwarg of the constructor is True (default)."""
        if self.cache is True:
            makedirs(self.database_directory, exist_ok=True)
            db = sqlite3.connect(path.join(self.database_directory, self.database))
            db.execute(
                '''CREATE TABLE IF NOT EXISTS computer 
                (node TEXT PRIMARY KEY, os_type TEXT, os_version TEXT, ts TIMESTAMP);''')
            request = "INSERT OR REPLACE INTO computer VALUES(?, ?, ?, DATETIME('now', 'localtime'));"
            db.execute(request, (self.computer, self.os_type, self.os_version,))
            db.execute(
                'CREATE TABLE IF NOT EXISTS screen (node TEXT, width INT, height INT, ts TIMESTAMP);')
            request = "INSERT INTO screen VALUES(?, ?, ?, DATETIME('now', 'localtime'));"
            db.execute(request, (self.computer, self.screen_width, self.screen_height,))
            db.commit()
            request = '''SELECT COUNT (*) 
            FROM (SELECT node, width, height 
                FROM screen 
                WHERE node = ? GROUP BY node, width, height);'''
            cur = db.cursor()
            cur.execute(request, (self.computer,))
            res = cur.fetchone()[0]
            if res > 1:
                if easygui.ynbox(
                        '''Various screens have been used by this computer.\nIt can mess with Sikuli image recognition.
Shall I continue?''',
                        'Display warning', ('Yes', 'No')):
                    pass
                else:
                    sys.exit(0)
            cur.close()
            db.close()

    def _cache_screenshot(self, file_name, text=""):
        """
        Caching the the name of the screenshot image.
           :param file_name: Name of the image file to cache.
           :param text: Text detected in the image by tesseract.
           :raise TypeError: If first argument file_name is not a string type.
        """
        if isinstance(file_name, str) is True:
            if self.cache is True:
                db = sqlite3.connect(path.join(self.database_directory, self.database))
                db.execute('''CREATE TABLE IF NOT EXISTS screenshot 
                    (image TEXT PRIMARY KEY, node TEXT, text TEXT, ts TIMESTAMP);''')
                request = "INSERT OR REPLACE INTO screenshot VALUES(?, ?, ?, DATETIME('now', 'localtime'));"
                db.execute(request, (file_name, self.computer, text,))
                db.commit()
                db.close()
        else:
            raise TypeError('First argument file_name must be a string type.')
