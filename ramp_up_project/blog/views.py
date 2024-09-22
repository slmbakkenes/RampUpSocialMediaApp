from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView

from blog.models import Post


# Create your views here.
class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"

class ForYouPageView(ListView):
    template_name = "forYouPage.html"
    paginate_by = 10
    model = Post
