#!/bin/bash
#ssh creds

readonly project_name=
readonly webroot=

readonly repo=${webroot}/${project_name}
readonly venv=${webroot}/venv
readonly supervisor_gunicorn_service_name=gunicorn_${project_name}

echo fetch src to ${repo}
cd ${repo}
git fetch origin master
git checkout origin/master

echo udpate db and statics
. ${venv}/bin/activate
python manage.py showmigrations
python manage.py migrate --noinput
python manage.py collectstatic --noinput
deactivate

echo reload gunicorn
sudo supervisorctl restart ${supervisor_gunicorn_service_name}
