import logging
import time
import uuid
from enum import Enum
from pathlib import Path
from queue import Queue
from threading import Thread
from typing import List

from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer
from watchdog.observers.polling import PollingObserver

from MangaTaggerLib import MangaTaggerLib
from MangaTaggerLib.database import TaskQueueTable


class QueueEventOrigin(Enum):
    WATCHDOG = 1
    FROM_DB = 2
    SCAN = 3


class QueueEvent:
    def __init__(self, event, origin=QueueEventOrigin.WATCHDOG):
        if origin == QueueEventOrigin.WATCHDOG:
            self.event_type = event.event_type
            self.src_path = Path(event.src_path)
            try:
                self.dest_path = Path(event.dest_path)
            except AttributeError:
                pass
        elif origin == QueueEventOrigin.FROM_DB:
            self.event_type = event['event_type']
            self.src_path = Path(event['src_path'])
            try:
                self.dest_path = Path(event['dest_path'])
            except KeyError:
                pass
        elif origin == QueueEventOrigin.SCAN:
            self.event_type = 'existing'
            self.src_path = event

    def __str__(self):
        if self.event_type in ('created', 'existing'):
            return f'File {self.event_type} event at {self.src_path.absolute()}'
        elif self.event_type == 'modified':
            return f'File {self.event_type} event at {self.dest_path.absolute()}'

    def dictionary(self):
        ret_dict = {
            'event_type': self.event_type,
            'src_path': str(self.src_path.absolute()),
            'manga_chapter': str(self.src_path.name.strip('.cbz'))
        }

        try:
            ret_dict['dest_path'] = str(self.dest_path.absolute())
        except AttributeError:
            pass

        return ret_dict


class QueueWorker:
    _queue: Queue = None
    _observer: Observer = None
    _log: logging = None
    _worker_list: List[Thread] = None
    _running: bool = False
    _debug_mode = False

    max_queue_size = None
    threads = None
    is_library_network_path = False
    download_dir: Path = None
    task_list = {}

    @classmethod
    def initialize(cls):
        cls._log = logging.getLogger(f'{cls.__module__}.{cls.__name__}')
        cls._queue = Queue(maxsize=cls.max_queue_size)
        cls._worker_list = []
        cls._running = True

        for i in range(cls.threads):
            if not cls._debug_mode:
                worker = Thread(target=cls.process, name=f'MTT-{i}', daemon=True)
            else:
                worker = Thread(target=cls.dummy_process, name=f'MTT-{i}', daemon=True)
            cls._log.debug(f'Worker thread {worker.name} has been initialized')
            cls._worker_list.append(worker)

        if cls.is_library_network_path:
            cls._observer = PollingObserver()
        else:
            cls._observer = Observer()

        cls._observer.schedule(SeriesHandler(cls._queue), cls.download_dir, True)

    @classmethod
    def load_task_queue(cls):
        TaskQueueTable.load(cls.task_list)

        for task in cls.task_list.values():
            event = QueueEvent(task, QueueEventOrigin.FROM_DB)
            cls._log.info(f'{event} has been added to the task queue')
            cls._queue.put(event)

        TaskQueueTable.delete_all()

    @classmethod
    def save_task_queue(cls):
        TaskQueueTable.save(cls._queue)
        with cls._queue.mutex:
            cls._queue.queue.clear()

    @classmethod
    def add_to_task_queue(cls, manga_chapter):
        event = QueueEvent(manga_chapter, QueueEventOrigin.SCAN)
        cls._log.info(f'{event} has been added to the task queue')
        cls._queue.put(event)

    @classmethod
    def exit(cls):
        # Stop worker threads from picking new items from the queue in process()
        cls._log.info('Stopping processing...')
        cls._running = False

        # Stop watchdog from adding new events to the queue
        cls._log.debug('Stopping watchdog...')
        cls._observer.stop()
        cls._observer.join()

        # Save and empty task queue
        cls.save_task_queue()

        # Finish current running jobs and stop worker threads
        cls._log.info('Stopping worker threads...')
        for worker in cls._worker_list:
            worker.join()
            cls._log.debug(f'Worker thread {worker.name} has been shut down')

    @classmethod
    def run(cls):
        pass

    @classmethod
    def dummy_process(cls):
        pass

    @classmethod
    def process(cls):
        pass

class SeriesHandler(PatternMatchingEventHandler):
    _log = None

    @classmethod
    def class_name(cls):
        pass

    @classmethod
    def fully_qualified_class_name(cls):
        pass

    def __init__(self, queue):
        self._log = logging.getLogger(self.fully_qualified_class_name())
        super().__init__(patterns=['*.cbz'])
        self.queue = queue
        self._log.debug(f'{self.class_name()} class has been initialized')

    def on_created(self, event):
        pass

    def on_moved(self, event):
        pass
