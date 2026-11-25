import pytest

INIT_DATA = 'user={"id":999,"first_name":"Tester"}'


@pytest.mark.asyncio
async def test_auth(client):
    r = await client.post("/auth/telegram", json={"init_data": INIT_DATA})
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
    assert data["user"]["telegram_id"] == 999


@pytest.mark.asyncio
async def test_courses_and_lessons(client):
    r = await client.post("/auth/telegram", json={"init_data": INIT_DATA})
    token = r.json()["access_token"]
    h = {"Authorization": f"Bearer {token}"}
    courses = await client.get("/courses", headers=h)
    assert courses.status_code == 200
    assert len(courses.json()) > 0
    # lessons of first course
    cid = courses.json()[0]["id"]
    lessons = await client.get(f"/courses/{cid}/lessons", headers=h)
    assert lessons.status_code == 200
    assert len(lessons.json()) > 0


@pytest.mark.asyncio
async def test_hearts(client):
    r = await client.post("/auth/telegram", json={"init_data": INIT_DATA})
    token = r.json()["access_token"]
    h = {"Authorization": f"Bearer {token}"}
    hearts = await client.get("/hearts", headers=h)
    assert hearts.status_code == 200
    assert hearts.json()["count"] == 5


@pytest.mark.asyncio
async def test_lesson_flow(client):
    r = await client.post("/auth/telegram", json={"init_data": INIT_DATA})
    token = r.json()["access_token"]
    h = {"Authorization": f"Bearer {token}"}
    courses = await client.get("/courses", headers=h)
    cid = courses.json()[0]["id"]
    lessons = await client.get(f"/courses/{cid}/lessons", headers=h)
    lid = lessons.json()[0]["id"]
    await client.post(f"/lessons/{lid}/start", headers=h)
    detail = await client.get(f"/lessons/{lid}", headers=h)
    assert detail.status_code == 200
    exs = detail.json()["exercises"]
    assert len(exs) > 0
    # submit first answer (wrong maybe)
    await client.post("/lessons/answer", headers=h, json={"exercise_id": exs[0]["id"], "answer": "wrong", "idempotency_key": "k1"})
    comp = await client.post("/lessons/complete", headers=h, json={"lesson_id": lid, "idempotency_key": "c1"})
    assert comp.status_code == 200
