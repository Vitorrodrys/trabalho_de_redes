import logging

from core import session_settings

class WindowHandler:

    def __init__(
        self
    ) -> None:
        self.__current_window_size = int(session_settings.superior_threshould*0.05)
        self.__lower_threshold = None
        self.__superior_threshould = session_settings.superior_threshould

    def __duplicate_window_size(self):
        if self.__current_window_size*2 < self.__superior_threshould:
            self.__current_window_size*=2
        else:
            logging.info("threshould window size %d arrived", self.__superior_threshould)

    def __increment_slowly(self):
        new_window_size = self.__current_window_size + session_settings.window_size_increment
        if new_window_size < self.__superior_threshould:
            self.__current_window_size = new_window_size

    def __increment_window(self):
        if self.__lower_threshold is not None and self.__current_window_size > self.__lower_threshold:
            self.__increment_slowly()
        else:
            self.__duplicate_window_size()

    def update_window_size(self, byte_count: int):
        if byte_count/self.__current_window_size == 1:
            self.__increment_window()
            logging.info("increasing window size to %d", self.__current_window_size)
            
            return
        logging.info("was detect losed packages, decreasing window size")
        self.__lower_threshold = self.__current_window_size/2


    def get_window_size(self) -> int:
        return self.__current_window_size
