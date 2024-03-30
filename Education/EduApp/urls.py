from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path("logout", views.logout_view, name="logout"),
    path("login", views.login_view, name="login"),
    path("register", views.register, name="register"),
    
    path('speech_to_text', views.speech_to_text, name='speech_to_text'),
    path('save_transcript', views.save_transcript, name='save_transcript'),
    # path('create_notes/<int:speech_data_id>/', views.create_notes, name='create_notes'),
    path('allNotes', views.subject_based_notes, name='subject_based_notes'),
    path('aiQuiz', views.AI_Quiz, name='AI_Quiz'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('saveScore', views.saveScore, name='saveScore'),

    path('tmp', views.tmp, name="tmp")
]