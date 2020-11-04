from tests.conftest import query


def superuser_login():
    querystr = """mutation {
    login(input: { email: "super.susi@gmail.com", password: "asdf3" }) {
        status
        error
        token
    }}"""
    res = query(querystr)
    data = res.json()["data"]
    assert data["login"]["status"] is True
    return data["login"]["token"]


def test_loing_and_query_me_with_or_without_access_token():
    res = query("""query {me {name, email}}""")
    data = res.json()["data"]
    assert data == {"me": None}

    token = superuser_login()
    res = query("""query {me {name, email}}""", jwt=token)
    data = res.json()["data"]
    assert data["me"]["email"] == "super.susi@gmail.com"


def test_superuser_fields_are_only_shown_to_superuser():
    res = query("""query {users {name, email}}""")
    users = res.json()["data"]["users"]
    assert len(users) > 0
    assert set(d["email"] for d in users) == {None}
    assert len(set(d["name"] for d in users)) == len(users)

    token = superuser_login()
    res = query("""query {users {name, email}}""", jwt=token)
    users = res.json()["data"]["users"]
    assert len(users) > 0
    assert len(set(d["email"] for d in users)) == len(users)
    assert len(set(d["name"] for d in users)) == len(users)

