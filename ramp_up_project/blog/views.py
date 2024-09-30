from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView
from blog.models import Post, Comment, Follow


# Create your views here.
class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


class ForYouPageView(ListView):
    template_name = "forYouPage.html"
    paginate_by = 15
    model = Post

    def get_queryset(self):
        queryset = super().get_queryset()
        path = self.request.path

        if "/foryoupage/" == path:
            following = Follow.objects.filter(follower=self.request.user).values_list('following', flat=True)
            queryset = queryset.filter(user__in=following)

        return queryset.order_by("-created_at")

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = Comment.objects.all()
        return context
