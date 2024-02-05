worker-run:
			celery -A core worker --loglevel=debug

beat-run:
			celery -A core beat

init:
		python manage.py makemigrations
		python manage.py migrate

run:
		python manage.py runserver

super:
		python manage.py createsuperuser


