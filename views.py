from abc import ABCMeta
from django import forms
from django.http import HttpResponse
from django.template import loader, Context, RequestContext


class FormError(Exception):
    pass


class View(HttpResponse):
    '''A base class for django views

    For constant views (that don't change the state of the model), combines a
    template and a context into a response.

    For non-constant views, processes POST data, and if it succeeds redirects
    to a next page.
    '''
    __metaclass__ = ABCMeta

    Form               = None
    context_processors = []

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

    def context_dict(self):
        return {'form': self.form()} if self.Form else {}

    def object(self):
        return None

    def form(self):
        if not hasattr(self, '_form'):
            args = [] if self.is_constant() else [self.request.POST, self.request.FILES]
            kwargs = {'instance': self.object()} if self.object() else {}
            self._form = self.Form(*args, **kwargs)
        return self._form

    def process(self):
        '''Process POST data, and throw a FormError if it isn't valid'''
        if self.form().is_valid():
            if isinstance(self.form(), forms.ModelForm):
                self.form().save()
        else:
            raise FormError

