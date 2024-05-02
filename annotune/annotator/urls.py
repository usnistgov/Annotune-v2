from django.urls import path

from . import views

urlpatterns = [ 
    path("", views.login, name="login"),
    path("sign-up", views.sign_up, name="sign-up"),
    path("homepage", views.homepage, name="homepage"),
    path("load-files", views.load_files, name="load-files"),
    path("documents", views.list_documents, name="documents"),
    path("label", views.label, name="label"),
]