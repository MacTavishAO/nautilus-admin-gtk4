# Nautilus Admin - Extension for Nautilus to do administrative operations
# Copyright (C) 2015-2017 Bruno Nova
#               2016 frmdstryr <frmdstryr@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import locale
import os
import subprocess
from gettext import gettext, bindtextdomain, textdomain

from gi.repository import Nautilus, GObject, Gio

ROOT_UID = 0
NAUTILUS_PATH = "/usr/bin/nautilus"


class NautilusAdmin(Nautilus.MenuProvider, GObject.GObject):
    """Simple Nautilus extension that adds some administrative (admin) actions to
    the right-click menu, using GNOME's new admin backend."""

    def __init__(self):
        pass

    def get_file_items(self, files):
        """Returns the menu items to display when one or more files/folders are
        selected."""
        # Don't show when already running as admin, or when more than 1 file is selected
        if os.geteuid() == ROOT_UID or len(files) != 1:
            return
        file = files[0]

        # Add the menu items
        items = []
        self._setup_gettext()
        if file.get_uri_scheme() == "file":  # must be a local file/directory
            if file.is_directory():
                if os.path.exists(NAUTILUS_PATH):
                    items += [self._create_nautilus_item(file)]
            else:
                items += [self._create_edit_file_as_admin_item(file)]

        return items

    def get_background_items(self, file):
        """Returns the menu items to display when no file/folder is selected
        (i.e. when right-clicking the background)."""
        # Don't show when already running as admin
        if os.geteuid() == ROOT_UID:
            return

        # Add the menu items
        items = []
        self._setup_gettext()
        if file.is_directory() and file.get_uri_scheme() == "file":
            if os.path.exists(NAUTILUS_PATH):
                items += [self._create_nautilus_item(file)]

        return items

    def _setup_gettext(self):
        """Initializes gettext to localize strings."""
        try:  # prevent a possible exception
            locale.setlocale(locale.LC_ALL, "")
        except:
            pass
        bindtextdomain("nautilus-admin", "@CMAKE_INSTALL_PREFIX@/share/locale")
        textdomain("nautilus-admin")

    def _nautilus_run(self, _, file):
        """'Open as Administrator' menu item callback."""
        uri = file.get_uri()
        admin_uri = uri.replace("file://", "admin://")
        subprocess.Popen([NAUTILUS_PATH, admin_uri])

    def _create_nautilus_item(self, file):
        """Creates the 'Open as Administrator' menu item."""
        item = Nautilus.MenuItem(name="NautilusAdmin::Nautilus",
                                 label=gettext("Open as admin"),
                                 tip=gettext("Open this folder with admin privileges"))
        item.connect("activate", self._nautilus_run, file)
        return item

    def _create_edit_file_as_admin_item(self, file):
        """Creates the 'Edit as Administrator' menu item."""
        item = Nautilus.MenuItem(name="NautilusAdmin::TextEditor",
                                 label=gettext("Edit as admin"),
                                 tip=gettext("Open this file in the default text editor with admin privileges"))
        item.connect("activate", self._edit_file, file)
        return item

    def _edit_file(self, _, file):
        """'Edit as Administrator' menu item callback."""
        uri = file.get_uri()
        admin_uri = uri.replace("file://", "admin://")
        content_type = Gio.content_type_guess()
        text_editor = Gio.app_info_get_default_for_type(content_type[0], True).get_executable()
        if text_editor is not None:
            subprocess.Popen([text_editor, admin_uri])
