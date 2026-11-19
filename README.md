
# Setup

- `pipx install papis`
- `pipx inject papis --editable tools/paperlib --include-apps`
- Create `~/.config/papis/config` with the [thesis] and [include] lines shown at the top of `.papis.config`.
- `pre-commit install --hook-type pre-commit --hook-type commit-msg`

