import logging

from core import session_settings

# Ensure the window size is a multiple of the OS cluster size to avoid reading
# unnecessary disk blocks and maximize data usage efficiency.
STARTS_DEFAULT_SIZE = int(session_settings.upper_threshould*0.05)
STARTS_DEFAULT_SIZE -= STARTS_DEFAULT_SIZE%session_settings.cluster_size

class WindowHandler:

    # State actions
    def __duplicate_window_size(self):
        self.__current_window_size*=2

    def __starts_to_begging(self):
        self.__threshould = self.__current_window_size/2
        self.__current_window_size = STARTS_DEFAULT_SIZE

    def __duplicate_until_threshould(self):
        if self.__current_window_size*2 > self.__threshould:
            self.__current_state = 3
            self.__increment_slowly()
            return
        self.__current_window_size = self.__current_window_size*2

    def __increment_slowly(self):
        new_window_size = self.__current_window_size + session_settings.cluster_size
        if new_window_size >= self.__threshould:
            self.__current_state = 4
            self.__keep_current_window_size()
            return
        self.__current_window_size = new_window_size

    def __keep_current_window_size(self):
        logging.info("keeping the current window size")

    #conditional transitions
    def __state_zero_transitions(self, losses_ocurred:bool):
        self.__current_state = 1 if losses_ocurred else 0

    def __state_one_transitions(self, losses_ocurred:bool):
        self.__current_state = 1 if losses_ocurred else 2

    def __state_two_transitions(self, losses_ocurred:bool):
        if losses_ocurred:
            self.__current_state = 1
            return
        if self.__current_window_size*2 >= self.__threshould:
            self.__current_state = 3
            return
        self.__current_state = 2

    def __state_three_transitions(self, losses_ocurred:bool):
        if losses_ocurred:
            self.__current_state = 1
            return
        if self.__current_window_size + session_settings.cluster_size >= self.__threshould:
            self.__current_state = 4
            return
        self.__current_state = 3

    def __state_four_transitions(self, losses_ocurred:bool):
        if not losses_ocurred:
            self.__current_state = 4
            return
        self.__current_state = 0
        self.__threshould = session_settings.upper_threshould

    def __init__(
        self
    ) -> None:
        self.__current_window_size = STARTS_DEFAULT_SIZE
        self.__threshould = session_settings.upper_threshould
        self.__current_state = 0
        self.__states_actions_map = [
            self.__duplicate_window_size,
            self.__starts_to_begging,
            self.__duplicate_until_threshould,
            self.__increment_slowly,
            self.__keep_current_window_size
        ]
        self.__state_transitions_map = [
            self.__state_zero_transitions,
            self.__state_one_transitions,
            self.__state_two_transitions,
            self.__state_three_transitions,
            self.__state_four_transitions
        ]

    def update_window_size(self, byte_count: int):
        losses_ocurred = byte_count/self.__current_window_size != 1
        self.__state_transitions_map[self.__current_state](losses_ocurred)
        self.__states_actions_map[self.__current_state]()
        logging.info("update window size to %d", self.__current_window_size)
        logging.info("current state: %d", self.__current_state)

    def get_window_size(self) -> int:
        assert self.__current_window_size % session_settings.cluster_size == 0
        return self.__current_window_size
