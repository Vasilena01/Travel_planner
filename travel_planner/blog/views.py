from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date
from .models import Post

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
        title = request.POST['title']
        content = request.POST['content']
        date_posted = date.today()
        image = request.FILES['image']

        try:
            Post.objects.create(
                author = request.user,
                title = title,
                content = content,
                date_posted = date_posted,
                image = image
            )
            messages.success(request, 'Account created successfully. Please login.')
            return redirect('list_posts')
        except Exception as e:
            messages.error(request, 'Error creating blog post. Please try again.')
            return render(request, 'blog/create_post.html')

    return render(request, 'blog/create_post.html')

@login_required
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if post.author != request.user:
        messages.error(request, "You don't have permission to delete this post.")
        return redirect('list_posts')

    post.delete()
    messages.success(request, "Post deleted successfully.")
    return redirect('list_posts')

