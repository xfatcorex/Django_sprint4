from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import CommentForm, PostForm, ProfileForm
from .models import Category, Comment, Post, User


POST_QUANTITY = 10

POST = Post.objects.filter(
    category__is_published=True
)

SORTING = '-pub_date'


def paginator(object_list, page_number):
    paginator = Paginator(object_list, POST_QUANTITY)
    return paginator.get_page(page_number)


def post_filter(posts_manager):
    return posts_manager.filter(
        pub_date__date__lte=timezone.now(),
        is_published=True
    )


def index(request):
    posts = post_filter(POST).annotate(
        comment_count=Count('comments')
    ).order_by(SORTING)
    page_obj = paginator(posts, request.GET.get('page'))
    context = {'page_obj': page_obj}
    return render(request, 'blog/index.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post = (
        post if post.author == request.user
        else get_object_or_404(post_filter(POST), pk=post_id)
    )
    form = CommentForm(request.POST or None)
    context = {
        'post': post,
        'form': form,
        'comments': post.comments.all()
    }
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    page_obj = paginator(post_filter(category.posts), request.GET.get('page'))
    context = {'category': category, 'page_obj': page_obj}
    return render(request, 'blog/category.html', context)


def profile(request, username):
    profile = get_object_or_404(
        User,
        username=username
    )
    posts = profile.posts.annotate(
        comment_count=Count('comments')
    ).order_by(SORTING)
    page_obj = paginator(posts, request.GET.get('page'))
    context = {'profile': profile, 'page_obj': page_obj}
    return render(request, 'blog/profile.html', context)


@login_required
def create_and_edit_post(request, post_id=None):
    if post_id is not None:
        post_obj = get_object_or_404(Post, pk=post_id)
        if request.user != post_obj.author:
            return redirect('blog:post_detail', post_id)
    else:
        post_obj = None
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post_obj
    )
    context = {'form': form}
    if form.is_valid():
        form.instance.author = request.user
        form.save()
        return (redirect('blog:post_detail', post_id) if post_id is not None
                else redirect('blog:profile', request.user))
    return render(request, 'blog/create.html', context)


def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id)
    form = PostForm(instance=post)
    context = {'form': form}
    if request.method == 'POST':
        post.delete()
        return redirect('blog:index')
    return render(request, 'blog/create.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('blog:post_detail', post_id)
    return render(request, 'blog/detail.html', {'post': post, 'form': form})


def edit_profile(request):
    username = get_object_or_404(
        User,
        username=request.user
    )
    form = ProfileForm(request.POST or None, instance=username)
    context = {'form': form}
    if form.is_valid():
        form.save()
        return redirect('blog:profile', form.instance.username)
    return render(request, 'blog/user.html', context)


def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user != comment.author:
        return redirect('blog:post_detail', post_id)
    form = CommentForm(request.POST or None, instance=comment)
    context = {'form': form, 'comment': comment}
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id)
    return render(request, 'blog/comment.html', context)


def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user != comment.author:
        return redirect('blog:post_detail', post_id)
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id)
    return render(request, 'blog/comment.html', {})
