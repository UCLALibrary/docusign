# Docusign and Jira Tools
UCLA Library tools for working with Docusign and Jira

# Development Environment

Requires relatively current versions of `docker`(version 25+) and `docker compose` (version 2+).

## Build (first time) / rebuild (as needed)

`docker compose build`

This builds a Docker image, `docusign-python:latest`, which can be used for developing, testing, and running code.

## Dev container

This project comes with a basic dev container definition, in `.devcontainer/devcontainer.json`. It's known to work with VS Code,
and may work with other IDEs like PyCharm.  For VS Code, it also installs the Python, Black (formatter), and Flake8 (linter)
extensions.

The project's directory is available within the container at `/home/docusign/app`.

### Rebuilding the dev container

VS Code builds its own container from the base image. This container may not always get rebuilt when the base image is rebuilt 
(e.g., if packages are changed via `requirements.txt`).

If needed, rebuild the dev container by:
1. Close VS Code and wait several seconds for the dev container to shut down (check via `docker ps`).
2. Delete the dev container.
   1. `docker images | grep vsc-docusign` # vsc-docusign-LONG_HEX_STRING-uid
   2. `docker image rm -f vsc-docusign-LONG_HEX_STRING-uid`
3. Start VS Code as usual.

## Running code

Running code from a VS Code terminal within the dev container should just work, e.g.: `python get_form_data.py` (or whatever the specific program is).

Otherwise, run a program via docker compose.  From the project directory:

`docker compose run python python get_form_data.py`

This starts up a container for the `python` service via `docker compose`, runs the given program, then shuts down the container.

### Secrets and other configuration

Docusign and Jira require various secrets, like API tokens, as well as configuration details, like server URLs.

Store this configration in a TOML file, named appropriately for each project or environment (details TBD...).  Ask a team member
for the appropriate configuration file and place it in the top-level directory of the project (same directory as `Dockerfile`).

The configuration file must be specified on the command line when running each program:

`python get_form_data.py --config NAME_OF_FILE`

Currently, the configuration file contains the following (see comments in file for documentation):
* `authorization_server`
* `client_id`
* `impersonated_user_id`
* `private_key`
