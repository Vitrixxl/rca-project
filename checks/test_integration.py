"""
End-to-end integration tests.
Run against a live docker-compose stack: pytest checks/test_integration.py -v
"""
import requests
import time
import concurrent.futures

BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api"


def test_full_crud_flow():
    # Create
    title = f"crud_test_{int(time.time())}"
    r = requests.post(f"{API_URL}/tasks", json={"title": title, "description": "e2e test"}, timeout=10)
    assert r.status_code == 201
    task = r.json()
    task_id = task["id"]
    assert task["title"] == title
    assert task["is_active"] is True

    # Read
    r = requests.get(f"{API_URL}/tasks", timeout=10)
    assert r.status_code == 200
    assert any(t["id"] == task_id for t in r.json())

    # Update
    r = requests.put(f"{API_URL}/tasks/{task_id}", json={"title": "updated", "is_active": False}, timeout=10)
    assert r.status_code == 200
    assert r.json()["title"] == "updated"
    assert r.json()["is_active"] is False

    # Delete
    r = requests.delete(f"{API_URL}/tasks/{task_id}", timeout=10)
    assert r.status_code == 204

    # Verify deleted
    r = requests.get(f"{API_URL}/tasks", timeout=10)
    assert not any(t["id"] == task_id for t in r.json())


def test_search_after_create():
    keyword = f"searchme_{int(time.time())}"
    requests.post(f"{API_URL}/tasks", json={"title": keyword}, timeout=10)
    time.sleep(0.5)

    r = requests.get(f"{API_URL}/search", params={"q": keyword}, timeout=10)
    assert r.status_code == 200
    results = r.json()
    assert any(t["title"] == keyword for t in results)


def test_stats_after_operations():
    # Get initial stats
    r = requests.get(f"{API_URL}/stats", timeout=10)
    initial = r.json()
    initial_total = initial["total"]
    initial_active = initial["active"]

    # Create a task
    title = f"stats_test_{int(time.time())}"
    requests.post(f"{API_URL}/tasks", json={"title": title}, timeout=10)

    # Stats should update
    r = requests.get(f"{API_URL}/stats", timeout=10)
    after_create = r.json()
    assert after_create["total"] == initial_total + 1
    assert after_create["active"] == initial_active + 1


def test_filter_active_done():
    # Create an active task
    title_active = f"active_{int(time.time())}"
    r = requests.post(f"{API_URL}/tasks", json={"title": title_active}, timeout=10)
    active_id = r.json()["id"]

    # Create and mark a task as done
    title_done = f"done_{int(time.time())}"
    r = requests.post(f"{API_URL}/tasks", json={"title": title_done}, timeout=10)
    done_id = r.json()["id"]
    requests.put(f"{API_URL}/tasks/{done_id}", json={"is_active": False}, timeout=10)

    # Filter active
    r = requests.get(f"{API_URL}/tasks", params={"status": "active"}, timeout=10)
    active_tasks = r.json()
    assert any(t["id"] == active_id for t in active_tasks)
    assert not any(t["id"] == done_id for t in active_tasks)

    # Filter done
    r = requests.get(f"{API_URL}/tasks", params={"status": "done"}, timeout=10)
    done_tasks = r.json()
    assert any(t["id"] == done_id for t in done_tasks)
    assert not any(t["id"] == active_id for t in done_tasks)


def test_concurrent_creates():
    base_title = f"concurrent_{int(time.time())}"
    titles = [f"{base_title}_{i}" for i in range(5)]

    def create_task(title):
        return requests.post(f"{API_URL}/tasks", json={"title": title}, timeout=10)

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(create_task, t) for t in titles]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    assert all(r.status_code == 201 for r in results)

    # Verify all tasks exist
    r = requests.get(f"{API_URL}/tasks", timeout=10)
    all_titles = [t["title"] for t in r.json()]
    for title in titles:
        assert title in all_titles
