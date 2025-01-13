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
import urllib
from gettext import gettext, bindtextdomain, textdomain
import urllib.parse
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

        contains_files = False
        contains_dir = False

        for file in files:
            if file.is_directory():
                contains_dir = True
            else:
                if file.get_mime_type().startswith("text/"):
                    contains_files = True

            if contains_files and contains_dir:
                break

        if files[0].get_uri_scheme() == "file" and (contains_files ^ contains_dir):
            if contains_dir:
                return [self._create_nautilus_item(files)]
            elif contains_files:
                return [self._create_edit_file_as_admin_item(files)]
        else:
            print("Non-homogenous items selected or already in admin mode")

    def get_background_items(self, file):
        """Returns the menu items to display when no file/folder is selected
        (i.e. when right-clicking the background)."""

        # Don't show when already running as admin
        if os.geteuid() == ROOT_UID:
            return

        # Add the menu items
        self._setup_gettext()
        if file.is_directory() and file.get_uri_scheme() == "file":
            return [self._create_nautilus_item([file])]

    def _setup_gettext(self):
        """Initializes gettext to localize strings."""
        try:  # prevent a possible exception
            locale.setlocale(locale.LC_ALL, "")
        except:
            pass

        bindtextdomain("nautilus-admin", "@CMAKE_INSTALL_PREFIX@/share/locale")
        textdomain("nautilus-admin")

    def _nautilus_run(self, _, files):
        uris = []

        for i in range(len(files)):
            uris.append(
                urllib.parse.urlparse(
                    files[i].get_location().get_path(), "admin"
                ).geturl()
            )

        self.nautilus.launch_uris(uris)

    def _create_nautilus_item(self, files):
        if self.nautilus is None:
            return None

        """Creates the 'Open as Administrator' menu item."""
        item = Nautilus.MenuItem(name="NautilusAdmin::Nautilus",
                                 label=gettext("Open as Admin"),
                                 tip=gettext("Open this folder with admin privileges"))

        item.connect("activate", self._nautilus_run, files)
        return item

    def _create_edit_file_as_admin_item(self, files):
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
        for i in range(len(files)):
            uris.append(
                urllib.parse.urlparse(
                    files[i].get_location().get_path(), "admin"
                ).geturl()
            )

        self.text_editor.launch_uris(uris)
