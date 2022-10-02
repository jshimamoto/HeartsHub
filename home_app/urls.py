from django.urls import path
from . import views


urlpatterns = [
path('', views.home, name = 'home'),
path('create/', views.create, name = 'create'),
path('groups/', views.groups, name = 'groups'),
path('groups/addplayers/<int:id>', views.addplayers, name = 'addplayers'),
path('groups/<int:id>', views.groupview, name = 'groupview'),
path('groups/<int:groupid>/<int:gameid>', views.game_, name = 'game_'),
path('results/<int:resultid>', views.result, name = 'result'),
path('people/', views.people, name = 'people')
]