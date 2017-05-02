#!/bin/bash
cd /var/www/beedo && git stash save --keep-index && git stash drop
cd /var/www/beedo && find . -name \*.pyc -delete
cd /var/www/beedo && git pull origin master
supervisorctl restart beedo