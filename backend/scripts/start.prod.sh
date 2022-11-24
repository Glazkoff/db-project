#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset
set -o xtrace

poetry run gunicorn --bind 0.0.0.0:5000 manage:app