import pytest

from Pybot.Pybot import Pybot


@pytest.fixture(scope='module')
def test_automaton():
    """Fixture representing a default automaton class of the Pybot class."""
    automaton = Pybot()
    yield automaton
    del automaton


@pytest.mark.skip("Initialization of the test not necessary.")
def test_a_(test_automaton):
    """Nothing to do yet"""
    pass


def test_b_init(test_automaton):
    """Test the init of Pybot class."""
    assert test_automaton != ""
    assert test_automaton.python_version != ""
    assert test_automaton.os_type != ""
    assert test_automaton.os_version != ""
    assert test_automaton.machine != ""
    assert test_automaton.uname != ""


def test_c_pgm(test_automaton):
    """Test the method to manage programs."""
    assert test_automaton.start_pgm('node.exe', sleep_sec=10) is True
    assert test_automaton.check_pgm('node.exe') is True
    assert test_automaton.kill_pgm('node.exe') is True


def test_d_android(test_automaton):
    """Test the method necessary to automate Android task."""
    assert test_automaton.start_android_gui(sleep_sec=6) is True
    assert test_automaton.check_android_gui() is True
    assert test_automaton.stop_android_gui() is True
    assert test_automaton.android_connected() is True
    assert test_automaton.android_number() == 1


@pytest.mark.skip("Shutdown the web radio...")
def test_e_web(test_automaton):
    """Test the opening of a website in the default browser."""
    test_automaton.start_web("https://papit.fr", sleep_sec=5)
    assert test_automaton.kill_pgm('Firefox.exe') is True


def test_f_export_sikuli(test_automaton):
    """Test the export of a sikuli project class to the Pybot python package."""
    assert test_automaton.export_sikuli_class("TahomaBee") is True


def test_g_script_sikuli(test_automaton):
    """Test the export of a sikuli project script to the script library."""
    assert test_automaton.export_sikuli_script("TahomaBee") is True


@pytest.mark.skip("In case we need the base for other tests.")
def test_h_script_sikuli(test_automaton):
    """Test the cache."""
    assert test_automaton.purge_cache() is True
    test_automaton2 = Pybot(cache=False)
    assert test_automaton2.purge_cache() is True
    del test_automaton2


def test_i_screenshot(test_automaton):
    """Test the screenshot method."""
    assert test_automaton.screenshot()[2] == ''
    res = test_automaton.screenshot(text=True)
    assert res[0] == 1
    assert res[2] != ''
    res = test_automaton.screenshot(text=True, lang='eng')
    assert res[0] == 1
    print(res[2])
    assert res[2] != ''
