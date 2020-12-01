from django.urls import path

from .views import (
    BookConfirmImportView,
    BookImportView,
    BookListView,
)

urlpatterns = [
    path('', BookListView.as_view(), name='list'),
    path('confirm/', BookConfirmImportView.as_view(), name='import_confirm'),
    path('import/', BookImportView.as_view(), name='import'),
]