"""Google Tasks API helpers."""

from googleapiclient import discovery

from auth import get_credentials


def _service():
    return discovery.build("tasks", "v1", credentials=get_credentials())


def fetch_tasks() -> list[dict]:
    result = (
        _service()
        .tasks()
        .list(tasklist="@default", showCompleted=False, maxResults=30)
        .execute()
    )
    return result.get("items", [])


def create_task(title: str) -> None:
    _service().tasks().insert(tasklist="@default", body={"title": title}).execute()


def complete_task(task_id: str) -> None:
    _service().tasks().patch(
        tasklist="@default",
        task=task_id,
        body={"status": "completed"},
    ).execute()
