import time


def dummy_generation_task(project_name: str) -> dict:
    """
    Placeholder for the real AI generation task (built in the next phase).
    Simulates a slow operation so we can verify the queue + worker mechanism
    works correctly before wiring in actual AI logic.
    """
    time.sleep(5)  # simulate slow AI generation
    return {
        "status": "completed",
        "project_name": project_name,
        "result": "fake_midi_data",
    }