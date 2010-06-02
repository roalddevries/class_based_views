from abc import ABCMeta
from django.http import HttpResponse
from django.template import loader, Context, RequestContext


class FormError(Exception):
    pass


class View(HttpResponse):
    __metaclass__ = ABCMeta

    context_processors = []
    context_dict       = {}

    def __init__(self, request, *args, **kwargs):
        self.request     = request
        self.view_args   = args
        self.view_kwargs = kwargs
        if self.is_constant():
            super(View, self).__init__(self.content())
        else:
            try:
                self.process()
            except FormError:
                super(View, self).__init__(self.content())
            else:
                super(View, self).__init__()
                self.status_code = 302 # redirect
                self['Location'] = self.next_page

    def is_constant(self):
        return self.request.method == 'GET'

    def content(self):
        return self.template().render(self.context())

    def template(self):
        return loader.get_template(self.template_file)

    def context(self):
        if self.context_processors:
            return RequestContext(self.request, self.context_dict, processors=self.context_processors)
        else:
            return Context(self.context_dict)

