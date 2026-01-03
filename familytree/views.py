from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import xml.etree.ElementTree as ET
import gzip
import tarfile
import os
import tempfile
import json
from .models import Person, Family, Event, Place, Note, Media, FamilyChild, ProposedModification
from .forms import RegisterForm, LoginForm, ProposedModificationForm, AddSpouseForm, AddChildForm, DeletePersonForm

GRAMPS_NS = 'http://gramps-project.org/xml/1.7.2/'  # Namespace for Gramps XML
ET.register_namespace('', GRAMPS_NS)


def import_gramps_data(file_path):
    # Clear existing data (optional, for fresh import)
    Person.objects.all().delete()
    Family.objects.all().delete()
    Event.objects.all().delete()
    Place.objects.all().delete()
    Note.objects.all().delete()
    Media.objects.all().delete()
    FamilyChild.objects.all().delete()
    
    # Check if it's a tar.gz containing the gramps file
    gramps_file_path = None
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            with gzip.open(file_path, 'rb') as gz_file:
                with tarfile.open(fileobj=gz_file, mode='r') as tar:
                    for member in tar.getmembers():
                        if member.name.endswith('.gramps'):
                            tar.extract(member, temp_dir)
                            gramps_file_path = os.path.join(temp_dir, member.name)
                            break
        except (tarfile.TarError, gzip.BadGzipFile):
            # Not a tar.gz, assume it's the gramps file directly
            gramps_file_path = file_path
        
        if not gramps_file_path:
            raise ValueError("No .gramps file found in the archive")
        
        # Now parse the gramps file
        try:
            file_obj = gzip.open(gramps_file_path, 'rt', encoding='utf-8')
            context = ET.iterparse(file_obj, events=('end',))
        except (gzip.BadGzipFile, OSError, UnicodeDecodeError):
            file_obj = open(gramps_file_path, 'r', encoding='utf-8')
            context = ET.iterparse(file_obj, events=('end',))
            
        places = {}
        people = {}
        families = {}
        
        for event, elem in context:
            tag = elem.tag.split('}', 1)[1] if '}' in elem.tag else elem.tag
            if tag == 'placeobj':
                place_id = elem.get('id')
                place_name_elem = elem.find(f'{{{GRAMPS_NS}}}ptitle')
                place_name = place_name_elem.text if place_name_elem is not None and place_name_elem.text else ''
                place = Place.objects.create(gramps_id=place_id, name=place_name)
                places[place_id] = place
            elif tag == 'person':
                person_id = elem.get('id')
                name_elem = elem.find(f'{{{GRAMPS_NS}}}name')
                first_name_elem = name_elem.find(f'{{{GRAMPS_NS}}}first') if name_elem else None
                first_name = first_name_elem.text if first_name_elem and first_name_elem.text else ''
                last_name_elem = name_elem.find(f'{{{GRAMPS_NS}}}surname') if name_elem else None
                last_name = last_name_elem.text if last_name_elem and last_name_elem.text else ''
                gender_elem = elem.find(f'{{{GRAMPS_NS}}}gender')
                gender = gender_elem.text.upper() if gender_elem and gender_elem.text else 'U'
                
                person = Person.objects.create(
                    gramps_id=person_id,
                    first_name=first_name,
                    last_name=last_name,
                    gender=gender
                )
                people[person_id] = person
            elif tag == 'family':
                family_id = elem.get('id')
                father_elem = elem.find(f'{{{GRAMPS_NS}}}father')
                father_id = father_elem.get('hlink') if father_elem is not None else None
                mother_elem = elem.find(f'{{{GRAMPS_NS}}}mother')
                mother_id = mother_elem.get('hlink') if mother_elem is not None else None
                
                family = Family.objects.create(
                    gramps_id=family_id,
                    father=people.get(father_id),
                    mother=people.get(mother_id)
                )
                families[family_id] = family
                
                # Add children with their order from Gramps
                for order, child_elem in enumerate(elem.findall(f'{{{GRAMPS_NS}}}childref')):
                    child_id = child_elem.get('hlink')
                    if child_id in people:
                        FamilyChild.objects.create(
                            family=family,
                            child=people[child_id],
                            order=order
                        )
            elif tag == 'event':
                event_id = elem.get('id')
                event_type = elem.get('type', 'unknown')
                date_elem = elem.find(f'{{{GRAMPS_NS}}}dateval')
                date = date_elem.get('val') if date_elem is not None else None
                
                place_elem = elem.find(f'{{{GRAMPS_NS}}}place')
                place_id = place_elem.get('hlink') if place_elem is not None else None
                description_elem = elem.find(f'{{{GRAMPS_NS}}}description')
                description = description_elem.text if description_elem and description_elem.text else ''
                
                # Find associated person or family
                person = None
                family_obj = None
                for person_elem in elem.findall(f'.//{{{GRAMPS_NS}}}person'):
                    person_id = person_elem.get('hlink')
                    person = people.get(person_id)
                for family_ref in elem.findall(f'.//{{{GRAMPS_NS}}}family'):
                    family_id = family_ref.get('hlink')
                    family_obj = families.get(family_id)
                
                Event.objects.create(
                    gramps_id=event_id,
                    type=event_type,
                    date=date,
                    place=places.get(place_id),
                    description=description,
                    person=person,
                    family=family_obj
                )
            elif tag == 'note':
                note_id = elem.get('id')
                text_elem = elem.find(f'{{{GRAMPS_NS}}}text')
                text = text_elem.text if text_elem and text_elem.text else ''
                
                Note.objects.create(
                    gramps_id=note_id,
                    text=text,
                    person=None,
                    family=None,
                    event=None
                )
            elif tag == 'object':
                obj_id = elem.get('id')
                file_elem = elem.find(f'{{{GRAMPS_NS}}}file')
                file_path = file_elem.get('src') if file_elem else ''
                mime_type = file_elem.get('mime') if file_elem else ''
                description_elem = elem.find(f'{{{GRAMPS_NS}}}description')
                description = description_elem.text if description_elem and description_elem.text else ''
                
                Media.objects.create(
                    gramps_id=obj_id,
                    file_path=file_path,
                    mime_type=mime_type,
                    description=description
                )
            # Clear element to save memory
            elem.clear()
        
        file_obj.close()


@login_required(login_url='login')
def person_detail(request, gramps_id_numeric):
    gramps_id = f'I{gramps_id_numeric:04d}'
    person = get_object_or_404(Person, gramps_id=gramps_id)
    
    # Get parents
    parents = []
    families_as_child = Family.objects.filter(children=person)
    for family in families_as_child:
        if family.father:
            parents.append(family.father)
        if family.mother:
            parents.append(family.mother)
    
    # Get siblings (sorted by Gramps order, then by birth date)
    siblings = []
    for family in families_as_child:
        # Get siblings through FamilyChild to preserve order
        family_children = FamilyChild.objects.filter(family=family).order_by('order', 'child__birth_date')
        for fc in family_children:
            if fc.child != person and fc.child not in siblings:
                siblings.append(fc.child)
    
    # Get spouses - families where this person is father or mother
    spouses = []
    families_as_parent = Family.objects.filter(father=person) | Family.objects.filter(mother=person)
    for family in families_as_parent:
        if family.father and family.father != person:
            spouses.append(family.father)
        if family.mother and family.mother != person:
            spouses.append(family.mother)
    
    # Get children grouped by spouse (with proper ordering)
    spouse_children = {}
    for spouse in spouses:
        # Find family where person and spouse are parents
        family = Family.objects.filter(
            (models.Q(father=person) & models.Q(mother=spouse)) |
            (models.Q(father=spouse) & models.Q(mother=person))
        ).first()
        if family:
            # Get children ordered by Gramps order, then by birth date
            family_children = FamilyChild.objects.filter(family=family).order_by('order', 'child__birth_date')
            spouse_children[spouse] = [fc.child for fc in family_children]
        else:
            spouse_children[spouse] = []
    
    # Prepare spouse data as list of tuples
    spouse_data = [(spouse, spouse_children[spouse]) for spouse in spouses]
    
    # Get all children (with proper ordering)
    children = []
    for family in families_as_parent:
        family_children = FamilyChild.objects.filter(family=family).order_by('order', 'child__birth_date')
        for fc in family_children:
            if fc.child not in children:
                children.append(fc.child)
    
    context = {
        'person': person,
        'parents': parents,
        'siblings': siblings,
        'spouse_data': spouse_data,
        'children': children,
    }
    
    return render(request, 'familytree/person_detail.html', context)


def landing(request):
    """Page publique d'accueil pour les utilisateurs non authentifiés"""
    if request.user.is_authenticated:
        return redirect('home')
    
    # Afficher les statistiques même pour les utilisateurs non connectés
    from django.db.models import Min, Max
    
    total_people = Person.objects.count()
    total_families = Family.objects.count()
    earliest_birth = Person.objects.filter(birth_date__isnull=False).aggregate(Min('birth_date'))['birth_date__min']
    latest_birth = Person.objects.filter(birth_date__isnull=False).aggregate(Max('birth_date'))['birth_date__max']
    deceased_count = Person.objects.filter(models.Q(death_date__isnull=False) | models.Q(is_deceased=True)).count()
    
    context = {
        'total_people': total_people,
        'total_families': total_families,
        'earliest_birth': earliest_birth,
        'latest_birth': latest_birth,
        'deceased_count': deceased_count,
        'living_count': total_people - deceased_count,
    }
    
    return render(request, 'familytree/landing.html', context)


@login_required(login_url='login')
def home(request):
    from django.db.models import Min, Max
    from django.core.paginator import Paginator
    
    # Gather statistics
    total_people = Person.objects.count()
    total_families = Family.objects.count()
    earliest_birth = Person.objects.filter(birth_date__isnull=False).aggregate(Min('birth_date'))['birth_date__min']
    latest_birth = Person.objects.filter(birth_date__isnull=False).aggregate(Max('birth_date'))['birth_date__max']
    deceased_count = Person.objects.filter(models.Q(death_date__isnull=False) | models.Q(is_deceased=True)).count()
    
    # Search functionality
    search_query = request.GET.get('q', '').strip()
    people = None
    
    if search_query:
        people = Person.objects.filter(
            models.Q(first_name__icontains=search_query) |
            models.Q(last_name__icontains=search_query) |
            models.Q(gramps_id__icontains=search_query)
        ).order_by('last_name', 'first_name')
        
        # Pagination
        paginator = Paginator(people, 25)  # 25 résultats par page
        page_number = request.GET.get('page')
        people = paginator.get_page(page_number)
    
    context = {
        'total_people': total_people,
        'total_families': total_families,
        'earliest_birth': earliest_birth,
        'latest_birth': latest_birth,
        'deceased_count': deceased_count,
        'living_count': total_people - deceased_count,
        'search_query': search_query,
        'people': people,
    }
    
    return render(request, 'familytree/home.html', context)


def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, _('Registration successful! You are now logged in.'))
            return redirect('home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, _(f'{field}: {error}'))
    else:
        form = RegisterForm()
    
    return render(request, 'familytree/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            # Try to authenticate with username or email
            user = authenticate(request, username=username, password=password)
            
            if user is None:
                # Try with email
                try:
                    user_obj = User.objects.get(email=username)
                    user = authenticate(request, username=user_obj.username, password=password)
                except User.DoesNotExist:
                    pass
            
            if user is not None:
                login(request, user)
                messages.success(request, _(f'Welcome {user.username}!'))
                return redirect('home')
            else:
                messages.error(request, _('Invalid username/email or password.'))
    else:
        form = LoginForm()
    
    return render(request, 'familytree/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, _('You have been logged out.'))
    return redirect('login')


from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods


@login_required(login_url='login')
def propose_modification(request):
    """Permettre à l'utilisateur de proposer une modification"""
    if request.method == 'POST':
        form = ProposedModificationForm(request.POST)
        if form.is_valid():
            modification = form.save(commit=False)
            modification.user = request.user
            
            # Assurer que l'entity_id contient au moins le gramps_id si la personne est sélectionnée
            if modification.person and not modification.entity_id:
                modification.entity_id = modification.person.gramps_id
            
            # Si data est une chaîne JSON, la parser
            if isinstance(modification.data, str):
                try:
                    modification.data = json.loads(modification.data)
                except json.JSONDecodeError:
                    messages.error(request, _('The JSON format of the data is invalid.'))
                    return render(request, 'familytree/propose_modification.html', {'form': form})
            
            modification.save()
            messages.success(request, _(f'Your proposal has been sent to the administrator. Number: #{modification.id}'))
            return redirect('home')
    else:
        form = ProposedModificationForm()
    
    return render(request, 'familytree/propose_modification.html', {'form': form})


@login_required(login_url='login')
def propose_spouse(request, gramps_id_numeric):
    """Proposer l'ajout d'un époux/épouse de manière simplifiée"""
    gramps_id = f'I{gramps_id_numeric:04d}'
    person = get_object_or_404(Person, gramps_id=gramps_id)
    
    # Vérifier que c'est l'utilisateur qui fait la proposition
    if request.method == 'POST':
        form = AddSpouseForm(request.POST)
        if form.is_valid():
            # Créer une proposition
            modification = ProposedModification.objects.create(
                user=request.user,
                person=person,
                action='add',
                entity_type='spouse',
                data={
                    'first_name': form.cleaned_data['first_name'],
                    'last_name': form.cleaned_data['last_name'],
                    'gender': form.cleaned_data['gender'],
                    'birth_date': str(form.cleaned_data['birth_date']) if form.cleaned_data['birth_date'] else None,
                }
            )
            messages.success(request, _(f'Your spouse addition proposal has been sent. Number: #{modification.id}'))
            return redirect('person_detail', gramps_id_numeric=gramps_id_numeric)
    else:
        form = AddSpouseForm()
    
    context = {
        'form': form,
        'person': person,
        'modification_type': 'époux/épouse'
    }
    return render(request, 'familytree/propose_spouse.html', context)


@login_required(login_url='login')
def propose_child(request, gramps_id_numeric):
    """Proposer l'ajout d'un enfant de manière simplifiée"""
    gramps_id = f'I{gramps_id_numeric:04d}'
    person = get_object_or_404(Person, gramps_id=gramps_id)
    
    if request.method == 'POST':
        form = AddChildForm(request.POST)
        if form.is_valid():
            # Créer une proposition
            modification = ProposedModification.objects.create(
                user=request.user,
                person=person,
                action='add',
                entity_type='child',
                data={
                    'first_name': form.cleaned_data['first_name'],
                    'last_name': form.cleaned_data['last_name'],
                    'gender': form.cleaned_data['gender'],
                    'birth_date': str(form.cleaned_data['birth_date']) if form.cleaned_data['birth_date'] else None,
                }
            )
            messages.success(request, _(f'Your child addition proposal has been sent. Number: #{modification.id}'))
            return redirect('person_detail', gramps_id_numeric=gramps_id_numeric)
    else:
        form = AddChildForm()
    
    context = {
        'form': form,
        'person': person,
        'modification_type': 'enfant'
    }
    return render(request, 'familytree/propose_child.html', context)


@login_required(login_url='login')
def propose_delete(request, gramps_id_numeric):
    """Proposer la suppression d'une personne"""
    gramps_id = f'I{gramps_id_numeric:04d}'
    person = get_object_or_404(Person, gramps_id=gramps_id)
    
    if request.method == 'POST':
        form = DeletePersonForm(request.POST)
        if form.is_valid():
            # Créer une proposition
            modification = ProposedModification.objects.create(
                user=request.user,
                person=person,
                action='delete',
                entity_type='other',
                entity_id=person.gramps_id,
                data={}
            )
            messages.success(request, _(f'Your deletion proposal has been sent. Number: #{modification.id}'))
            return redirect('home')
    else:
        form = DeletePersonForm()
    
    context = {
        'form': form,
        'person': person,
    }
    return render(request, 'familytree/propose_delete.html', context)


@login_required(login_url='login')
def my_proposals(request):
    """Afficher toutes les propositions de l'utilisateur"""
    proposals = ProposedModification.objects.filter(user=request.user).order_by('-created_at')
    
    # Statistiques
    stats = {
        'total': proposals.count(),
        'proposed': proposals.filter(status='proposed').count(),
        'acknowledged': proposals.filter(status='acknowledged').count(),
        'completed': proposals.filter(status='completed').count(),
        'rejected': proposals.filter(status='rejected').count(),
    }
    
    context = {
        'proposals': proposals,
        'stats': stats,
    }
    return render(request, 'familytree/my_proposals.html', context)
