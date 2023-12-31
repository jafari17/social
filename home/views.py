from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.utils.text import slugify
from django.views import View

from home.models import Post, Comment
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .form import PostCreateUpdateForm, CommentCreateForm, CommentReplyForm

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
# Create your views here.


class HomeView(View):
    def get(self, request):
        posts = Post.objects.all()
        return render(request, 'home/index.html', {'posts':posts})

class PostDetailView(View):
    form_class = CommentCreateForm
    form_class_reply = CommentReplyForm
    def setup(self, request, *args, **kwargs):
        self.post_instance = get_object_or_404(Post, pk=kwargs['post_id'], slug=kwargs['post_slug'])
        return super().setup(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        comments = self.post_instance.pcomments.filter(is_reply=False)
        return render(request, 'home/detail.html', {'post': self.post_instance, 'comments': comments, 'form': self.form_class, 'form_reply':self.form_class_reply })

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.user = request.user
            new_comment.post = self.post_instance
            new_comment.save()
            messages.success(request, 'your cooment subitted successfulLy', 'success')
            return redirect('home:post_detail', self.post_instance.id, self.post_instance.slug)
class PostDeleteView( LoginRequiredMixin, View):
    def get(self, request,post_id):
        post = get_object_or_404(Post, pk=post_id)
        if request.user.id == post.user.id:
            post.delete()
            messages.success(request, "post delete shod", 'success')
        else:
            messages.error(request, 'shoma nemitavanid post DELETE konid', 'danger')
        return redirect('home:home')


class PostUpdateView(LoginRequiredMixin, View):
    form_class = PostCreateUpdateForm

    def setup(self, request, *args, **kwargs):
        self.post_instance = get_object_or_404(Post, pk=kwargs['post_id'])

        return super().setup(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        post = self.post_instance
        if not request.user.id == post.user.id:
            messages.error(request, 'shoma nemitavanid post UPDATE konid', 'danger')
            return redirect('home:home')
        return super().dispatch(request, *args, **kwargs)


    def get(self, request, *args, **kwargs):
        post = self.post_instance
        form = self.form_class(instance=post)
        return render(request, 'home/update.html', {'form': form})

    def post(self, request, *args, **kwargs):
        post = self.post_instance
        form = self.form_class(request.POST, instance=post)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.slug = slugify(form.cleaned_data['body'][:30])
            new_post.save()
            messages.success(request, "post Update shod", 'success')
            return redirect('home:post_detail', post.id, post.slug)


class PostCreateView(LoginRequiredMixin, View):
    form_class = PostCreateUpdateForm
    template_name ='home/create.html'

    # def dispatch(self, request, *args, **kwargs):
    #     if not request.user.is_authenticated:
    #             return redirect('home:home')
    #     return super().dispatch(request, *args, **kwargs )

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
         form = self.form_class(request.POST)

         if form.is_valid():

             new_post = form.save(commit=False)
             new_post.slug = slugify(form.cleaned_data['body'][:30])
             new_post.user = request.user
             new_post.save()
             messages.success(request, "post Create shod", 'success')
             return redirect('home:post_detail', new_post.id, new_post.slug)


class PostAddReplyView(LoginRequiredMixin, View):
    form_class = CommentReplyForm

    def post(self, request, post_id, comment_id):
        post = get_object_or_404(Post, id=post_id)
        comment = get_object_or_404(Comment, id=comment_id)
        form = self.form_class(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.user = request.user
            reply.post = post
            reply.reply = comment
            reply.is_reply = True
            reply.save()
            messages.success(request,'reply success','success')
        return redirect('home:post_detail', post.id, post.slug)
