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
from gettext import gettext, bindtextdomain, textdomain
from gi.repository import Nautilus, GObject, Gio

ROOT_UID = 0
NAUTILUS_APP_ID = "org.gnome.Nautilus.desktop"


class NautilusAdmin(Nautilus.MenuProvider, GObject.GObject):
    """Simple Nautilus extension that adds some administrative (admin) actions to
    the right-click menu, using GNOME's new admin backend."""

    def __init__(self):
        # Get an instance of system's nautilus extension in a portable way with Nautilus's application ID (works like a package name)
        self.nautilus = Gio.DesktopAppInfo.new(NAUTILUS_APP_ID)

        # Get the system's default plain text file handler
        # TODO: Figure out how to avoid hardcoding "plain"
        self.text_editor = Gio.AppInfo.get_default_for_type("text/plain", True)

    def get_file_items(self, files):
        """Returns the menu items to display when one or more files/folders are
        selected."""
        # Don't show when already running as admin
        if os.geteuid() == ROOT_UID:
            return

        # Return if no files have been selected
        if len(files) == 0:
            return

        self._setup_gettext()

        if len(files) == 1:
            file = files[0]

            if file.is_directory():
                return [self._create_selected_dir_item(file)]
            elif file.get_mime_type().startswith("text/"):
                return [self._create_edit_file_item([file])]

        for file in files:
            if file.is_directory() or not file.get_mime_type().startswith("text/"):
                return

        return [self._create_edit_file_item(files)]

    def get_background_items(self, curr_dir):
        """Returns the menu items to display when no file/folder is selected
        (i.e. when right-clicking the background)."""

        # Don't show when already running as admin
        if os.geteuid() == ROOT_UID:
            return

        # Add the menu items
        self._setup_gettext()

        if curr_dir.is_directory() and curr_dir.get_uri_scheme() == "file":
            return [self._create_current_dir_item(curr_dir)]

    def _setup_gettext(self):
        """Initializes gettext to localize strings."""
        try:  # prevent a possible exception
            locale.setlocale(locale.LC_ALL, "")
        except:
            pass

        bindtextdomain("nautilus-admin", "@CMAKE_INSTALL_PREFIX@/share/locale")
        textdomain("nautilus-admin")

    def _create_current_dir_item(self, dir):
        if self.nautilus is None:
            return None

        item = Nautilus.MenuItem(name="NautilusAdmin::NautilusCurrent",
                                 label=gettext("Open current as Admin"),
                                 tip=gettext("Open currently opened folder as Admin"))

        item.connect("activate", self._open_nautilus, dir)
        return item

    def _create_selected_dir_item(self, dir):
        if self.nautilus is None:
            return None

        """Creates the 'Open as Administrator' menu item."""
        item = Nautilus.MenuItem(name="NautilusAdmin::Nautilus",
                                 label=gettext("Open as Admin"),
                                 tip=gettext("Open this folder with admin privileges"))

        item.connect("activate", self._open_nautilus, dir)
        return item

    def _create_edit_file_item(self, files):
        if self.text_editor is None:
            return None

        """Creates the 'Edit as Administrator' menu item."""
        item = Nautilus.MenuItem(name="NautilusAdmin::TextEditor",
                                 label=gettext("Edit as Admin"),
                                 tip=gettext("Open this file in the default text editor with admin privileges"))

        item.connect("activate", self._edit_file, files)
        return item

    def _edit_file(self, _, files):
        uris = []
        for file in files:
            path = file.get_location().get_path()
            uri = f"admin:{path}"
            uris.append(uri)

        self.text_editor.launch_uris(uris)

    def _open_nautilus(self, _, dir):
        path = dir.get_location().get_path()
        uri = f"admin:{path}"
        print(uri)
        self.nautilus.launch_uris([uri])
