from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from .models import ProposedModification, Person


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Email'
        })
    )
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Username'
        })
    )
    password1 = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Password'
        })
    )
    password2 = forms.CharField(
        label=_('Confirm password'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Confirm password'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('This email is already in use.'))
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(_('This username is already taken.'))
        return username


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Username or email',
            'autocomplete': 'username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Password',
            'autocomplete': 'current-password'
        })
    )


class ProposedModificationForm(forms.ModelForm):
    """Form to propose a modification (add, update, delete)"""
    
    class Meta:
        model = ProposedModification
        fields = ['action', 'entity_type', 'person', 'entity_id', 'data']
        widgets = {
            'action': forms.Select(attrs={
                'class': 'form-input',
            }),
            'entity_type': forms.Select(attrs={
                'class': 'form-input',
            }),
            'person': forms.Select(attrs={
                'class': 'form-input',
            }),
            'entity_id': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Gramps ID (for update/deletion)',
                'required': False,
            }),
            'data': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': '{"first_name": "Jean", "last_name": "Dupont", "birth_date": "1990-01-01"}',
                'rows': 6,
            }),
        }
        labels = {
            'action': _('Action type'),
            'entity_type': _('Relationship type'),
            'person': _('Affected person *'),
            'entity_id': _('Person ID to update (Gramps ID)'),
            'data': _('Data (JSON format)'),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personnaliser les options du formulaire
        self.fields['person'].queryset = Person.objects.all().order_by('last_name', 'first_name')
        self.fields['person'].label = _('Your profile / Affected person *')
        # Rendre le champ obligatoire
        self.fields['person'].required = True
    
    def clean_person(self):
        """Validate that a person is selected"""
        person = self.cleaned_data.get('person')
        if not person:
            raise forms.ValidationError(_('You must select a person affected by this proposal.'))
        return person


class AddSpouseForm(forms.Form):
    """Simplified form to propose adding a spouse"""
    first_name = forms.CharField(
        max_length=100,
        label=_('First name'),
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'First name',
        })
    )
    last_name = forms.CharField(
        max_length=100,
        label=_('Last name'),
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Last name',
        })
    )
    gender = forms.ChoiceField(
        choices=[('M', _('Male')), ('F', _('Female')), ('U', _('Unknown'))],
        label=_('Gender'),
        widget=forms.RadioSelect(attrs={
            'class': 'form-radio',
        })
    )
    birth_date = forms.DateField(
        required=False,
        label=_('Birth date'),
        widget=forms.DateInput(attrs={
            'class': 'form-input',
            'type': 'date',
        })
    )


class AddChildForm(forms.Form):
    """Simplified form to propose adding a child"""
    first_name = forms.CharField(
        max_length=100,
        label=_('First name'),
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'First name',
        })
    )
    last_name = forms.CharField(
        max_length=100,
        label=_('Last name'),
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Last name',
        })
    )
    gender = forms.ChoiceField(
        choices=[('M', _('Male')), ('F', _('Female')), ('U', _('Unknown'))],
        label=_('Gender'),
        widget=forms.RadioSelect(attrs={
            'class': 'form-radio',
        })
    )
    birth_date = forms.DateField(
        required=False,
        label=_('Birth date'),
        widget=forms.DateInput(attrs={
            'class': 'form-input',
            'type': 'date',
        })
    )


class DeletePersonForm(forms.Form):
    """Form to propose deleting a person"""
    entity_id = forms.CharField(
        max_length=255,
        label=_('Person ID to delete (Gramps ID)'),
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'e.g. I0001',
        })
    )
    confirmation = forms.BooleanField(
        label=_('I confirm the deletion'),
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-checkbox',
        })
    )
