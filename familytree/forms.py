from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
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
            'placeholder': 'Nom d\'utilisateur'
        })
    )
    password1 = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Mot de passe'
        })
    )
    password2 = forms.CharField(
        label='Confirmer le mot de passe',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Confirmer le mot de passe'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Cet email est déjà utilisé.')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Ce nom d\'utilisateur est déjà pris.')
        return username


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Nom d\'utilisateur ou email',
            'autocomplete': 'username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Mot de passe',
            'autocomplete': 'current-password'
        })
    )


class ProposedModificationForm(forms.ModelForm):
    """Formulaire pour proposer une modification (ajout, modification, suppression)"""
    
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
                'placeholder': 'ID Gramps (pour modification/suppression)',
                'required': False,
            }),
            'data': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': '{"first_name": "Jean", "last_name": "Dupont", "birth_date": "1990-01-01"}',
                'rows': 6,
            }),
        }
        labels = {
            'action': 'Type d\'action',
            'entity_type': 'Type de relation',
            'person': 'Personne concernée *',
            'entity_id': 'ID de la personne à modifier (Gramps ID)',
            'data': 'Données (format JSON)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personnaliser les options du formulaire
        self.fields['person'].queryset = Person.objects.all().order_by('last_name', 'first_name')
        self.fields['person'].label = 'Votre profil / Personne concernée *'
        # Rendre le champ obligatoire
        self.fields['person'].required = True
    
    def clean_person(self):
        """Valider que la personne est sélectionnée"""
        person = self.cleaned_data.get('person')
        if not person:
            raise forms.ValidationError('Vous devez sélectionner une personne concernée par cette proposition.')
        return person


class AddSpouseForm(forms.Form):
    """Formulaire simplifié pour proposer l'ajout d'un époux/épouse"""
    first_name = forms.CharField(
        max_length=100,
        label='Prénom',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Prénom',
        })
    )
    last_name = forms.CharField(
        max_length=100,
        label='Nom',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Nom',
        })
    )
    gender = forms.ChoiceField(
        choices=[('M', 'Homme'), ('F', 'Femme'), ('U', 'Inconnu')],
        label='Genre',
        widget=forms.RadioSelect(attrs={
            'class': 'form-radio',
        })
    )
    birth_date = forms.DateField(
        required=False,
        label='Date de naissance',
        widget=forms.DateInput(attrs={
            'class': 'form-input',
            'type': 'date',
        })
    )


class AddChildForm(forms.Form):
    """Formulaire simplifié pour proposer l'ajout d'un enfant"""
    first_name = forms.CharField(
        max_length=100,
        label='Prénom',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Prénom',
        })
    )
    last_name = forms.CharField(
        max_length=100,
        label='Nom',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Nom',
        })
    )
    gender = forms.ChoiceField(
        choices=[('M', 'Homme'), ('F', 'Femme'), ('U', 'Inconnu')],
        label='Genre',
        widget=forms.RadioSelect(attrs={
            'class': 'form-radio',
        })
    )
    birth_date = forms.DateField(
        required=False,
        label='Date de naissance',
        widget=forms.DateInput(attrs={
            'class': 'form-input',
            'type': 'date',
        })
    )


class DeletePersonForm(forms.Form):
    """Formulaire pour proposer la suppression d'une personne"""
    entity_id = forms.CharField(
        max_length=255,
        label='ID de la personne à supprimer (Gramps ID)',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'ex: I0001',
        })
    )
    confirmation = forms.BooleanField(
        label='Je confirme la suppression',
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-checkbox',
        })
    )
