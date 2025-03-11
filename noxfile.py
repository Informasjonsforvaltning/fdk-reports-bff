"""Nox sessions."""

import nox
from nox.sessions import Session
import nox_poetry

nox.options.envdir = ".cache"
locations = "src", "test", "noxfile.py"
nox.options.sessions = (
    "lint",
    "mypy",
    "unit_tests",
    "contract_tests",
    "integration_tests",
)


@nox_poetry.session(python="3.13")
def unit_tests(session: Session) -> None:
    """Run the unit test suite."""
    args = session.posargs
    session.install(
        ".",
        "pytest",
        "requests-mock",
        "pytest-mock",
    )
    session.run(
        "pytest",
        "-m unit",
        "-rA",
        *args,
    )


@nox_poetry.session(python="3.13")
def tests(session: Session) -> None:
    """Run the integration test suite."""
    args = session.posargs or ["--cov"]
    session.install(
        ".",
        "coverage[toml]",
        "pytest",
        "pytest-cov",
        "pytest-docker",
        "requests-mock",
        "pytest-mock",
        "pytest-aiohttp",
    )
    session.run(
        "pytest",
        "-rA",
        *args,
        env={"API_KEY": "my-api-key"},
    )


@nox_poetry.session(python="3.13")
def contract_tests(session: Session) -> None:
    """Run the contract test suite."""
    args = session.posargs
    session.install(".", "pytest", "pytest-docker", "requests_mock", "pytest_mock")
    session.run(
        "pytest",
        "-m contract",
        "-rA",
        *args,
    )


@nox_poetry.session(python="3.13")
def integration_tests(session: Session) -> None:
    """Run the integration test suite."""
    args = session.posargs
    session.install(
        ".",
        "pytest",
        "pytest-docker",
        "requests-mock",
        "pytest-mock",
    )

    session.run(
        "pytest",
        "-m integration",
        "-rA",
        *args,
        env={"API_KEY": "my-api-key"},
    )


@nox_poetry.session(python="3.13")
def black(session: Session) -> None:
    """Run black code formatter."""
    args = session.posargs or locations
    session.install("black")
    session.run("black", *args)


@nox_poetry.session(python="3.13")
def lint(session: Session) -> None:
    """Lint using flake8."""
    args = session.posargs or locations
    session.install(
        "flake8",
        "flake8-annotations",
        "flake8-bandit",
        "flake8-black",
        "flake8-bugbear",
        "flake8-import-order",
        "pep8-naming",
    )
    session.run("flake8", *args)


@nox_poetry.session(python="3.13")
def coverage(session: Session) -> None:
    """Upload coverage data."""
    session.install("coverage[toml]")
    session.run("coverage", "xml", "--fail-under=0")


@nox_poetry.session(python="3.13")
def mypy(session: Session) -> None:
    """Type-check using mypy."""
    args = session.posargs or locations
    session.install("mypy")
    session.run("mypy", *args)
