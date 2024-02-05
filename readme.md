# Конвертер файлов в PDF
Приложение Django, в воркере Celery запускается экземпляр libreoffice и выполняется конвертация (ничего проще не придумал)
Сделано просто так, на кошках потренироваться  
Файлы сначала загружаются через веб-форму в media/files_loaded, потом pdf сохраняется в media/pdf_convert  
Списки файлов хранятся для каждого пользователя отдельно (если пользователь авторизован - по user.id, если не авторизован - по session.session_key)
Периодическая задача celery beat стирает старые файлы (по умолчанию стоит 14 дней)  
В админке есть настройки периодической задачи  (http://127.0.0.1:8000/admin)  
Для мониторинга запускается Flower, доступен по http://127.0.0.1:5555
Веб-форма обновляется автоматически раз в 5сек, пусть и выглядит страшно внутри (REST так и просится)  
База sqlite, для прода лучше что-то посолиднее, но на малых нагрузках должно хватить (корпоративный портал например)  
Ну и ясно дело - нужен nginx на все это, в таком виде с django наружу - только поиграться

# Запуск

## Докер
- `.env.example` переименовать в `.env`  
- `make docker-run` - собирает и запускает контейнеры  
- `make docker-init` - выполняет миграции и создает суперпользователя (чтобы в админку сходить)
- `make docker-stop` - останавливает контейнеры

## Локальный запуск
При локальном запуске сервер Redis все равно нужен, из корневой папки запускаем `make redis-run`
- идем в `src\web`
- устанавливаем зависимости из `requirements.txt` (`pip install -r requirements.txt`)
- `make init` - применяем миграции
- `make super` - создаем суперпользователя (если нужен)
- `make run` - запускаем локальный сервер django
- `make worker-run` - запускает воркер celery
- `make beat-run` - запускает планировщик celery



