import datetime
import logging

from django.db import models
from django.utils.timezone import now

from core.settings import FILES_LOADED_FOLDER, PDF_FILE_FOLDER
from core.single_model import SingletonModel

logger = logging.getLogger(__file__)


class Doc(models.Model):
    class Meta:
        verbose_name = "Файл"
        verbose_name_plural = "Файлы"

    class DocState(models.IntegerChoices):
        LOADED = 0, "LOADED"
        IN_WORK = 1, "IN WORK"
        CONVERTED = 2, "CONVERTED"
        ERROR = 3, "ERROR"

    file = models.FileField(upload_to=FILES_LOADED_FOLDER)
    title = models.CharField(max_length=200, blank=True)
    owner = models.CharField(max_length=50, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=DocState.choices, default=DocState.LOADED)
    info = models.CharField(max_length=300, blank=True)
    result_file = models.FileField(blank=True, upload_to=PDF_FILE_FOLDER)

    def delete(self, *args, **kwargs):
        # До удаления записи получаем необходимую информацию
        if self.file:
            storage, path = self.file.storage, self.file.path
            # Потом удаляем сам файл
            storage.delete(path)
            logger.debug("delete file {0}".format(path))

        if self.result_file:
            storage, path = self.result_file.storage, self.result_file.path
            storage.delete(path)
            logger.debug("delete file {0}".format(path))

        super().delete(*args, **kwargs)

    def __str__(self):
        return self.title

    @classmethod
    def delete_by_ttl(cls, ttl: int):
        # удаляем записи старше ttl
        datetime_max_value = now() - datetime.timedelta(seconds=ttl)
        files_for_delete = cls.objects.filter(uploaded_at__lt=datetime_max_value)
        count = files_for_delete.count()
        files_for_delete.delete()
        logger.debug("delete converter by ttl, count={0}".format(count))
        return count


class Settings(SingletonModel):
    file_ttl = models.IntegerField(default=14 * 24 * 60, verbose_name="Время жизни файлов (мин)")
    auto_remove = models.BooleanField(default=False, verbose_name="Включить автоудаление")

    class Meta:
        verbose_name = "Настройки"
        verbose_name_plural = "Настройки"

    def __str__(self):
        return "Установки автоудаления"
