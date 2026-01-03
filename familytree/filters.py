import django_filters
from .models import Person

class PersonFilter(django_filters.FilterSet):
    first_name = django_filters.CharFilter(lookup_expr='icontains')
    last_name = django_filters.CharFilter(lookup_expr='icontains')
    gender = django_filters.ChoiceFilter(choices=Person.GENDER_CHOICES)
    birth_date = django_filters.DateFilter()
    death_date = django_filters.DateFilter()

    class Meta:
        model = Person
        fields = ['first_name', 'last_name', 'gender', 'birth_date', 'death_date']