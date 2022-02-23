#!/usr/bin/env bash
set -e

FILES=$(git ls-files | egrep '\.py$')
venv/bin/black --check --diff $FILES
venv/bin/isort --check --diff $FILES 
venv/bin/mypy $FILES
