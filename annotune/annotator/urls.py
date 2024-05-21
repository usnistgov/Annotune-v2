from django.urls import path
from django.conf.urls.static import static
from . import views



urlpatterns = [ 
    path("", views.login, name="login"),
    path("register", views.sign_up, name="sign-up"),
    path("homepage", views.homepage, name="homepage"),
    path("documents", views.list_documents, name="documents"),
    path("label", views.label, name="label"),
    # path("label2", views.label2, name="label2"),
    path('skip/', views.skip_document, name='skip_document'),
    path('submit/<str:document_id>/<str:label>/', views.submit_data, name='submit_data'),
    

]

