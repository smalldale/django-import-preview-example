from custom_import_export.views import ImportView, ConfirmImportView

from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic

from .models import Book
from .resources import BookResource

# Create your views here.


class BookListView(generic.ListView):
    model = Book
    template_name = 'book/list.html'

class BookImportView(ImportView):
    """
    ImportView specific for model Book and resource BookResource
    """
    import_template_name = 'book/import.html'
    #: resource class
    resource_class = BookResource
    #: model to be imported
    model = Book


class BookConfirmImportView(ConfirmImportView):
    """
    ConfirmImportView specific for model Period and resource PeriodResource
    """
    import_template_name = 'book/import.html'
    #: resource class
    resource_class = BookResource
    #: model to be imported
    model = Book
    success_url = reverse_lazy('list')
    