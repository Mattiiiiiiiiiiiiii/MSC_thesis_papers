
# Setup

- `pipx install papis`
- run `git submodule init && git submodule update` to clone `paperlib`
- `pipx inject papis --editable paperlib --include-apps`
- Create `~/.config/papis/config` with the [thesis] and [include] lines shown at the top of `.papis.config`.
- `pre-commit install --hook-type pre-commit --hook-type commit-msg`

