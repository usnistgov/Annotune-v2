from django.urls import path
from django.conf.urls.static import static
from . import views



urlpatterns = [ 
    path("", views.login, name="login"),
    path("skip_document/", views.skip_document),
    path("register", views.sign_up, name="sign-up"),
    path("homepage/<int:user_id>/", views.homepage, name="homepage"),
    path("documents/<int:user_id>/", views.list_documents, name="documents"),
    path("label/<int:user_id>/<str:document_id>/", views.label, name="label"),
    path('get_all_documents/', views.get_all_documents, name='get-all-documents'),
    path('submit/<int:document_id>/<str:label>/', views.submit_data, name='submit_data'),
    path("fetch_data/<int:user_id>/<str:document_id>/", views.fetch_data, name="fetch_data"),
    path('logout/', views.logout_view, name='logout')
    
]
