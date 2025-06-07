

from myapp.views import home, DocumentViewSet, KnowledgeAssistantViewSet,RegisterView
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView


urlpatterns = [
    
    path('index', home, name='home'),
    path('doc', DocumentViewSet.as_view({'get': 'list', 'post': 'create'}), name='document-list'),
    path('bot', KnowledgeAssistantViewSet.as_view({'post': 'ask_question', 'get': 'query_history'}), name='knowledge-assistant'),
    
    #signin/signup
    path('register', RegisterView.as_view(), name='register'),
    path('login', TokenObtainPairView.as_view(), name='token_obtain_pair'),
]
