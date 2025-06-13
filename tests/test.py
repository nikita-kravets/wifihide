import unittest
import datetime
import re
import time
import itertools
from colorama import Fore, Style
from wifihide import wifihide

class FakeTerm:
    """A simple emulator"""
    def __init__(self):
        self.__out = "(config)"
    
    def sendline(self, line: str):
        self.__line = str

    def expect(self, exp: str, timeout = -1):
        if timeout > 0:
            time.sleep(timeout)
        if exp != self.__out:
            raise Exception("Expectation failed!")

class Test(unittest.TestCase):
    """A test for SSID and passwd generation"""
    def test_passwd_gen_default(self):
        newpass, secret = wifihide.passwd_gen()
        self.assertNotEqual(re.match(r"^#[a-f0-9]{6}$", newpass), None, 
                            "Generated password does not match required pattern!")
        self.assertEqual(secret, "-" + str(datetime.date.today().day).rjust(2, "0"), 
                         "Generated secret mismatch")
    
    def test_passwd_gen_secret(self):
        newpass, secret = wifihide.passwd_gen("my_secret")
        self.assertNotEqual(re.match(r"^#[a-f0-9]{6}-my_secret$", newpass + secret), None, 
                            "Password mismatch")

    def test_combine(self):
        # case 1
        a = []
        b = []
        default = "dummy"
        self.assertEqual(wifihide.combine(a, b, default), default, 
                         "Must return given default!")
        # case 2
        a = ["a","b","c"]
        b = ["e","f"]
        cross = list(itertools.product(a, b))
        c = tuple(wifihide.combine(a, b, default).split("-")) 
                  
        self.assertEqual(c in cross, True, "A generated value should be in a cross product!")

        
class TerminalTest(unittest.TestCase):
    """A test for a terminal connection using emulator"""
    def test_execute(self):
        result = True
        term = FakeTerm()
        try:
            wifihide.execute("dummy", term, "(config)")
        except Exception:
            result = False

        self.assertEqual(result, True)

if __name__ == "__main__":
    unittest.main()
