import time
from concurrent.futures import ThreadPoolExecutor
from threading import Event, Thread
from typing import Any, Callable, Dict

import schedule

from ..utils.logger import get_logger

logger = get_logger(__name__)


class AdvancedTaskScheduler:
    def __init__(self, max_workers: int = 10):
        self.tasks = {}
        self.running = False
        self.stop_event = Event()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def add_task(self, name: str, interval: str, task: Callable, **kwargs: Any) -> None:
        if name in self.tasks:
            logger.warning(f"Task '{name}' already exists. Updating it.")

        scheduled_task = self._schedule_task(interval, name, task, **kwargs)
        self.tasks[name] = {
            "interval": interval,
            "task": task,
            "kwargs": kwargs,
            "scheduled_task": scheduled_task,
        }
        logger.info(f"Task '{name}' added with interval {interval}")

    def _schedule_task(
        self, interval: str, name: str, task: Callable, **kwargs: Any
    ) -> schedule.Job:
        job = None
        if interval.endswith("s"):
            job = schedule.every(int(interval[:-1])).seconds
        elif interval.endswith("m"):
            job = schedule.every(int(interval[:-1])).minutes
        elif interval.endswith("h"):
            job = schedule.every(int(interval[:-1])).hours
        elif interval.endswith("d"):
            job = schedule.every(int(interval[:-1])).days
        else:
            raise ValueError(f"Invalid interval format: {interval}")

        return job.do(self._run_task, name, task, **kwargs)

    def _run_task(self, name: str, task: Callable, **kwargs: Any) -> None:
        try:
            logger.info(f"Starting task: {name}")
            self.executor.submit(task, **kwargs)
        except Exception as e:
            logger.error(f"Error running task {name}: {str(e)}")

    def run(self) -> None:
        self.running = True
        self.stop_event.clear()
        thread = Thread(target=self._run_continuously)
        thread.start()
        logger.info("Scheduler started")

    def _run_continuously(self) -> None:
        while self.running:
            schedule.run_pending()
            time.sleep(1)
            if self.stop_event.is_set():
                break

    def stop(self) -> None:
        self.running = False
        self.stop_event.set()
        self.executor.shutdown(wait=True)
        logger.info("Scheduler stopped")
