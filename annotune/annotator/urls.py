from django.urls import path
from django.conf.urls.static import static
from . import views



urlpatterns = [
    path("", views.login, name="login"),
    path("skip_document/", views.skip_document, name='skip_document'),
    path("register/", views.sign_up, name="sign-up"),
    path("homepage/<int:user_id>/", views.homepage, name="homepage"),
    path("documents/<int:user_id>/<str:recommendation>/", views.list_documents, name="documents"),
    path("label/<int:user_id>/<str:document_id>/<str:recommendation>/", views.label, name="label"),
    path('get_all_documents/', views.get_all_documents, name='get-all-documents'),
    path('submit/<int:document_id>/<str:label>/', views.submit_data, name='submit_data'),
    path("fetch_data/<int:user_id>/<str:document_id>/", views.fetch_data, name="fetch_data"),
    path('logout/', views.logout_view, name='logout'),
    path("append_time/<str:pageName>/", views.append_time, name="append"),
    path("labeled/<int:user_id>/<str:recommendation>/", views.display, name="display"),
    path("relabel/<int:document_id>/<str:given_label>/", views.relabel, name="relabel"),
    path("log-hover-duration/<int:document_id>/<int:hover_time>/", views.log_hover),
    path("manualList/<int:user_id>/", views.manualDocumentsList, name="manualList"),
    path("manualLabel/<int:user_id>/<int:document_id>/", views.manualLabel, name="manualLabel"),
    path("manualLabeledList/<int:user_id>/", views.manualLabeledList, name="manualLabeledList"),
    path("pretext/<int:user_id>/", views.pre_text, name="pretext"),
    path("post-test", views.post_text, name="post-test"),
    path("thankyou", views.thankYou, name="thankYou")
]
 