# from django.core.paginator import Paginator
# from django.core.urlresolvers import reverse
from abc import ABCMeta, abstractmethod, abstractproperty
from django.http import HttpResponse
from django.template import loader, Context, RequestContext
import pdb


class FormError(Exception):
    pass


class View(HttpResponse):
    __metaclass__ = ABCMeta

    def __init__(self, request, *args, **kwargs):
        self.request     = request
        self.view_args   = args
        self.view_kwargs = kwargs
        if self.is_constant:
            super(View, self).__init__(self.content)
        else:
            try:
                self.process()
            except FormError:
                super(View, self).__init__(self.content)
            else:
                super(View, self).__init__()
                self.status_code = 302 # redirect
                self['Location'] = self.next_page

    @property
    def is_constant(self):
        return self.request.method == 'GET'

    @property
    def content(self):
        return self.template.render(self.context)

    @property
    def template(self):
        return loader.get_template(self.template_file)

    @abstractproperty
    def template_file(self):
        return None

    @property
    def context(self):
        if self.processors:
            return RequestContext(self.request, self.context_dict, processors=self.processors)
        else:
            return Context(self.context_dict)

    @abstractproperty
    def context_dict(self):
        return {}


# class AddView(View):
#     def context_form(self):
#         if self.is_constant():
#             return self.Form()
#         else:
#             return self.form # set by 'process_data'
# 
#     def process_data(self):
#         self.form = self.Form(
#                 self.request.POST,
#                 self.request.FILES,
#                 )
#         if self.form.is_valid():
#             self.form.save()
#         else:
#             raise FormError
# 
# 
# class EditView(View):
#     def context_form(self):
#         if self.is_constant():
#             return self.Form(instance=self.object())
#         else:
#             return self.form # set by 'process_data'
# 
#     def process_data(self):
#         self.form = self.Form(self.request.POST, self.request.FILES, instance=self.object())
#         if self.form.is_valid():
#             self.form.save()
#         else:
#             raise FormError
# 
# 
# class ConstantView(View):
#     def is_constant(self):
#         return True
# 
# 
# class ListView(ConstantView):
#     objects_per_page   = 10
# 
#     def context_dict(self):
#         return dict(
#                 objects             = self.objects(),
#                 page                = self.page(),
#                 linked_page_numbers = self.linked_page_numbers(),
#                 search_form         = self.search_form(),
#                 )
# 
#     def objects(self):
#         objects = self.Model.objects
#         return objects.search(self.search_string()) if self.search_string() else objects.all()
# 
#     def search_string(self):
#         return self.request.GET['search'] if 'search' in self.request.GET else None
# 
#     def page(self):
#         page = self.paginator().page(self.page_number())
#         page.view = reverse(type(self), args=self.view_args, kwargs=self.view_kwargs)
#         return page
# 
#     def paginator(self):
#         return Paginator(self.objects(), self.objects_per_page)
# 
#     def page_number(self):
#         try:
#             page = int(self.request.GET.get('page', '1'))
#         except ValueError:
#             return 1
#         else:
#             return min(max(1, page), self.paginator().num_pages)
# 
#     def linked_page_numbers(self):
#         page = self.page_number()
#         return self.paginator().page_range[max(0, page-3):page+2]
# 
#     def search_form(self):
#         return self.SearchForm(dict(search=self.search_string()) if self.search_string() else {})

