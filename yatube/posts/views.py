from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post, User


def index(request):
    template = 'posts/index.html'
    post_list = Post.objects.all()
    paginator = Paginator(post_list, settings.SHOW_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    template = 'posts/group_list.html'
    post_list = group.posts.all()
    paginator = Paginator(post_list, settings.SHOW_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    # Здесь код запроса к модели и создание словаря контекста
    author = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=author)
    paginator = Paginator(post_list, settings.SHOW_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    post_count = Post.objects.filter(author=author).count()
    context = {
        'author': author,
        'page_obj': page_obj,
        'post_count': post_count,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    context = {
        'post': post,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    template = 'posts/post_create.html'
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            group = form.cleaned_data['group']
            author = request.user
            post = Post.objects.create(text=text, group=group, author=author)
            post.save()
            username = author.username
            return redirect('posts:profile', username)
        return render(request, template, {'form': form})
    form = PostForm()
    return render(request, template, {'form': form})


@login_required
def post_edit(request, post_id):
    template = 'posts/post_create.html'
    if request.method == 'POST':
        post = Post.objects.get(pk=post_id)
        form = PostForm(request.POST or None, instance=post)
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id)
        return render(request, template, {'form': form})
    post = Post.objects.get(pk=post_id)
    form = PostForm(request.POST or None, instance=post)
    is_edit = True
    return render(request, template, {'form': form, 'is_edit': is_edit})
