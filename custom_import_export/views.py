from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.views import generic
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _
from django.utils.encoding import force_text

from import_export.forms import ConfirmImportForm
from import_export.signals import post_import
import import_export.admin

class ImportView(import_export.admin.ImportMixin, generic.View):
    """
    Subclassing of ImportMixin as a generic View implementing ImportForm
    """
    #: template for import view
    import_template_name = 'import.html'
    #: resource class
    resource_class = None
    #: model to be imported
    model = None

    def get_confirm_import_form(self):
        '''
        Get the form type used to display the results and confirm the upload.
        '''
        return ConfirmImportForm

    def get(self, request, *args, **kwargs):
        """
        Overriding the GET part of ImportMixin.import_action method to be used without site_admin
        """
        return self.post(request, *args, **kwargs)


    def post(self, request, *args, **kwargs):
        """
        Overriding the POST part of ImportMixin.import_action method to be used without site_admin
        """

        resource = self.get_import_resource_class()(**self.get_import_resource_kwargs(request, *args, **kwargs))

        context = self.get_import_context_data()

        import_formats = self.get_import_formats()
        form = self.get_import_form()(import_formats, request.POST or None, request.FILES or None)

        if request.POST and form.is_valid():
            input_format = import_formats[
                int(form.cleaned_data['input_format'])
            ]()
            import_file = form.cleaned_data['import_file']
            # first always write the uploaded file to disk as it may be a
            # memory file or else based on settings upload handlers
            tmp_storage = self.write_to_tmp_storage(import_file, input_format)

            # then read the file, using the proper format-specific mode
            # warning, big files may exceed memory
            try:
                data = tmp_storage.read(input_format.get_read_mode())
                if not input_format.is_binary() and self.from_encoding:
                    data = force_text(data, self.from_encoding)
                dataset = input_format.create_dataset(data)
            except UnicodeDecodeError as ex1:
                return HttpResponse(_(u"<h1>Imported file has a wrong encoding: %s</h1>" % ex1))
            except Exception as ex2:
                return HttpResponse(_(u"<h1>%s encountered while trying to read file: %s</h1>" % (type(ex2).__name__, import_file.name)))
            result = resource.import_data(dataset, dry_run=True, raise_errors=False, file_name=import_file.name, user=request.user)

            context['result'] = result

            if not result.has_errors() and not result.has_validation_errors():
                context['confirm_form'] = self.get_confirm_import_form()(initial={
                    'import_file_name': tmp_storage.name,
                    'original_file_name': import_file.name,
                    'input_format': form.cleaned_data['input_format'],
                })

        # context.update(self.admin_site.each_context(request))

        context['title'] = _("Import " + self.get_model_info()[1])
        context['form'] = form
        context['opts'] = self.model._meta
        context['fields'] = [f.column_name for f in resource.get_user_visible_fields()]

        # request.current_app = self.admin_site.name
        return TemplateResponse(request, [self.import_template_name], context)


class ConfirmImportView(import_export.admin.ImportMixin, generic.View):
    """
    Subclassing of ImportMixin as a generic View implementing ConfirmImportForm
    """
    #: template for import view
    import_template_name = 'import.html'
    #: resource class
    resource_class = None
    #: model to be imported
    model = None
    success_url = None

    def get_confirm_import_form(self):
        '''
        Get the form type used to display the results and confirm the upload.
        '''
        return ConfirmImportForm

    def post(self, request, *args, **kwargs):
        """
        Perform the actual import action (after the user has confirmed the import)
        """

        confirm_form = self.get_confirm_import_form()(request.POST)
        if confirm_form.is_valid():
            import_formats = self.get_import_formats()
            input_format = import_formats[
                int(confirm_form.cleaned_data['input_format'])
            ]()
            tmp_storage = self.get_tmp_storage_class()(name=confirm_form.cleaned_data['import_file_name'])
            data = tmp_storage.read(input_format.get_read_mode())
            if not input_format.is_binary() and self.from_encoding:
                data = force_text(data, self.from_encoding)
            dataset = input_format.create_dataset(data)

            result = self.process_dataset(dataset, confirm_form, request, *args, **kwargs)

            tmp_storage.remove()

            self.generate_log_entries(result, request)
            self.add_success_message(result, request)
            post_import.send(sender=None, model=self.model)

            if self.success_url:
                url = self.success_url
            else:
                url = reverse('{}:{}_index'.format(self.get_model_info()[0], self.get_model_info()[1]))
            return HttpResponseRedirect(url)
