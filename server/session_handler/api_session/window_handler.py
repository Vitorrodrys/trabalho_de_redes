import json
import logging
import os

import ffmpeg

from core import session_settings

class WindowHandler:

    def __get_video_byterate(self, video_path: str) -> float:
        file_size = os.path.getsize(video_path)
        probe = ffmpeg.probe(video_path)
        probe_format = probe['format']

        if 'duration' in probe_format:
            duration = float(probe_format['duration'])
        else:
            logging.error("Unable to get video duration with ffmpeg.")
            logging.error(
                "Here is the dictionary returned by ffmpeg.probe:\n%s", 
                json.dumps(
                    probe,
                    indent=4
                )
            )
            raise ValueError("Unable to get video duration with ffmpeg.")
        byterate = file_size / duration
        logging.info("Byte rate calculated successfully: %f bytes per second", byterate)
        return byterate

    # State actions
    def __duplicate_window_size(self):
        self.__current_window_size*=2

    def __starts_to_begging(self):
        self.__threshould = self.__current_window_size/2
        self.__current_window_size = int(self.__video_byterate*0.05)
        self.__current_window_size -= self.__current_window_size%session_settings.cluster_size

    def __duplicate_until_threshould(self):
        if self.__current_window_size*2 > self.__threshould:
            return
        self.__current_window_size = self.__current_window_size*2

    def __increment_slowly(self):
        new_window_size = self.__current_window_size + session_settings.cluster_size
        if new_window_size >= self.__threshould:
            return
        self.__current_window_size = new_window_size

    def __keep_current_window_size(self):
        logging.info("keeping the current window size")

    #conditional transitions
    def __state_zero_transitions(self, losses_ocurred:bool):
        if self.__current_window_size*2 >= self.__threshould:
            self.__current_state = 3
            return
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
        self.__threshould = self.__video_byterate
        self.__current_window_size = int(self.__video_byterate*0.05)
        self.__current_window_size -= self.__current_window_size%session_settings.cluster_size

    def __init__(
        self,
        video_path: str
    ) -> None:
        # Ensure the window size is a multiple of the OS cluster size
        # to avoid reading unnecessary disk blocks and maximize data usage efficiency.
        video_byterate = self.__get_video_byterate(video_path)
        self.__video_byterate = video_byterate
        self.__current_window_size = int(video_byterate*0.05)
        self.__current_window_size -= self.__current_window_size%session_settings.cluster_size
        self.__threshould = video_byterate
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
