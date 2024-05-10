#! /bin/bash
python manage.py collectstatic --noinput
# while !</dev/tcp/$POSTGRES_HOST/$POSTGRES_PORT; do sleep 1; done;
python manage.py migrate
python manage.py createsuperuser --noinput
chown uwsgi-user:uwsgi-user /var/log
cd sqlite_to_postgres
python load_data.py
cd ..
uwsgi --ini uwsgi.ini --pidfile uwsgi.pid
