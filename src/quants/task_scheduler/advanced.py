import time
from threading import Event, Thread
from typing import Any, Callable, Dict

import schedule

from ..utils.logger import get_logger
from .base import BaseTaskScheduler

logger = get_logger(__name__)


class AdvancedTaskScheduler(BaseTaskScheduler):
    def __init__(self):
        self.tasks = {}
        self.running = False
        self.stop_event = Event()

    def add_task(self, name: str, interval: str, task: Callable, **kwargs: Any) -> None:
        if name in self.tasks:
            logger.warning(f"Task '{name}' already exists. Updating it.")

        scheduled_task = self._schedule_task(interval, task, **kwargs)
        self.tasks[name] = {
            "interval": interval,
            "task": task,
            "kwargs": kwargs,
            "scheduled_task": scheduled_task,
        }
        logger.info(f"Task '{name}' added with interval {interval}")

    def remove_task(self, name: str) -> None:
        if name in self.tasks:
            schedule.cancel_job(self.tasks[name]["scheduled_task"])
            del self.tasks[name]
            logger.info(f"Task '{name}' removed")
        else:
            logger.warning(f"Task '{name}' not found")

    def get_tasks(self) -> Dict[str, Dict[str, Any]]:
        return {
            name: {k: v for k, v in task.items() if k != "scheduled_task"}
            for name, task in self.tasks.items()
        }

    def run(self) -> None:
        self.running = True
        self.stop_event.clear()
        thread = Thread(target=self._run_continuously)
        thread.start()
        logger.info("Scheduler started")
        logger.info(f"Scheduled tasks: {self.get_tasks()}")

    def stop(self) -> None:
        self.running = False
        self.stop_event.set()
        logger.info("Scheduler stopped")

    def _run_continuously(self) -> None:
        while self.running:
            schedule.run_pending()
            time.sleep(1)
            if self.stop_event.is_set():
                break

    def _schedule_task(self, interval: str, task: Callable, **kwargs: Any) -> schedule.Job:
        if interval.endswith("s"):
            return schedule.every(int(interval[:-1])).seconds.do(task, **kwargs)
        elif interval.endswith("m"):
            return schedule.every(int(interval[:-1])).minutes.do(task, **kwargs)
        elif interval.endswith("h"):
            return schedule.every(int(interval[:-1])).hours.do(task, **kwargs)
        elif interval.endswith("d"):
            return schedule.every(int(interval[:-1])).days.do(task, **kwargs)
        else:
            raise ValueError(f"Invalid interval format: {interval}")
