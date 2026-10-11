"""Scheduled job wiring, the equivalent of Spring's @Scheduled + ShedLock."""

from apscheduler.schedulers.background import BackgroundScheduler


def run_task_with_lock(lock, name, owner, task, lock_for_seconds=30) -> bool:
    """Run a task only if the distributed lock can be acquired.

    The lock is always released in a finally block, even when the task raises,
    so a failed run does not block the next scheduled run.
    """
    if not lock.acquire(name, owner, lock_for_seconds):
        return False
    try:
        task()
    finally:
        lock.release(name, owner)
    return True


def create_scheduler(
    lock,
    task,
    owner="node-1",
    name="daily-invoice",
    hour=9,
    minute=0,
):
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        run_task_with_lock,
        "cron",
        hour=hour,
        minute=minute,
        args=[lock, name, owner, task],
        name=name,
    )
    return scheduler
