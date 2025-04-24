# FDK Reports BFF

This application provides an API for the reports pages on [data.norge.no](https://data.norge.no/reports).

For a broader understanding of the system’s context, refer to
the [architecture documentation](https://github.com/Informasjonsforvaltning/architecture-documentation) wiki. For more
specific context on this application, see the **Portal** subsystem section.

## Getting Started

These instructions will give you a copy of the project up and running on your local machine for development and testing
purposes.

### Prerequisites

Ensure you have the following installed:

- Python
- [poetry](https://python-poetry.org/)
- [nox](https://nox.thea.codes/en/stable/)
- [nox-poetry](https://pypi.org/project/nox-poetry/)

### Running locally

Clone the repository

```sh
git clone https://github.com/Informasjonsforvaltning/fdk-reports-bff.git
cd fdk-reports-bff
```

Install packages
```sh
poetry install
```

Start the application with CLI

```sh
docker-compose up -d
poetry shell
gunicorn --chdir src "fdk_organization_bff:create_app" --config=src/fdk_organization_bff/gunicorn_config.py --worker-class aiohttp.GunicornWebWorker
```

or start the application with Docker Compose

```sh
docker compose up -d
```

### API Documentation (OpenAPI)

The API documentation is available at ```fdk-report-bff.yaml```.

### Running tests

#### with nox sessions

Run default sessions:

```sh
nox
```

Run specific session:

```sh
nox -s unit_tests
nox -s contract_tests
```

#### outside nox sessions

```sh
poetry run pytest
```
