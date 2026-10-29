# Project instructions

- Use synthetic exports. Treat connection settings and decoded passwords as secrets; never print or commit real credentials.
- Follow the repository's documented setup and pinned tooling. Validate code changes with:

```sh
uv run ruff format --check heidi_decode.py tests
uv run ruff check --select E9,F63,F7,F82 heidi_decode.py tests
uv run python -m unittest discover -s tests -v
```
