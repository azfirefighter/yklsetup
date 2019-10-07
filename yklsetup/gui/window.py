#!/usr/bin/python3

"""
 Copyright 2017-2018 Ian Santopietro <isantop@gmail.com>

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

gui.py - the GUI for yklsetup
"""
import os
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from .headerbar import Headerbar

import yklsetup

class Window(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self)
        self.header = Headerbar()
        self.set_titlebar(self.header)

        self.delete_button = Gtk.Button.new_from_icon_name(
            'edit-delete-symbolic', 
            Gtk.IconSize.BUTTON
        )
        self.delete_button.connect('clicked', self.on_delete_button_clicked)
        self.delete_button.set_tooltip_text(
            'Uninstall PAM Support (disables Yubikey login system-wide)'
        )
        self.header.pack_start(self.delete_button)

        self.refresh_button = Gtk.Button.new_from_icon_name(
            'view-refresh-symbolic',
            Gtk.IconSize.BUTTON
        )
        self.refresh_button.connect('clicked', self.on_refresh_button_clicked)
        # self.header.pack_end(self.refresh_button)

        self.content_grid = Gtk.Grid()
        self.content_grid.props.row_spacing = 12
        self.content_grid.props.column_spacing = 12
        self.add(self.content_grid)

        self.pam_infobar = Gtk.InfoBar()
        self.pam_infobar.props.width_request = 430
        self.pam_infobar.add_button(
            'Install PAM Support',
            0
        )
        self.pam_infobar.connect('response', self.on_infobar_response)
        pam_infobar_label = Gtk.Label(
            'PAM Support is missing and must be installed to enable Yubikey login'
        )
        pam_infobar_label.props.wrap = True
        self.pam_infobar.get_content_area().add(pam_infobar_label)
        self.pam_infobar.set_message_type(Gtk.MessageType.INFO)
        self.pam_infobar.props.revealed = False
        self.content_grid.attach(self.pam_infobar, 0, 0, 2, 1)
        self.show_infobar()
        
        username = yklsetup.system.get_username()
        user_avatar_path = os.path.join(
            '/var/lib/AccountsService/icons',
            username
        )

        self.user_avatar = Gtk.Grid()
        self.user_avatar.props.row_spacing = 6
        self.user_avatar.props.column_spacing = 12
        self.user_avatar.props.margin = 12
        self.user_avatar.props.hexpand = True
        self.user_avatar.props.vexpand = True
        self.user_avatar.props.halign = Gtk.Align.CENTER
        self.user_avatar.props.valign = Gtk.Align.END
        self.content_grid.attach(self.user_avatar, 0, 1, 1, 1)

        self.user_avatar_image = Gtk.Image()
        self.user_avatar_image.props.hexpand = True
        self.user_avatar_image.set_from_file(user_avatar_path)
        self.user_avatar.attach(self.user_avatar_image, 0, 0, 1, 1)
        
        self.user_label = Gtk.Label(username)
        Gtk.StyleContext.add_class(self.user_label.get_style_context(), "h2")
        self.user_avatar.attach(self.user_label, 0, 1, 1, 1)

        self.switch_grid = Gtk.Grid()
        self.switch_grid.props.row_spacing = 12
        self.switch_grid.props.column_spacing = 12
        self.switch_grid.props.margin = 12
        self.switch_grid.props.hexpand = True
        self.switch_grid.props.vexpand = True
        self.switch_grid.props.halign = Gtk.Align.CENTER
        self.switch_grid.props.valign = Gtk.Align.START
        self.content_grid.attach(self.switch_grid, 0, 2, 1, 1)
        
        self.switch_label = Gtk.Label('Yubikey Login')
        self.switch_grid.attach(self.switch_label, 0, 0, 1, 1)

        self.login_switch = Gtk.Switch()
        self.login_switch.set_active(self.get_current_auth_state(username))
        self.login_switch.connect("notify::active", self.on_switch_activated)
        self.switch_grid.attach(self.login_switch, 1, 0, 1, 1)
    
    def get_current_auth_state(self, user):
        auths = yklsetup.system.get_auths()
        for auth in auths:
            if user in auth:
                return True
        return False
    
    def on_infobar_response(self, widget, response_id):
        if response_id == 0:
            try:
                yklsetup.pam.modify_pam_files(req='sufficient')
                self.pam_infobar.props.revealed = False
            except:
                self.pam_infobar.props.revealed = True

    def on_switch_activated(self, switch, data=None):
        if switch.get_active():
            user_home = yklsetup.system.get_user_home()
            yklsetup.yubikey.setup_slot(slot=2)
            key = yklsetup.yubikey.make_config(user_home, slot=2)
            yklsetup.system.ensure_sys_config_dir()
            challenge_path = f'/var/yubico/{yklsetup.system.get_username()}-{key[2]}'
            yklsetup.system.privilged_move_file(key[0], challenge_path)
        else:
            yklsetup.system.deauthorize_yuibikey()
    
    def show_infobar(self):
        pam_configs = yklsetup.pam.check_pam_configured()

        if pam_configs != 1:
            self.pam_infobar.props.revealed = True

    def on_delete_button_clicked(self, widget, data=None):
        yklsetup.pam.deauthorize_pam()
        self.show_infobar()
    
    def on_refresh_button_clicked(self, widget, data=None):
        yklsetup.system.restart_service()
        yklsetup.pam.check_pam_configured()
        