#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset
set -o xtrace

poetry run python manage.py run -h 0.0.0.0 -p 5000 
