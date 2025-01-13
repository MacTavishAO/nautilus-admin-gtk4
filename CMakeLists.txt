cmake_minimum_required(VERSION 2.6)
project(NautilusAdmin NONE)
find_package(Gettext REQUIRED)

# Configurable paths
execute_process(COMMAND which nautilus OUTPUT_VARIABLE NAUTILUS_PATH OUTPUT_STRIP_TRAILING_WHITESPACE)
set(INSTALLATION_DIR "$ENV{HOME}/.local/share/nautilus-python/extensions")

# Configure files
configure_file(extension/nautilus-admin.py extension/nautilus-admin.py)

# Install target
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/extension/nautilus-admin.py"
        DESTINATION "${INSTALLATION_DIR}")