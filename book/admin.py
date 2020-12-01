from django.contrib import admin

from import_export.admin import ImportExportModelAdmin

from .models import Book

# Register your models here.

class BookAdmin(ImportExportModelAdmin):
    list_display = ('title', 'author', 'publication_date', 'pages', 'price',)
    search_fields = ('title', 'author', )

admin.site.register(Book, BookAdmin)
