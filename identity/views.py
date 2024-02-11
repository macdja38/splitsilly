from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView

from .forms import SignupForm, UserSettingsForm
from .models import User


class Login(LoginView):
    def get_default_redirect_url(self):
        return reverse("groups:index")


class Signup(CreateView):
    model = User
    form_class = SignupForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("groups:index")

    def _get_invite(self):
        from groups.views import get_valid_invite

        if hasattr(self, "_invite"):
            return self._invite
        elif not self.request.GET.get("invite_id"):
            return None
        else:
            self._invite = get_valid_invite(self.request.GET["invite_id"])
            return self._invite

    def dispatch(self, request, *args, **kwargs):
        if not request.GET.get("invite_id"):
            return render(request, "registration/signup_disallowed.html")
        elif self._get_invite() is None:
            return render(request, "groups/invite_invalid.html")
        else:
            return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        invite = self._get_invite()
        if invite:
            return reverse("groups:consume_invite", args=[invite.id])
        else:
            return super().get_success_url()


class Logout(LogoutView):
    next_page = "home"


class UserSettingsView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserSettingsForm
    template_name = "identity/settings.html"
    success_url = reverse_lazy("groups:index")

    def get_object(self):
        return self.request.user
