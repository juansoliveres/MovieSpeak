from django.urls import path

from . import views
from sqltranslator.views import IndexView
from sqltranslator.views import LoginView

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("login/", LoginView.as_view(), name="login"),
]