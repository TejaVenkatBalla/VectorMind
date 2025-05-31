

from myapp.views import home, DocumentViewSet, KnowledgeAssistantViewSet
from django.urls import path,include

urlpatterns = [
    
    path('index', home, name='home'),
    path('doc', DocumentViewSet.as_view({'get': 'list', 'post': 'create'}), name='document-list'),
    path('bot', KnowledgeAssistantViewSet.as_view({'post': 'ask_question', 'get': 'query_history'}), name='knowledge-assistant'),
]
