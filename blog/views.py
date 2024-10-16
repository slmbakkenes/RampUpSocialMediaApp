from django.contrib import messages

from blog.forms import ProfileForm
from forms.comment_form import CommentForm
from blog.models import Post, Comment, User, Profile, Category, CategoryPost, LikePost
from blog.models import Follow as FollowModel
from forms.post_form import PostForm
from forms.user_create_form import UserCreationForm
from django.urls import reverse_lazy
from django.urls import reverse
from django.views.generic import CreateView, ListView, TemplateView, UpdateView, DeleteView, DetailView, RedirectView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponseForbidden, JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


# Home view that requires login
class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'
    login_url = 'login'  # Redirect to login if not authenticated

# Class-based view for following a user
class Follow(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        # Get the user to be followed
        user_to_follow = get_object_or_404(User, username=kwargs['username'])

        # Check if the logged-in user is not already following the user
        if not FollowModel.objects.filter(follower=self.request.user, following=user_to_follow).exists():
            # Create the follow relationship
            FollowModel.objects.create(follower=self.request.user, following=user_to_follow)

        # Redirect back to the profile page of the followed user
        return reverse('profile', kwargs={'username': user_to_follow.username})


# Class-based view for unfollowing a user
class Unfollow(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        # Get the user to be unfollowed
        user_to_unfollow = get_object_or_404(User, username=kwargs['username'])

        # Check if the logged-in user is following the user
        follow_relation = FollowModel.objects.filter(follower=self.request.user, following=user_to_unfollow)
        if follow_relation.exists():
            # Remove the follow relationship
            follow_relation.delete()

        # Redirect back to the profile page of the unfollowed user
        return reverse('profile', kwargs={'username': user_to_unfollow.username})


# Sign-up view for creating a new user
class SignUpView(CreateView):
    form_class = UserCreationForm
    template_name = "registration/signup.html"

    def form_invalid(self, form):
        response = super().form_invalid(form)
        error_message(self, form)
        return response

    def get_success_url(self):
        success_message(self)
        return reverse_lazy("login")

# View for the "For You" page showing posts from followed users
class ForYouPageView(LoginRequiredMixin, ListView):
    template_name = "index.html"
    paginate_by = 15
    model = Post

    def get_queryset(self):
        queryset = super().get_queryset()
        path = self.request.path

        if "/foryoupage/" == path:
            following = FollowModel.objects.filter(follower=self.request.user).values_list('following', flat=True)
            queryset = queryset.filter(user__in=following)

        categories = self.request.GET.getlist('categories')
        if categories:
            queryset = queryset.filter(categorypost__category__id__in=categories).distinct()

        return queryset.order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = Comment.objects.all()
        context['categoryPosts'] = CategoryPost.objects.all()
        context['categories'] = Category.objects.all()
        context['checked'] = self.request.GET.getlist('categories')
        liked_posts = LikePost.objects.filter(user=self.request.user).values_list('post_id', flat=True)
        context['liked_posts'] = liked_posts
        return context

# View for creating a new post
class PostCreationView(LoginRequiredMixin, CreateView):
    form_class = PostForm
    template_name = "Post/create_post.html"

    def form_valid(self, form):
        form.instance.user = self.request.user  # Associate the post with the logged-in user
        response = super().form_valid(form)
        categories = form.cleaned_data.get('categories')
        for category in categories:
            CategoryPost.objects.create(post=self.object, category=category)
        return response

    def form_invalid(self, form):
        response = super().form_invalid(form)
        error_message(self, form)
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

    def get_success_url(self):
        success_message(self)
        # Redirect to the user's profile using the username
        return reverse_lazy('profile', kwargs={'username': self.request.user.username})

# View for listing all posts
class ListPostsView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'list_posts.html'
    paginate_by = 15  # You can adjust this as needed

# View for updating a post
class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'post/update_post.html'

    def form_valid(self, form):
        # Save the post object
        post = form.save()

        # Get the list of selected category IDs from the form
        selected_categories_ids = self.request.POST.getlist('categories')

        # Clear old categories linked to the post
        CategoryPost.objects.filter(post=post).delete()

        # Add new categories selected in the form
        for category_id in selected_categories_ids:
            category = get_object_or_404(Category, id=category_id)
            CategoryPost.objects.create(post=post, category=category)

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get all categories
        context['categories'] = Category.objects.all()

        # Fetch the post instance
        post = self.get_object()

        # Get the selected categories linked to this post from the blog_categorypost table
        context['selected_categories'] = CategoryPost.objects.filter(post=post).values_list('category_id', flat=True)

        return context

    def get_success_url(self, **kwargs):
        return reverse_lazy('profile', kwargs={'username': self.request.user.username})

# View for deleting a post
class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'profile/profile.html'

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        if post.user != request.user:
            return HttpResponseForbidden("You are not allowed to delete this post.")
        return super().dispatch(request, *args, **kwargs)

    # Na het verwijderen van de post wordt de gebruiker teruggestuurd naar hun profielpagina
    def get_success_url(self):
        return reverse_lazy('profile', kwargs={'username': self.request.user.username})


class LikePostView(LoginRequiredMixin, TemplateView):
    def post(self, request, *args, **kwargs):
        # Ensure the request is an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            post_id = request.POST.get('post_id')  # Get the post ID from the request
            post = get_object_or_404(Post, id=post_id)  # Fetch the post object
            liked = False  # Track if the post is liked or unliked

            # Check if the post has already been liked by this user
            like = LikePost.objects.filter(post=post, user=request.user).first()

            if like:
                # If already liked, unlike it
                like.delete()
                post.no_of_likes -= 1
                post.save()  # Save the updated like count
            else:
                # If not liked, create a new like
                new_like = LikePost(post=post, user=request.user)
                new_like.save()
                post.no_of_likes += 1
                post.save()  # Save the updated like count
                liked = True

            # Return a JSON response with the updated like status and like count
            return JsonResponse({
                'liked': liked,
                'no_of_likes': post.no_of_likes,
            })

        # If it's not a valid AJAX request, return an error
        return JsonResponse({'error': 'Invalid request'}, status=400)

class ReportPostView(LoginRequiredMixin, TemplateView):
    def post(self, request, *args, **kwargs):
        post_id = kwargs['post_id']
        post = get_object_or_404(Post, id=post_id)

        # Check if the user has already reported this post
        if request.user in post.reported_by.all():
            messages.error(request, 'You have already reported this post.')
            return redirect(request.META.get('HTTP_REFERER', 'foryoupage'))  # Redirect back to previous page

        # Add the user to the reported_by field and increase the report count
        post.reported_by.add(request.user)
        post.total_reports += 1

        # If the total reports reach 5, soft-delete the post
        if post.total_reports >= 5:
            post.is_deleted = True
            messages.info(request, 'This post has been removed due to multiple reports.')
        else:
            messages.success(request, 'Thank you for reporting this post.')

        post.save()

        # Redirect back to the previous page or a default page
        return redirect(request.META.get('HTTP_REFERER', 'foryoupage'))

class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'profile/profile.html'
    context_object_name = 'user'

    def get_object(self, queryset=None):
        # Get the user based on the username in the URL
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()

        # Get the profile of the user
        context['profile'] = get_object_or_404(Profile, user=user)
        context['self'] = self.request.user

        # Get all posts of the user
        posts = Post.objects.filter(user=user).order_by('-created_at')

        # Pagination setup
        paginator = Paginator(posts, 15)  # Show 15 posts per page
        page = self.request.GET.get('page')  # Get the page number from the request

        try:
            paginated_posts = paginator.page(page)
        except PageNotAnInteger:
            paginated_posts = paginator.page(1)  # If page is not an integer, deliver the first page
        except EmptyPage:
            paginated_posts = paginator.page(paginator.num_pages)  # If page is out of range, deliver the last page

        # Add paginated posts and pagination object to the context
        context['posts'] = paginated_posts
        context['page_obj'] = paginated_posts  # Add page_obj to maintain consistency with other views
        context['is_paginated'] = paginated_posts.has_other_pages()  # Flag to indicate if pagination is needed

        context['is_following'] = FollowModel.objects.filter(follower=self.request.user, following=user).exists()

        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'profile/profile_update.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        user = get_object_or_404(User, username=self.kwargs['username'])
        return get_object_or_404(Profile, user=user)

    def form_valid(self, form):
        profile = form.save(commit=False)
        profile.save()
        success_message(self)
        return redirect('profile', username=self.kwargs['username'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Haal alle categorieën op, en ook de categorieën die bij het profiel horen
        categories = Category.objects.all()
        selected_categories = self.object.categories.values_list('id', flat=True)  # Categorieën van profiel
        context['categories'] = categories
        context['selected_categories'] = selected_categories  # Voeg geselecteerde categorieën toe aan context
        return context


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    form_class = CommentForm
    template_name = 'confirm_delete.html'  # Dit is de template waarin je de bevestiging voor verwijderen toont.

    def dispatch(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.user != request.user:
            return HttpResponseForbidden()  # Voorkom ongeautoriseerde verwijderingen
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        # Redirect naar de detailpagina van de post na succesvolle verwijdering
        return reverse_lazy('post_detail', kwargs={'post_id': self.object.post.id})

class CommentCreationView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'post/post_detail.html'  # Maak deze template aan voor het toevoegen van opmerkingen

    def form_valid(self, form):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])  # Verkrijg de post
        form.instance.user = self.request.user  # Koppel de gebruiker aan de opmerking
        form.instance.post = post  # Koppel de opmerking aan de post
        response = super().form_valid(form)  # Verwerk het formulier en sla de opmerking op
        return response  # Geef de response terug na succesvolle validatie

    def get_success_url(self):
        # Redirect naar de detailpagina van de post na succesvol toevoegen van een commentaar
        return reverse_lazy('post_detail', kwargs={'post_id': self.object.post.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = get_object_or_404(Post, id=self.kwargs['post_id'])  # Verkrijg de post om deze in de context te kunnen gebruiken
        return context


class EditCommentView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'post/post_detail.html'  # Hier stellen we de juiste template in voor bewerken

    def dispatch(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.user != request.user:
            return HttpResponseForbidden()  # Voorkom ongeautoriseerde bewerkingen
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('post_detail', kwargs={'post_id': self.object.post.id})


# Method to take an invalid form and pass an error message
def error_message(self, form):
    message = ""
    for key, value in form.errors.items():
        for item in value:
            message += f"{key.capitalize()}: "
            message += f"{item}\n"
    messages.error(self.request, message)

# Method to take an invalid form and pass a success message
def success_message(self):
    type_of_request = ""
    if self.form_class.__name__.lower().__contains__("delete"):
        type_of_request += "deleted"
    elif self.form_class.__name__.lower().__contains__("update"):
        type_of_request += "updated"
    elif self.form_class.__name__.lower().__contains__("create"):
        type_of_request += "created"
    message = f"Successfully created {self.form_class.Meta.model.__name__}!"
    messages.success(self.request, message)

# Method to take an invalid form and pass an info message
def info_message(self, message):
    try:
        messages.info(self.request, message)
    except AttributeError:
        messages.info(self, message)
