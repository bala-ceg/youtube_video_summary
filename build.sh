#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Installing the latest version of poetry..."

pip install poetry==1.2.0

rm poetry.lock

poetry lock

python -m poetry install

/opt/render/project/src/.venv/bin/python -m pip install --upgrade pip
python manage.py migrate
