from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('home/', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('people/<int:gramps_id_numeric>/', views.person_detail, name='person_detail'),
    # Routes pour les propositions de modification
    path('propose/', views.propose_modification, name='propose_modification'),
    path('propose/spouse/<int:gramps_id_numeric>/', views.propose_spouse, name='propose_spouse'),
    path('propose/child/<int:gramps_id_numeric>/', views.propose_child, name='propose_child'),
    path('propose/delete/<int:gramps_id_numeric>/', views.propose_delete, name='propose_delete'),
    path('my-proposals/', views.my_proposals, name='my_proposals'),
]
