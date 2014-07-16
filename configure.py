#!/usr/boin/env python
# -*- coding: utf-8 -*-

import os
import subprocess as sp

if __name__ == "__main__":

	secrets_pyFile = open(os.path.join(os.path.curdir, "spaintvs", "secrets.py"), "w")
	secrets_pyFile.write("A3PLAYER_SECRET = ''\n")
	secrets_pyFile.close()

	os.chdir("Web")
	sp.call(["python", os.path.join(os.path.curdir, "application", "generate_keys.py")])
	secrets_keys_pyFile = open(os.path.join(os.path.curdir, "secret_keys.py") , "a")
	secrets_keys_pyFile.write("_IPS_API = []\n")
	secrets_keys_pyFile.write("_DOS_IPS = []\n")
	secrets_keys_pyFile.close()

	utils_pyFile = open(os.path.join(os.path.curdir, "application", "utils.py") , "w")
	utils_pyContent = """# -*- coding: utf-8 -*-
def random1(a):
    return ""

def random3(a):
    return ""

def random2(a):
    return ""

def random4():
    return ""

def sendAPICall2Analytics(visitor, visited):
    return ""
	"""
	utils_pyFile.write(utils_pyContent)
	utils_pyFile.close()
