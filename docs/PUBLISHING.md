# Publishing meloda-mcp

This document is the operator-side checklist for cutting a release.

The project uses **PyPI Trusted Publishing** so no API token is stored in the
repository. Publishing is triggered by pushing a `v*` tag; the
`.github/workflows/publish.yml` workflow builds the sdist + wheel and uploads
them to PyPI on behalf of the project's pending publisher configuration.

---

## One-time setup (you only do this once for the project)

### 1. Create a PyPI account

1. Sign up at <https://pypi.org/account/register/>.
2. Enable 2FA. PyPI requires it for any project that uses Trusted Publishing.

### 2. Reserve the project name with Trusted Publishing

Because `meloda-mcp` does not exist on PyPI yet, you create a *pending*
publisher:

1. Open <https://pypi.org/manage/account/publishing/>.
2. Scroll to **Add a new pending publisher**.
3. Fill in:
   | Field            | Value                                |
   |------------------|--------------------------------------|
   | PyPI project name| `meloda-mcp`                         |
   | Owner            | `albertoabellagarcia`                |
   | Repository       | `meloda`                             |
   | Workflow         | `publish.yml`                        |
   | Environment      | *(leave blank)*                      |
4. Save.

After the first successful publish, this entry becomes a regular Trusted
Publisher attached to the now-existing project.

### 3. (Optional) Set up TestPyPI for rehearsals

Mirror the same flow at <https://test.pypi.org/manage/account/publishing/>.
Adjust `publish.yml` (or use a separate workflow) to publish to TestPyPI when
testing release tooling without burning real version numbers.

---

## Cutting a release

1. **Verify everything is green.** `pytest`, `ruff check`, and the GitHub
   Actions `tests` workflow on `main`.
2. **Bump the version.** Update both `pyproject.toml` and
   `meloda_mcp/__init__.py`. Commit on `main` with a message like
   `Bump to 0.x.y`.
3. **Update `CHANGELOG.md`.** Move the *Unreleased* section into a new
   dated entry, in the same commit.
4. **Tag and push.**

   ```bash
   git tag -a v0.x.y -m "meloda-mcp 0.x.y"
   git push origin v0.x.y
   ```

5. **Watch the workflow.** Go to *Actions → publish* in GitHub. The job builds
   `sdist` + `wheel` and publishes to PyPI via Trusted Publishing.
6. **Verify on PyPI.** `pip install meloda-mcp==0.x.y` should work. Check
   <https://pypi.org/project/meloda-mcp/>.
7. **Smoke-test the published artifact.**

   ```bash
   uvx --refresh meloda-mcp@0.x.y --help
   ```

8. **(Optional) Cut a GitHub Release** from the tag with the same notes you
   added to `CHANGELOG.md`.

---

## Alternative: publishing with an API token

If you would rather not use Trusted Publishing, replace the `publish` step in
`.github/workflows/publish.yml` with:

```yaml
- name: Publish to PyPI
  env:
    TWINE_USERNAME: __token__
    TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
  run: |
    pip install twine
    twine upload dist/*
```

…and store a project-scoped token in *Settings → Secrets → Actions* as
`PYPI_API_TOKEN`. Trusted Publishing is generally preferred (no secret to
rotate, scoped per workflow), but a token works.

---

## Smithery listing

After the first PyPI release:

1. Open <https://smithery.ai/new>.
2. Connect the GitHub repo `albertoabellagarcia/meloda`.
3. Smithery picks up `smithery.yaml` from the repo root.
4. Approve the auto-detected configuration. The listing is live within a few
   minutes.

The `smithery.yaml` shipped in this repo declares an `stdio` install via
`uvx meloda-mcp`, so users can add the server to their MCP-aware client with
a single click from Smithery.

---

## Anthropic Claude Connectors directory

Anthropic curates a directory of community MCP servers at
<https://www.claude.com/connectors>. Submission is by form; see
<https://support.claude.com/en/articles/12080973-getting-started-with-custom-connectors-using-remote-mcp>
for the most current process. Suggested copy is in
[`docs/SUBMISSION.md`](SUBMISSION.md).
