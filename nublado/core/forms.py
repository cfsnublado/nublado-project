from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class BaseModelForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        # kwargs.setdefault('auto_id', '%s')
        # kwargs.setdefault('label_suffix', '')
        super(BaseModelForm, self).__init__(*args, **kwargs)


class UploadFileForm(forms.Form):
    ''' This form represents a basic request from Fine Uploader.
    The required fields will **always** be sent, the other fields are optional
    based on your setup.

    Edit this if you want to add custom parameters in the body of the POST
    request.
    '''
    qqfile = forms.FileField()
    qquuid = forms.CharField()
    qqfilename = forms.CharField()
    qqpartindex = forms.IntegerField(required=False)
    qqchunksize = forms.IntegerField(required=False)
    qqpartbyteoffset = forms.IntegerField(required=False)
    qqtotalfilesize = forms.IntegerField(required=False)
    qqtotalparts = forms.IntegerField(required=False)
