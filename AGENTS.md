# Pz Server

This repository contains the PzServer web application and API for managing scientific data products for the LSST project. The Python package `pzserver` lives in a separate repository and consumes this API. Check the Python client when changing API routes, authentication, or response formats.

Develop and test Pz Server as an integrated project, including the web application, orchestration, pipelines, and Python client as relevant to the task. Before editing a component, identify its owning Git repository and follow its applicable `AGENTS.md`, including when a separate checkout is nested under the project directory.

For changes spanning repositories, use a separate branch, commits, and pull request in each affected repository. Cross-link related PRs and document any required merge or deployment order. Run the relevant component checks and verify the integrated workflow when changes cross repository boundaries.

## Repository map

- `backend/` contains the Django and Django REST Framework application. API routes and settings live in `backend/pzserver/`. Domain models, views, migrations, and tests live under `backend/core/`.
- `frontend/` contains the Next.js web application. Pages live in `frontend/pages/`, shared UI in `frontend/components/`, and authentication state in `frontend/contexts/`. Reuse existing Material UI components and theme conventions when changing the interface.
- `orchestration/` is a Git submodule containing the orchestration service. Its backend lives in `orchestration/backend/`. See `orchestration/README.md` for setup and follow the orchestration repository's instructions when editing it.
- `orchestration/pipelines/` contains pipeline implementations and configuration, including `training_set_maker/`, `combine_redshift_dedup/`, and `hello_world/`. Changes here belong to the orchestration repository.
- The local application stack uses Docker Compose, PostgreSQL, RabbitMQ, Celery, and Nginx.
- Use `backend/requirements.txt` and `frontend/package.json` for dependency versions. See `README.md` for local setup and deployment.

## Local development and verification

- Run application commands, including Django management commands, migrations, and tests, through Docker Compose. Run repository inspection commands such as `git` and `rg` on the host.
- Never install Python project dependencies on the host or into a running container. Declare new backend dependencies in `backend/requirements.txt` and rebuild the image using the applicable Compose configuration.
- For backend dependency changes, run `docker compose build backend` and `docker compose up -d backend` to use the rebuilt image before testing.

- Follow the README to configure the local Compose environment. Start the stack with `docker compose up` once configured.
- With the backend service running, use `docker compose exec backend pytest`. For focused checks, append the relevant path under `core/test/`.
- For frontend build verification, use `docker compose run frontend yarn build`.
- See `.github/workflows/test.yml` for CI. When changing device authorization locking or concurrency, include the PostgreSQL checks configured there.

## Authentication

- The web frontend and Python client have distinct authentication flows. Browser approval in the OAuth Device Flow uses a Django session and CSRF protection. The Python client uses the issued access and refresh tokens.
- For changes to Device Flow, check browser approval, token renewal and revocation, and the existing web login paths. See `docs/device-authentication.md` for the workflow, test commands, and deployment steps.
- Use checked-in configuration templates for examples. Keep credentials, tokens, and user data out of source, documentation, and test output.
