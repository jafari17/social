from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from account.forms import UserRegistrationForm, UserLoginForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from home.models import Post
from .models import Relation
class UserRegisterView(View):
    form_class = UserRegistrationForm
    template_name = 'account/register.html'


    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home:home')
        return super().dispatch(request, *args, **kwargs )

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
         form = self.form_class(request.POST)
         if form.is_valid():
             cd = form.cleaned_data
             User.objects.create_user(cd['username'], cd['email'], cd['password1'])
             messages.success(request, 'register successfully', 'success')
             return redirect('home:home')
         return render(request, self.template_name, {'form': form})



class User_loginView(View):
    form_class = UserLoginForm
    template_name = 'account/login.html'

    def setup(self, request, *args, **kwargs):
        self.next = request.GET.get('next')
        return super().setup(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
                return redirect('home:home')
        return super().dispatch(request, *args, **kwargs )

    def get(self, request):
        form = self.form_class
        return render(request, self.template_name, {'form':form})

    def post(self, request):
        form =self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request,  username=cd['username'], password=cd['password'])
            if user is not None:
                login(request, user)
                messages.success(request,'ba mofagiat vard shodid ', 'success')
                if self.next:
                    return redirect(self.next)
                return redirect('home:home')
            messages.error(request,'user ya password eshtebahe')
        return render(request, self.template_name, {'form': form})

class UserLogoutView(LoginRequiredMixin, View):
    # LOGIN_URL = '/account/login/'
    def get(self, request):
        logout(request)
        messages.success(request, 'logout ', 'success')
        return redirect('home:home')


class UserProfileView(LoginRequiredMixin, View):
    def get(self, request, user_id):
        is_following = False
        user = get_object_or_404(User, pk=user_id)
        posts = user.post_set.all()
        relation = Relation.objects.filter(from_user=request.user, to_user=user)
        if relation.exists():
            is_following = True
        return render(request, 'account/profile.html', {'user': user, 'posts': posts, 'is_following': is_following})


class UserFollowView(LoginRequiredMixin, View):
    def get(self, request, user_id):
        user = User.objects.get(id=user_id)
        relation = Relation.objects.filter(from_user=request.user, to_user=user)
        if relation.exists():
            messages.error(request, 'shoma follwing in user hastid', 'danger')
        else:
            Relation(from_user=request.user,to_user=user).save()
            messages.success(request,'shoma donbal konande in user hastid', 'success')
        return redirect('account:user_profile', user.id)

class UserUnfollowView(LoginRequiredMixin, View):
    def get(self, request, user_id):
        user = User.objects.get(id=user_id)
        relation = Relation.objects.filter(from_user=request.user, to_user=user)
        if relation.exists():
            relation.delete()
            messages.error(request, 'shoma follwing in user digar nistid', 'success')
        else:
            messages.success(request,'shoma donbal konande in user nistid', 'danger')
        return redirect('account:user_profile', user.id)