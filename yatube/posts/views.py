from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post, User
from .paginator import get_paginator


def index(request):
    context = get_paginator(Post.objects.all(), request)
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    context = {
        'group': group,
    }
    context.update(get_paginator(post_list, request))
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    # Здесь код запроса к модели и создание словаря контекста
    author = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=author)
    post_count = author.posts.count()
    context = {
        'author': author,
        'post_count': post_count,
    }
    context.update(get_paginator(post_list, request))
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
    form = PostForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            author = request.user
            post = form.save(commit=False)
            post.author = author
            post.save()
            username = author.username
            return redirect('posts:profile', username)
        return render(request, template, {'form': form})
    return render(request, template, {'form': form})


@login_required
def post_edit(request, post_id):
    template = 'posts/post_create.html'
    post = Post.objects.get(pk=post_id)
    form = PostForm(request.POST or None, instance=post)
    if request.method == 'POST':
        if request.user == post.author:
            form.save()
            return redirect('posts:post_detail', post_id)
        return render(request, template, {'form': form})
    return render(request, template, {'form': form})
