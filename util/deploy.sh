#!/bin/bash
#ssh creds

readonly project_name=
readonly webroot=
readonly supervisor_service_name=

readonly repo=${webroot}/${project_name}
readonly venv=${webroot}/venv

echo fetch src to ${repo}
cd ${repo}
git fetch origin master
git checkout origin/master

echo build statics
cd ${repo}/front
npm run build

echo run db updates
echo ...

echo reload wsgi service
sudo supervisorctl restart ${supervisor_service_name}
