import pytest  # type: ignore
from tests.conftest import query


@pytest.mark.parametrize(
    "filters, n",
    (
        ("securityDbid: 1", 2),
        ("year: 2000", 1),
        ("yearGte: 2000", 2),
        ("and: [{year: 2000}, {year: 2001}]", 0),
        ("or: [{year: 2000}, {year: 2001}]", 2),
    ),
)
def test_query_all_balances_with_filters(filters, n):
    querystr = "query { allBalances(filters: {%s}) { edges { node { dbid }}}}" % filters
    resp = query(querystr)
    print(resp.content)
    assert resp.ok

    edges = resp.json()["data"]["allBalances"]["edges"]
    assert len(edges) == n, "expected amount of edges"


@pytest.mark.parametrize(
    "args",
    (
        'dim: "", year: 1999, securityIsin: "isin_a"',
        'currency: "EUR", year: 1999, securityIsin: "isin_a"',
        'currency: "EUR", dim: "", securityIsin: "isin_a"',
        'currency: "ASD", dim: "", year: 1999, securityIsin: "isin_a"',
        'currency: "EUR", dim: "Ö", year: 1999, securityIsin: "isin_a"',
        'currency: "EUR", dim: "", year: "asd", securityIsin: "isin_a"',
        'currency: "EUR", dim: "", year: 1999, securityIsin: "isin_xxx"',
    ),
)
def test_create_balance_missing_or_wrong_input(args):
    querystr = "mutation { createBalance(%s) { node { dbid }}}" % args
    assert not query(querystr).ok


def test_successful_create_and_update_balance():
    args = 'currency: "EUR", dim: "M", year: 1000, securityIsin: "isin_a"'
    querystr = "mutation { createBalance(%s) { node { dbid }}}" % args
    resp = query(querystr)
    print(resp.content)
    assert resp.ok

    querystr = "mutation { createBalance(%s) { node { dbid }}}" % f"{args} total: 100"
    resp = query(querystr)
    print(resp.content)
    assert resp.ok

    querystr = """
        query {
            allSecurities(filters: {isin: "isin_a"}) {
                edges { node { balances { edges {
                    node { total, year }
                }}}}
            }
        }
    """
    resp = query(querystr)
    print(resp.content)
    sec = resp.json()["data"]["allSecurities"]["edges"][0]["node"]
    edges = sec["balances"]["edges"]
    hits = [d["node"]["total"] for d in edges if d["node"]["year"] == 1000]
    assert hits[0] == 100, "value was updated"
