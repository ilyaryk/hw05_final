from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.cache import cache_page

from .models import Post, Group, User, Comment, Follow
from .forms import PostForm, CommentForm
from .utils import paginator_arrange


@cache_page(20)
def index(request):
    post_list = Post.objects.all().order_by('-pub_date')
    page_obj = paginator_arrange(request, post_list)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.filter(group=group).order_by('-pub_date')
    page_obj = paginator_arrange(request, post_list)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


@cache_page(20)
def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    page_obj = paginator_arrange(request, post_list)
    following = False
    if request.user.is_authenticated:
        if (Follow.objects.filter(user=request.user,
                                  author=author).exists()):
            following = True
    context = {'author': author,
               'page_obj': page_obj,
               'following': following,
               }
    return render(request, 'posts/profile.html', context)


@cache_page(20)
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    comments = Comment.objects.filter(post=post).order_by('created')
    context = {'post': post,
               'form': form,
               'comments': comments
               }
    return render(request, 'posts/posts.html', context)


@cache_page(20)
@login_required
def post_create(request):
    form = PostForm(request.POST or None,
                    files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author_id = request.user.id
        post.save()
        return redirect('posts:profile', request.user.username)
    template = 'posts/create_post.html'
    context = {
        'form': form,
        'is_edit': False,
    }
    return render(request, template, context)


@cache_page(20)
@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None, instance=post)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id)
        return render(request, 'posts/create_post.html', {'form': form})
    context = {
        'form': form,
        'post': post,
        'is_edit': True
    }
    return render(request, 'posts/create_post.html', context)


@cache_page(20)
@login_required
def add_comment(request, post_id):
    form = CommentForm(request.POST or None)
    post = get_object_or_404(Post, pk=post_id)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    follows = Follow.objects.filter(user=request.user)
    post_list = []
    for i in follows:
        posts = Post.objects.filter(author=i.author)
        for f in posts:
            post_list.append(f)
    page_obj = paginator_arrange(request, post_list)
    context = {'page_obj': page_obj}
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if not (Follow.objects.filter(user=request.user,
                                  author=author).exists()) \
       and author != request.user:
        Follow.objects.create(user=request.user, author=author)
    context = {
        'username': username
    }
    return render(request, 'posts/profile_follow.html', context)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    if author:
        Follow.objects.get(user=request.user, author=author).delete()
    context = {
        'username': username
    }
    return render(request, 'posts/profile_unfollow.html', context)
