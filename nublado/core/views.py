import json
from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.cache import cache_control
from django.views.generic import View

from .forms import UploadFileForm
from .utils import LazyEncoder, handle_deleted_file, handle_upload

User = get_user_model()


def home_files(request, filename):
    return render(request, '{0}'.format(filename), {}, content_type='text/plain')


@cache_control(public=True)
def render_js(request, cache=True, *args, **kwargs):
    context = {}
    response = render(
        request=request,
        template_name='settings.js',
        context=context,
        *args,
        **kwargs
    )
    response['Content-Type'] = 'application/javascript; charset=UTF-8'
    if cache:
        now = datetime.utcnow()
        response['Last-Modified'] = now.strftime('%a, %d %b %Y %H:%M:%S GMT')
        # cache in the browser for 1 month
        expires = now + timedelta(days=31)
        response['Expires'] = expires.strftime('%a, %d %b %Y %H:%M:%S GMT')
    else:
        response['Pragma'] = 'No-Cache'
    return response


def get_required_user(request, username=None):
    user = get_object_or_404(
        User.objects.select_related('profile'),
        username=username
    )
    return user


class ObjectSessionMixin(object):
    session_obj = None
    session_obj_attrs = []

    def dispatch(self, request, *args, **kwargs):
        self.setup_session(request)
        return super(ObjectSessionMixin, self).dispatch(request, *args, **kwargs)

    def setup_session(self, request, *args, **kwargs):
        if self.session_obj is not None and self.session_obj_attrs:
            request.session['session_obj'] = {self.session_obj: {}}
            obj = getattr(self, self.session_obj, None)
            if obj is not None:
                for attr in self.session_obj_attrs:
                    request.session['session_obj'][self.session_obj][attr] = getattr(obj, attr, None)
        elif 'session_obj' in request.session:
            del request.session['session_obj']


class CachedObjectMixin(object):

    def get_object(self):
        # This is a trivial means of 'caching' the object so that
        # multiple calls don't result in repeat query executions.
        get_object = getattr(super(CachedObjectMixin, self), 'get_object', None)

        if callable(get_object):
            if not hasattr(self, 'object'):
                self.object = super(CachedObjectMixin, self).get_object()

        return self.object


class AutocompleteMixin(object):
    '''
    Generic, single-field search on a model.
    '''
    search_model = None
    search_field = None
    search_filter = 'istartswith'
    id_attr = 'id'
    label_attr = 'label'
    value_attr = 'value'
    extra_attr = {}

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            objects = self.get_queryset()
            results = []
            for obj in objects:
                obj_json = self.set_obj_attr(obj)
                results.append(obj_json)
            return JsonResponse(results, safe=False)
        else:
            return HttpResponseNotFound('Error')

    def get_queryset(self, **kwargs):
        q = self.request.GET.get('term', '')
        search_kwargs = {
            '{0}__{1}'.format(self.search_field, self.search_filter): q
        }
        qs = self.search_model.objects.filter(**search_kwargs)
        qs = qs.order_by(self.search_field, self.id_attr)
        return qs

    def set_obj_attr(self, obj, **kwargs):
        obj_json = {}
        obj_json['id'] = self.set_id_attr(obj)
        obj_json['label'] = self.set_label_attr(obj)
        obj_json['value'] = self.set_value_attr(obj)
        if self.extra_attr:
            obj_json['attr'] = self.set_extra_attr(obj)
        return obj_json

    def set_id_attr(self, obj):
        return getattr(obj, self.id_attr)

    def set_label_attr(self, obj):
        return getattr(obj, self.label_attr)

    def set_value_attr(self, obj):
        return getattr(obj, self.value_attr)

    def set_extra_attr(self, obj):
        extra_dict = {}
        for key, value in self.extra_attr.items():
            extra_dict[key] = getattr(obj, value)
        return extra_dict


class AttachmentMixin(object):
    content_type = 'text/plain'
    filename = 'document.txt'
    manual_attachment = False

    def get(self, request, *args, **kwargs):
        if self.manual_attachment:
            return self.write_attachment()
        else:
            response = super(AttachmentMixin, self).get(request, *args, **kwargs)
            return self.make_attachment(response)

    def get_content_type(self):
        return self.content_type

    def get_filename(self):
        return self.filename

    def get_file_content(self):
        return ''

    def make_attachment(self, response):
        '''
        Makes the response an attachment to be downloaded.
        '''
        content_disposition = 'attachment; filename={0}'.format(self.get_filename())
        response['Content-Disposition'] = content_disposition
        return response

    def write_attachment(self):
        '''
        Writes content directly to response.
        '''
        response = HttpResponse(content_type=self.get_content_type())
        response.write(self.get_file_content())
        return self.make_attachment(response)


class JsonAttachmentMixin(AttachmentMixin):
    json_indent = None

    def get(self, request, *args, **kwargs):
        data = self.get_file_content()
        response = JsonResponse(
            data,
            json_dumps_params={
                'indent': self.json_indent,
            },
            safe=False
        )
        return self.make_attachment(response)


class UserMixin(object):
    '''
    For views centered on a requested user. Return 404 if user not found.
    '''

    def dispatch(self, request, *args, **kwargs):
        self.requested_user = get_required_user(request, kwargs['username'])
        return super(UserMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UserMixin, self).get_context_data(**kwargs)
        context['requested_user'] = self.requested_user
        return context


class UserRequiredMixin(object):
    '''
    Requesting user must be the the requested user or superuser.
    '''

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            self.requested_user = request.user
        else:
            self.requested_user = get_required_user(request, kwargs['username'])
            if request.user.id != self.requested_user.id:
                raise PermissionDenied
        return super(UserRequiredMixin, self).dispatch(request, *args, **kwargs)


class SuperuserRequiredMixin(object):
    '''
    Requesting user must be superuser.
    '''

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied
        return super(SuperuserRequiredMixin, self).dispatch(request, *args, **kwargs)


class UserstampMixin(object):
    '''
    A view mixin for models that inherit from UserStampModel.
    It stamps the user who has created the model or updated it last.
    '''

    def form_valid(self, form):
        if not form.instance.id:
            form.instance.created_by = self.request.user
        form.instance.last_updated_by = self.request.user
        return super(UserstampMixin, self).form_valid(form)


class MessageMixin(object):
    success_message = _('message_success')
    error_message = _('message_error')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(MessageMixin, self).delete(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super(MessageMixin, self).form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, self.error_message)
        return super(MessageMixin, self).form_invalid(form)

    def get_messages(self):
        django_messages = []
        for message in messages.get_messages(self.request):
            django_messages.append({
                'level': message.level,
                'message': message.message,
                'extra_tags': message.tags,
            })
        return django_messages


class AjaxDataMixin(object):
    '''
    An ajax mixin for sending data.
    '''
    data = {}

    def get_data(self):
        return self.data


class AjaxSessionMixin(object):
    '''
    A mixin for setting user session variables via ajax.

    Expeced session post data in request body: {'session_data': {'key': 'value', ...}}
    '''

    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            data = json.loads(request.body)
            for key, value in data['session_data'].items():
                request.session[key] = value
            return JsonResponse({})
        else:
            return HttpResponseNotFound('Error')


class AjaxFormMixin(MessageMixin, AjaxDataMixin):
    '''
    Ajax mixin for ModelForm CBVs

    Error data format
    {
        'model': Model name,
        'messages': General error messages,
        'errors': {
            'non_field_errors': form non-field errors
            'fields': {
                'field 1': {
                    'id': field id,
                    'message' error message
                }
            }
        }
    }
    '''
    # A simplified template that typically only displays the form.
    ajax_template = None

    def dispatch(self, request, *args, **kwargs):
        if request.is_ajax() and self.ajax_template:
            self.template_name = self.ajax_template
        return super(AjaxFormMixin, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super(AjaxFormMixin, self).form_valid(form)
        # The model inherits from core.models.SerializeModel.
        model_object = self.object
        if self.request.is_ajax():
            serializer = model_object.get_serializer()
            obj = serializer(model_object, context={'request': self.request}).json_data()
            self.data.update(
                {
                    'obj': obj,
                    'model': self.model.__name__,
                    'messages': self.get_messages(),
                }
            )
            return JsonResponse(self.data, encoder=LazyEncoder)
        else:
            return response

    def form_invalid(self, form):
        response = super(AjaxFormMixin, self).form_invalid(form)
        if self.request.is_ajax():
            self.data = {
                'model': self.model.__name__,
                'messages': self.get_messages()
            }
            errors = {
                'non_field_errors': form.non_field_errors(),
            }
            fields = {}
            error_items = form.errors.items()
            for field_name, error_message in error_items:
                fields[field_name] = {}
                fields[field_name]['message'] = error_message
                fields[field_name]['id'] = field_name
            errors.update(fields=fields)
            self.data.update(errors=errors)
            return JsonResponse(self.data, encoder=LazyEncoder, status=400)
        else:
            return response


class AjaxMultiFormMixin(MessageMixin, AjaxDataMixin):
    '''
    Ajax mixin for MultiModelForm from django-betterforms
    '''

    def form_valid(self, form):
        response = super(AjaxMultiFormMixin, self).form_valid(form)
        object_dict = self.object
        objects = {}
        if self.request.is_ajax():
            for name, obj in object_dict.items():
                serializer = obj.get_serializer()
                objects[name] = serializer(obj, context={'request': self.request}).json_data()
            self.data = {
                'objects': objects,
                'model': self.model.__name__,
                'messages': self.get_messages(),
            }
            return JsonResponse(self.data, encoder=LazyEncoder)
        else:
            return response

    def form_invalid(self, form):
        response = super(AjaxMultiFormMixin, self).form_invalid(form)
        if self.request.is_ajax():
            self.data = {
                'model': self.model.__name__,
                'messages': self.get_messages()
            }
            errors = {
                'non_field_errors': form.non_field_errors(),
            }
            fields = {}
            for model_form in form.forms.values():
                for field_name, error_message in model_form.errors.items():
                    fields[field_name] = {}
                    fields[field_name]['message'] = error_message
                    fields[field_name]['id'] = model_form[field_name].auto_id
            errors.update(fields=fields)
            self.data.update(errors=errors)
            return JsonResponse(self.data, encoder=LazyEncoder, status=400)
        else:
            return response


class AjaxDeleteMixin(MessageMixin, AjaxDataMixin):
    '''
    Ajax mixin for DeleteView
    '''

    def delete(self, request, *args, **kwargs):
        if request.is_ajax():
            self.object = self.get_object()
            serializer = self.object.get_serializer()
            obj = serializer(self.object, context={'request': request}).json_data()
            self.data = {
                'obj': obj,
                'model': self.model.__name__,
                'success_url': self.get_success_url(),
                'success_message': self.success_message,
            }
            self.object.delete()
            return JsonResponse(self.data, encoder=LazyEncoder)
        else:
            return super(AjaxDeleteMixin, self).delete(request, *args, **kwargs)


class UploadView(View):
    '''
    View used for Fine Uploader.
    '''

    def post(self, request, *args, **kwargs):
        '''A POST request. Validate the form and then handle the upload
        based ont the POSTed data. Does not handle extra parameters yet.
        '''
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_upload(request.FILES['qqfile'], form.cleaned_data)
            data = {
                'uuid': form.cleaned_data['qquuid'],
                'success': True,
            }
            return JsonResponse(data, encoder=LazyEncoder, status=200)
        else:
            data = {
                'success': False,
                'error': '{0}'.format(repr(form.errors))
            }
            return JsonResponse(data, encoder=LazyEncoder, status=400)

    def delete(self, request, *args, **kwargs):
        '''A DELETE request. If found, deletes a file with the corresponding
        UUID from the server's filesystem.
        '''
        qquuid = kwargs.get('qquuid', '')
        if qquuid:
            try:
                handle_deleted_file(qquuid)
                data = {
                    'success': True,
                }
                return JsonResponse(data, encoder=LazyEncoder, status=200)
            except Exception as e:
                data = {
                    'success': False,
                    'error': '{0}'.format(repr(e))
                }
                return JsonResponse(data, encoder=LazyEncoder, status=400)
