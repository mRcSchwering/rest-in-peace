# Tests

Upon starting the app ([start.sh](../start.sh)) a single alembic test will always check
that database and code are in sync.
I could treat this test differently and put it somewhere else.
Currently both the actual _app_ and the testing service _test_ run with the same image
so it doesnt really matter where that one test lives.

Test:

```
pytest tests/
```
