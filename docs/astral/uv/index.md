# uv

## Install Python`

Install the latest available Python version

```shell
uv python install
```

Install a specific python version:

```shell
uv python install 3.12
```

Install multiple Python versions:

```shell
uv python install 3.11 3.12
```

Upgrade Python version

```shell
uv python upgrade 3.12
```

This upgrades a Python version to the latest supported patch release.





Reinstalling Python
:
```shell
uv python install --reinstall
```

Note: This will reinstall all previously installed Python versions. Improvements are constantly being added to the Python distributions so reinstalling may resolve bugs even if the Python version does not change.


View Python installations

```shell
uv python list
```

## Setting up an existing project

If a project already has a pyproject.toml file

```shell
uv python install 3.13
uv python pin 3.13
uv sync
```

This gives you an explicit pythgon version, a reproducible env (uv.lock)

## Update pyproject.toml build backend

Replace whatever you currently have under `[build-system]` to:

```toml
[build-system]
requires = ["uv_build>=0.9.18,<0.10.0"]
build-backend = "uv_build"
```

Astral explicitly recommends an upper bound to avoid surprise breaking changes as uv_build evolves.

By default, uv_build expects a src/ layout like `src/<package_name>/__init__.py`.

## Build and validate using the uv-build backend

```shell
uv build
```

uv will use the bundled backend if compatible; otherwise it will pull a compatible uv_build to build.

Other build frontends will use the uv_build package according to your [build-system].requires constraints.
