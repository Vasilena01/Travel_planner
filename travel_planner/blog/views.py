from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date
from .models import Post
from .forms import PostForm

@login_required
def list_posts(request):
    posts = Post.objects.all().order_by('-date_posted')
    return render(request, 'blog/main_blog_page.html', {'posts': posts})

@login_required
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})

@login_required
def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Post created successfully!')
            return redirect('list_posts')
        else:
            messages.error(request, 'Error creating blog post. Please try again.')
    else:
        form = PostForm()

    return render(request, 'blog/create_post.html', {'form': form})

@login_required
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if post.author != request.user:
        messages.error(request, "You don't have permission to delete this post.")
        return redirect('list_posts')

    post.delete()
    messages.success(request, "Post deleted successfully.")
    return redirect('list_posts')

@login_required
def edit_post(request, pk):
    post = get_object_or_404(Post, id=pk)

    if post.author != request.user:
        messages.error(request, "You do not have permission to edit this post.")
        return redirect('post_detail', pk=post.id)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Post updated successfully!")
            return redirect('list_posts')
    else:
        form = PostForm(instance=post)

    return render(request, 'blog/post_detail.html', {'post': post, 'form': form})