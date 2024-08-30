from dataclasses import dataclass
import os
from queue import Queue, Empty
from threading import Event, Lock, Thread

from core import session_settings
from session_handler.data_channels import UDPChannel


@dataclass(frozen=True)
class RequestFrame:
    size: int


class __WorkerStreamLayer:
    def __process_request(self, request_frame: RequestFrame):
        """
        process a single request of stream bytes from client

        args:
            request_frame: RequestFrame -> a frame received from queue to be processed
        """
        with self._lock:
            data = self._video_file.read(request_frame.size)
            self._udp_channel.send_data(data)

    def __handler_video(self):
        while True:
            with self._pause_lock:
                pass
            if self._kill_event.is_set():
                return
            try:
                request_frame = self._requests_queue.get(block=False)
            except Empty:
                continue
            self.__process_request(request_frame)

    def __init__(self, udp_channel: UDPChannel, video_path: str) -> None:
        self._udp_channel = udp_channel
        self._video_path = video_path
        self._video_file = open(video_path, "rb")
        self._file_size = os.path.getsize(video_path)
        self._requests_queue: Queue[RequestFrame] = Queue(session_settings.max_requests)
        self._lock = Lock()
        self._pause_lock = Lock()
        self._kill_event = Event()
        self._worker_thread = Thread(target=self.__handler_video)
        self._worker_thread.start()


class StreamLayer(__WorkerStreamLayer):
    def add_request(self, request_frame: RequestFrame):
        self._requests_queue.put(request_frame, block=True)

    def update_offset(self, offset: int) -> bool:
        if offset >= self._file_size:
            return False
        with self._lock:
            self._video_file.seek(offset)
            return True
    
    def seek_forward_offset(self):
        current_offset = self._video_file.tell()
        new_offset = current_offset + int(self._file_size * 0.01)
        
        if new_offset >= self._file_size:
            print("Error: Cannot seek beyond the end of the video.")
            return False
        
        return self.update_offset(new_offset)

    def seek_backward_offset(self):
        current_offset = self._video_file.tell()
        new_offset = max(0, current_offset - int(self._file_size * 0.01))
        
        if new_offset < 0:
            new_offset = 0  # start video from the beginning if offset is less than 0

        return self.update_offset(new_offset)

    def pause(self):
        if self._pause_lock.locked():
            self._pause_lock.release()
            return
        self._pause_lock.acquire()

    def stop(self):
        with self._lock:
            self._video_file.close()
        self._kill_event.set()
        self._worker_thread.join()
        self._udp_channel.close()

    def __del__(self):
        self.stop()
