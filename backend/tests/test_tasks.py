"""Tests for the task board endpoints and /users."""


def approve(client, tasks, note_id=None):
    """Helper: save tasks the way the frontend does after review."""
    response = client.post("/tasks/bulk", json={"note_id": note_id, "tasks": tasks})
    assert response.status_code == 201, response.text
    return response.json()


def test_bulk_create_links_owners_by_name(client):
    saved = approve(
        client,
        [
            {"title": "Book the room", "owner_name": "Ada"},
            {"title": "Write the agenda", "owner_name": "ada"},  # same person
            {"title": "Order pizza"},  # nobody assigned
        ],
    )

    assert [task["status"] for task in saved] == ["todo", "todo", "todo"]
    assert saved[0]["owner"]["id"] == saved[1]["owner"]["id"]
    assert saved[0]["owner"]["name"] == "Ada"
    assert saved[2]["owner"] is None
    # Only one user was created for "Ada" and "ada".
    assert [user["name"] for user in client.get("/users").json()] == ["Ada"]


def test_bulk_create_with_unknown_note_saves_nothing(client):
    response = client.post(
        "/tasks/bulk", json={"note_id": 999, "tasks": [{"title": "Something"}]}
    )

    assert response.status_code == 404
    assert client.get("/tasks").json() == []


def test_list_orders_by_due_date_and_filters(client):
    approve(
        client,
        [
            {"title": "No date"},
            {"title": "Later", "due_date": "2026-12-01", "owner_name": "Ada"},
            {"title": "Sooner", "due_date": "2026-11-01"},
        ],
    )

    titles = [task["title"] for task in client.get("/tasks").json()]
    assert titles == ["Sooner", "Later", "No date"]

    ada_id = client.get("/users").json()[0]["id"]
    only_ada = client.get(f"/tasks?owner_id={ada_id}").json()
    assert [task["title"] for task in only_ada] == ["Later"]


def test_patch_changes_only_the_fields_sent(client):
    task = approve(client, [{"title": "Fix the bug", "owner_name": "Ada", "due_date": "2026-11-01"}])[0]

    response = client.patch(f"/tasks/{task['id']}", json={"status": "done"})

    assert response.status_code == 200
    updated = response.json()
    assert updated["status"] == "done"
    assert updated["title"] == "Fix the bug"
    assert updated["owner"]["name"] == "Ada"
    assert updated["due_date"] == "2026-11-01"
    assert client.get("/tasks?status=done").json()[0]["id"] == task["id"]


def test_patch_can_reassign_and_unassign(client):
    task = approve(client, [{"title": "Fix the bug", "owner_name": "Ada"}])[0]

    reassigned = client.patch(f"/tasks/{task['id']}", json={"owner_name": "Grace"}).json()
    assert reassigned["owner"]["name"] == "Grace"

    unassigned = client.patch(f"/tasks/{task['id']}", json={"owner_name": ""}).json()
    assert unassigned["owner"] is None


def test_patch_rejects_unknown_status(client):
    task = approve(client, [{"title": "Fix the bug"}])[0]

    response = client.patch(f"/tasks/{task['id']}", json={"status": "archived"})

    assert response.status_code == 422


def test_delete_task(client):
    task = approve(client, [{"title": "Temporary"}])[0]

    assert client.delete(f"/tasks/{task['id']}").status_code == 204
    assert client.get("/tasks").json() == []
    assert client.delete(f"/tasks/{task['id']}").status_code == 404


def test_create_single_task(client):
    response = client.post("/tasks", json={"title": "Added by hand", "owner_name": "Alan"})

    assert response.status_code == 201
    assert response.json()["owner"]["name"] == "Alan"


def test_users_reject_duplicate_email(client):
    first = client.post("/users", json={"name": "Ada", "email": "ada@example.com"})
    second = client.post("/users", json={"name": "Ada L", "email": "ada@example.com"})

    assert first.status_code == 201
    assert second.status_code == 409
