"""Invoke tasks for FastAPI Basic Example."""

from invoke import task


@task(aliases=["i"])
def install(ctx):
    """Install dependencies using uv."""
    ctx.run("uv sync --dev")


@task(aliases=["r"])
def run(ctx, host="0.0.0.0", port=8000):
    """Run the FastAPI application."""
    ctx.run(
        f"uvicorn src.fastapi_basic_example.main:app --host {host} "
        f"--port {port} --reload"
    )


@task(aliases=["f"])
def format(ctx):
    """Format code with ruff."""
    ctx.run("uv run ruff format .")


@task(pre=[format], aliases=["l"])
def lint(ctx, fix=False):
    """Run ruff linter."""
    fix_flag = "--fix" if fix else ""
    ctx.run(f"uv run ruff check {fix_flag} .")


@task(aliases=["k"])
def format_check(ctx):
    """Check code formatting with ruff."""
    ctx.run("uv run ruff format --check .")


@task(pre=[lint], aliases=["t"])
def test(ctx, verbose=False, markers=None, coverage=True, fail_under=80):
    """Run tests with pytest."""
    flags = []
    if verbose:
        flags.append("-v")
    if markers:
        flags.append(f"-m {markers}")
    if coverage:
        flags.extend(
            [
                "--cov=src/fastapi_basic_example",
                "--cov-report=term-missing",
                "--cov-report=html:htmlcov",
                f"--cov-fail-under={fail_under}",
            ]
        )

    flags_str = " ".join(flags)
    ctx.run(f"uv run pytest {flags_str}")


@task(aliases=["u"])
def test_unit(ctx):
    """Run only unit tests."""
    test(ctx, markers="unit")


@task(aliases=["n"])
def test_integration(ctx):
    """Run only integration tests."""
    test(ctx, markers="integration")


@task(aliases=["e"])
def test_e2e(ctx):
    """Run only end-to-end tests."""
    test(ctx, markers="e2e")


@task(aliases=["v"])
def coverage_report(ctx):
    """Generate coverage report."""
    ctx.run("uv run coverage report")
    ctx.run("uv run coverage html")
    print("📊 Coverage report generated in htmlcov/index.html")


@task(aliases=["x"])
def clean(ctx):
    """Clean up build artifacts and cache files."""
    print("🧹 Cleaning up build artifacts and cache files...")

    # Remove Python cache files and directories
    ctx.run("find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true")
    ctx.run("find . -type f -name '*.pyc' -delete 2>/dev/null || true")
    ctx.run("find . -type f -name '*.pyo' -delete 2>/dev/null || true")

    # Remove test cache
    ctx.run("rm -rf .pytest_cache")

    # Remove linter cache
    ctx.run("rm -rf .ruff_cache")

    # Remove build artifacts
    ctx.run("rm -rf build/")
    ctx.run("rm -rf dist/")
    ctx.run("rm -rf *.egg-info/")

    # Remove coverage files
    ctx.run("rm -rf .coverage")
    ctx.run("rm -rf htmlcov/")
    ctx.run("rm -rf .coverage.*")

    # Remove mypy cache
    ctx.run("rm -rf .mypy_cache")

    print("✅ Cleanup complete!")


@task(pre=[lint], aliases=["c"])
def check(ctx):
    """Run all checks (format and lint)."""
    print("✅ All checks passed!")


@task(aliases=["d"])
def dev(ctx, log_level="info", json_logging=False):
    """Start development server."""
    env_vars = []
    if json_logging:
        env_vars.append("JSON_LOGGING=true")
    env_vars.append(f"LOG_LEVEL={log_level}")

    env_prefix = " ".join(env_vars) + " " if env_vars else ""

    ctx.run(
        f"{env_prefix}uvicorn src.fastapi_basic_example.main:app --reload "
        "--host 0.0.0.0 --port 8000"
    )


@task(pre=[check], aliases=["b"])
def build(ctx):
    """Build the project."""
    ctx.run("uv build")


@task(pre=[check], aliases=["o"])
def build_docker(ctx, tag="fastapi-basic-example:latest", no_cache=False):
    """Build Docker image."""
    cache_flag = "--no-cache" if no_cache else ""
    ctx.run(f"docker build {cache_flag} -t {tag} .")


@task(aliases=["a"])
def build_all(ctx):
    """Build both Python package and Docker image."""
    print("🏗️  Building Python package...")
    build(ctx)
    print("🐳 Building Docker image...")
    build_docker(ctx)
