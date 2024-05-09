from django.urls import path
from .views import CustomLoginView
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [ 
    path("", CustomLoginView.as_view(), name="login"),
    path("register", views.sign_up, name="sign-up"),
    path("homepage", views.homepage, name="homepage"),
    path("load-files", views.load_files, name="load-files"),
    path("documents", views.list_documents, name="documents"),
    path("label", views.label, name="label"),
    path("label2", views.label2, name="label2"),
]

# # Append static files serving URL pattern (only in development)
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)