from core import session_settings



class WindowHandler:

    def __init__(self) -> None:
        self.__current_window_size = session_settings.default_starts_window_size
        self.__lower_threshold = None

    def __duplicate_window_size(self):
        if self.__current_window_size*2 < session_settings.threshold_window_size:
            self.__current_window_size*=2

    def __increment_slowly(self):
        new_window_size = self.__current_window_size + session_settings.window_size_increment
        if new_window_size < session_settings.threshold_window_size:
            self.__current_window_size = new_window_size

    def __increment_window(self):
        if self.__lower_threshold is not None and self.__current_window_size > self.__lower_threshold:
            self.__increment_slowly()
        else:
            self.__duplicate_window_size()

    def update_window_size(self, received_packages: int):
        if received_packages/self.__current_window_size == 1:
            self.__increment_window()
            return
        self.__lower_threshold = self.__current_window_size/2


    def get_window_size(self) -> int:
        return self.__current_window_size
