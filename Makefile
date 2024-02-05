docker-run:
		docker compose up -d --build

docker-stop:
		docker compose down

docker-init:
	docker exec -it django-celery-web-1 python manage.py makemigrations
	docker exec -it django-celery-web-1 python manage.py migrate
	docker exec -it django-celery-web-1 python manage.py createsuperuser

redis-run:
	docker compose up redis -d
