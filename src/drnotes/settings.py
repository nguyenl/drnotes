from PySide6.QtCore import QSettings


class Settings:
    """Persistent application settings backed by QSettings."""

    def __init__(self):
        self._s = QSettings("DrNotes", "DrNotes")

    # -- notes root directory --------------------------------------------------

    @property
    def notes_root(self) -> str:
        return self._s.value("notes_root", "", type=str)

    @notes_root.setter
    def notes_root(self, path: str):
        self._s.setValue("notes_root", path)

    # -- last opened file ------------------------------------------------------

    @property
    def last_file(self) -> str:
        return self._s.value("last_file", "", type=str)

    @last_file.setter
    def last_file(self, path: str):
        self._s.setValue("last_file", path)

    # -- window geometry -------------------------------------------------------

    @property
    def window_geometry(self) -> bytes:
        v = self._s.value("window_geometry")
        return v if v else b""

    @window_geometry.setter
    def window_geometry(self, data):
        self._s.setValue("window_geometry", data)

    # -- window state ----------------------------------------------------------

    @property
    def window_state(self) -> bytes:
        v = self._s.value("window_state")
        return v if v else b""

    @window_state.setter
    def window_state(self, data):
        self._s.setValue("window_state", data)

    # -- splitter state --------------------------------------------------------

    @property
    def splitter_state(self) -> bytes:
        v = self._s.value("splitter_state")
        return v if v else b""

    @splitter_state.setter
    def splitter_state(self, data):
        self._s.setValue("splitter_state", data)

    # -- view mode (edit / preview / split) ------------------------------------

    @property
    def view_mode(self) -> str:
        return self._s.value("view_mode", "split", type=str)

    @view_mode.setter
    def view_mode(self, mode: str):
        self._s.setValue("view_mode", mode)

    # -- theme (light / dark) --------------------------------------------------

    @property
    def dark_mode(self) -> bool:
        return self._s.value("dark_mode", False, type=bool)

    @dark_mode.setter
    def dark_mode(self, enabled: bool):
        self._s.setValue("dark_mode", enabled)

    # -- emacs mode ------------------------------------------------------------

    @property
    def emacs_mode(self) -> bool:
        return self._s.value("emacs_mode", False, type=bool)

    @emacs_mode.setter
    def emacs_mode(self, enabled: bool):
        self._s.setValue("emacs_mode", enabled)

    # -- font size -------------------------------------------------------------

    @property
    def font_size(self) -> int:
        return self._s.value("font_size", 11, type=int)

    @font_size.setter
    def font_size(self, size: int):
        self._s.setValue("font_size", size)
