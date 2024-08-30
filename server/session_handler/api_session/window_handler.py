import json
import logging
import os

import ffmpeg

from core import session_settings


class WindowHandler:
    def __get_video_byterate(self, video_path: str) -> float:
        file_size = os.path.getsize(video_path)
        probe = ffmpeg.probe(video_path)
        probe_format = probe["format"]

        if "duration" in probe_format:
            duration = float(probe_format["duration"])
        else:
            logging.error("Unable to get video duration with ffmpeg.")
            logging.error(
                "Here is the dictionary returned by ffmpeg.probe:\n%s",
                json.dumps(probe, indent=4),
            )
            raise ValueError("Unable to get video duration with ffmpeg.")
        byterate = file_size / duration
        logging.info("Byte rate calculated successfully: %f bytes per second", byterate)
        return byterate

    def __get_max_video_byterate(self, video_path: str) -> float:
        video_byterate = self.__get_video_byterate(video_path)
        return video_byterate * 1.5

    # State actions
    def __duplicate_window_size(self):
        self.__current_window_size *= 2

    def __starts_to_begging(self):
        self.__threshould = self.__current_window_size / 2
        self.__current_window_size = int(self.__video_byterate * 0.2)
        self.__current_window_size -= (
            self.__current_window_size % session_settings.cluster_size
        )

    def __duplicate_until_threshould(self):
        if self.__current_window_size * 2 > self.__threshould:
            return
        self.__current_window_size = self.__current_window_size * 2

    def __increment_slowly(self):
        new_window_size = self.__current_window_size + session_settings.cluster_size
        if new_window_size >= self.__threshould:
            return
        self.__current_window_size = new_window_size

    def __keep_current_window_size(self):
        logging.info("keeping the current window size")

    def __recover_from_loss(self):
        """
        This state try recovery from a package loss backing slowly the window size
        """
        new_window_size = self.__current_window_size - session_settings.cluster_size*2
        if new_window_size < int(self.__video_byterate * 0.2):
            logging.info("window already reached to inferior threshould, nothing to do")
            return
        self.__threshould = new_window_size + session_settings.cluster_size
        self.__current_window_size = new_window_size

    # conditional transitions
    def __check_loss_percentage(self, loss_percentage: float):
        return loss_percentage-session_settings.at_most_loss_percentage >= 1e-5

    def __state_zero_transitions(self, loss_percentage: float):

        if self.__check_loss_percentage(loss_percentage):
            self.__current_state = 1
            return
        if self.__current_window_size * 2 >= self.__threshould:
            self.__current_state = 3
            return
        self.__current_state = 0

    def __state_one_transitions(self, loss_percentage: float):
        self.__current_state = 1 if self.__check_loss_percentage(loss_percentage) else 2

    def __state_two_transitions(self, loss_percentage: float):
        if self.__check_loss_percentage(loss_percentage):
            self.__current_state = 1
            return
        if self.__current_window_size * 2 >= self.__threshould:
            self.__current_state = 3
            return
        self.__current_state = 2

    def __state_three_transitions(self, loss_percentage: float):
        if self.__check_loss_percentage(loss_percentage):
            self.__current_state = 1
            return
        if (
            self.__current_window_size + session_settings.cluster_size
            >= self.__threshould
        ):
            self.__current_state = 4
            return
        self.__current_state = 3

    def __state_four_transitions(self, loss_percentage: float):
        if not self.__check_loss_percentage(loss_percentage):
            self.__current_state = 4
            return
        self.__current_state = 5

    def __state_five_transitions(self, loss_percentage:float):
        if self.__check_loss_percentage(loss_percentage):
            self.__current_state = 5
            return
        self.__current_state = 3

    def __init__(self, video_path: str) -> None:
        # Ensure the window size is a multiple of the OS cluster size
        # to avoid reading unnecessary disk blocks and maximize data usage efficiency.
        video_byterate = self.__get_max_video_byterate(video_path)
        self.__video_byterate = video_byterate
        self.__current_window_size = int(video_byterate * 0.2)
        self.__current_window_size -= (
            self.__current_window_size % session_settings.cluster_size
        )
        self.__threshould = video_byterate
        self.__current_state = 0
        self.__states_actions_map = [
            self.__duplicate_window_size,
            self.__starts_to_begging,
            self.__duplicate_until_threshould,
            self.__increment_slowly,
            self.__keep_current_window_size,
            self.__recover_from_loss
        ]
        self.__state_transitions_map = [
            self.__state_zero_transitions,
            self.__state_one_transitions,
            self.__state_two_transitions,
            self.__state_three_transitions,
            self.__state_four_transitions,
            self.__state_five_transitions
        ]

    def update_window_size(self, byte_count: int):
        logging.info("throughput: %d, bytes losed: %d", byte_count, self.__current_window_size-byte_count)
        loss_percentage = 1.0 - byte_count / self.__current_window_size
        self.__state_transitions_map[self.__current_state](loss_percentage)
        self.__states_actions_map[self.__current_state]()
        logging.info("update window size to %d", self.__current_window_size)
        logging.info("current state: %d", self.__current_state)

    def get_window_size(self) -> int:
        assert self.__current_window_size % session_settings.cluster_size == 0
        return self.__current_window_size
