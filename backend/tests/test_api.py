"""
Backend API integration tests.
Run against a live docker-compose stack: pytest backend/tests/test_api.py -v
"""
import requests
import time

BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api"


def test_health_endpoint():
    r = requests.get(f"{BASE_URL}/health", timeout=10)
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert "timestamp" in data


def test_create_task():
    payload = {"title": f"Test task {int(time.time())}", "description": "A test task"}
    r = requests.post(f"{API_URL}/tasks", json=payload, timeout=10)
    assert r.status_code == 201
    data = r.json()
    assert data["title"] == payload["title"]
    assert data["description"] == payload["description"]
    assert data["is_active"] is True
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_create_task_no_title():
    r = requests.post(f"{API_URL}/tasks", json={"description": "no title"}, timeout=10)
    assert r.status_code == 400
    assert "error" in r.json()


def test_list_tasks():
    r = requests.get(f"{API_URL}/tasks", timeout=10)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)


def test_update_task():
    # Create a task first
    payload = {"title": f"Update test {int(time.time())}"}
    create_r = requests.post(f"{API_URL}/tasks", json=payload, timeout=10)
    task_id = create_r.json()["id"]

    # Update it
    update_payload = {"title": "Updated title", "is_active": False}
    r = requests.put(f"{API_URL}/tasks/{task_id}", json=update_payload, timeout=10)
    assert r.status_code == 200
    data = r.json()
    assert data["title"] == "Updated title"
    assert data["is_active"] is False


def test_delete_task():
    # Create a task first
    payload = {"title": f"Delete test {int(time.time())}"}
    create_r = requests.post(f"{API_URL}/tasks", json=payload, timeout=10)
    task_id = create_r.json()["id"]

    # Delete it
    r = requests.delete(f"{API_URL}/tasks/{task_id}", timeout=10)
    assert r.status_code == 204


def test_search_tasks():
    # Create a task with a unique keyword
    keyword = f"searchable_{int(time.time())}"
    requests.post(f"{API_URL}/tasks", json={"title": keyword}, timeout=10)

    # Search for it
    r = requests.get(f"{API_URL}/search", params={"q": keyword}, timeout=10)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert any(t["title"] == keyword for t in data)


def test_get_stats():
    r = requests.get(f"{API_URL}/stats", timeout=10)
    assert r.status_code == 200
    data = r.json()
    assert "total" in data
    assert "active" in data
    assert "done" in data
    assert isinstance(data["total"], int)


def test_update_nonexistent_task():
    r = requests.put(f"{API_URL}/tasks/99999", json={"title": "nope"}, timeout=10)
    assert r.status_code == 404
