web: python manage.py collectstatic --noinput && python manage.py migrate --noinput && gunicorn booking_platform.wsgi --bind 0.0.0.0:$PORT --log-file -
