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
        with open(self._video_path, 'rb') as video_file:
            video_file.seek(self._current_offset)
            data = video_file.read(request_frame.size)
            self._udp_channel.send_data(data)
            self._current_offset += request_frame.size
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
            with self._lock:
                self.__process_request(request_frame)

    def __init__(
        self,
        udp_channel: UDPChannel,
        video_path: str
    ) -> None:
        self._udp_channel = udp_channel
        self._video_path = video_path
        self._requests_queue: Queue[RequestFrame] = Queue(session_settings.max_requests)
        self._current_offset = 0
        self._lock = Lock()
        self._pause_lock = Lock()
        self._kill_event = Event()
        self._worker_thread = Thread(target=self.__handler_video)
        self._worker_thread.start()


class StreamLayer(__WorkerStreamLayer):

    def add_request(self, request_frame: RequestFrame):
        self._requests_queue.put(request_frame, block=True)

    def update_offset(self, offset: int)->bool:
        if offset >= os.path.getsize(self._video_path):
            return False
        with self._lock:
            self._current_offset = offset
            return True
    def pause(self):
        if self._pause_lock.locked():
            self._pause_lock.release()
            return
        self._pause_lock.acquire()

    def stop(self):
        self._kill_event.set()
        self._worker_thread.join()
        self._udp_channel.close()
