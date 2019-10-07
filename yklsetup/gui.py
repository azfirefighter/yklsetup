#!/usr/bin/python3

"""
 Copyright 2017-2018 Ian Santopietro <isantop@gmail.com>

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

gui.py - the GUI for yklsetup
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

import yklsetup

def main():
    win = Gtk.Window()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
