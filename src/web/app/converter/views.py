import logging

from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import DeleteView, FormMixin

from .forms import UploadFileForm
from .models import Doc
from .tasks import convert_to_pdf

logger = logging.getLogger(__file__)


class SafePaginator(Paginator):
    """Если число страниц больше числа документов, то вернет последнюю страницу"""

    def validate_number(self, number):
        try:
            number = int(number)
        except ValueError:
            number = 1
        return min(number, self.num_pages)


class Files(FormMixin, ListView):
    model = Doc
    template_name = "converter/files.html"
    context_object_name = "files"
    paginate_by = 2
    form_class = UploadFileForm
    success_url = reverse_lazy("converter:index")
    ordering = ["-uploaded_at"]
    allow_empty = True
    paginator_class = SafePaginator

    def get_user_id(self):
        if self.request.user.is_authenticated:
            return self.request.user.id
        else:
            if not self.request.session or not self.request.session.session_key:
                self.request.session.save()
            return self.request.session.session_key

    def get_queryset(self):
        user_id = self.get_user_id()
        return Doc.objects.filter(owner=user_id).order_by("-uploaded_at")

    def post(self, request, *args, **kwargs):
        """Обработка POST при использовани FormMixin"""
        form = self.get_form()
        # form.errors = 'no error'
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        # сохраняем файл и делаем запись в базу
        file = form.cleaned_data["file"]
        user_id = self.get_user_id()
        logger.debug("user id: {0}".format(user_id))

        doc = Doc(file=file, title=file.name, owner=user_id)
        doc.save()
        task = convert_to_pdf.delay(doc.pk)
        logger.debug("got file {0} and create task {1}".format(doc.file.name, task))
        return super().form_valid(form)

    def form_invalid(self, form):
        self.object_list = self.get_queryset()
        return super().form_invalid(form)


class DeleteFile(DeleteView):
    model = Doc

    def get_success_url(self):
        page = self.request.POST.get("from_page", 1)
        return reverse_lazy("converter:index") + f"?page={page}"
