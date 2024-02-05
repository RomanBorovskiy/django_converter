from pathlib import Path

from celery import shared_task
from django.core.files import File

from .models import Doc, Settings
from .utils import ConvertError, convert_docx_to_pdf


@shared_task(bind=True, name="converter.pdf_convert")
def convert_to_pdf(self, doc_id):
    doc = Doc.objects.get(pk=doc_id)
    if not doc:
        return f"file {doc_id} not found"

    # делаем запись в базе о начале обработки
    doc.status = Doc.DocState.IN_WORK
    doc.save()

    try:
        # получаем полный путь до исходного файла
        # у celery должен доступ к MEDIA
        file_src = Path(str(doc.file.path))

        # временная директория - будет удалена после конвертации
        out_dir = Path(f"/tmp/{self.request.id}/")

        file_dsc = convert_docx_to_pdf(file_src, out_dir)
        file_src.unlink(missing_ok=True)
        doc.file = ""

    except ConvertError as error:
        doc.status = Doc.DocState.ERROR
        doc.info = str(error)
        doc.save()
        return str(error)

    # делаем запись в базе о конце обработки
    doc.status = Doc.DocState.CONVERTED
    doc.file = None

    with Path(file_dsc).open("rb") as f:
        doc.result_file.save(Path(file_dsc).name, File(f))

    doc.info = file_src
    doc.save()

    # удаляем временную директорию
    Path(file_dsc).unlink(missing_ok=True)
    out_dir.rmdir()

    return "ok"


@shared_task(name="converter.clear_by_ttl")
def clear_by_ttl():
    settings = Settings.load()

    if not settings.auto_remove:
        return "not enabled"
    ttl = settings.file_ttl
    count = Doc.delete_by_ttl(ttl * 60)
    return f"Ok, ttl={ttl}, count={count}"
