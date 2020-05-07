from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class BaseModelForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        # kwargs.setdefault('auto_id', '%s')
        # kwargs.setdefault('label_suffix', '')
        super(BaseModelForm, self).__init__(*args, **kwargs)
