from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import Post, Comment
from django.contrib.auth import authenticate, login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Q
# Create your views here.


def searchPost(request):
    post_search = ""
    if request.GET.get('search'):
        post_search = request.GET.get('search')
    posts = Post.objects.filter(
        Q(title__icontains=post_search) | Q(body__icontains=post_search))
    return posts


def index(request):
    posts = searchPost(request)
    context = {'posts': posts}

    return render(request, 'index.html', context)

# Authenticate


#
def loginUser(request):
    if request.user.is_authenticated:
        return redirect('index')
    context = {}
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            context = {'message': 'Invalid Username or Password'}

    return render(request, 'login.html', context)


@login_required(login_url='login')
def logout(request):
    auth_logout(request)
    return redirect('index')


@login_required(login_url='login')
def myAccount(request):
    user = request.user
    user_posts = Post.objects.filter(author=user)
    context = {'posts': user_posts}
    context['capitalize_username'] = request.user.username.capitalize()
    return render(request, 'my_account.html', context)


def register(request):
    if request.user.is_authenticated:
        return redirect('index')

    context = {}
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password == confirm_password:
            user = User.objects.create(
                username=username, email=email, password=password)
            user.save()

            login(request, user)
            return redirect('index')
    return render(request, 'register.html', context)

# Posts CRUD methods


def getPost(request, pk):
    post = Post.objects.get(id=pk)
    if request.method == 'POST':
        comment = request.POST.get('comment')
        Comment.objects.create(
            post=post,
            author=request.user,
            comment=comment
        )
    return render(request, 'post_detail.html', {
        'post': post
    })


@login_required(login_url='login')
def deletePost(request, pk):
    post = Post.objects.get(id=pk)
    if request.user == post.author:
        post.delete()
    else:
        return HttpResponse("403 Forbidde")

    return redirect('index')


@login_required(login_url='login')
def createPost(request):
    context = {}
    if request.method == 'POST':
        try:
            Post.objects.create(
                title=request.POST.get('title'),
                body=request.POST.get('description'),
                author=request.user
            )
            return redirect('index')
        except:
            context["message"] = "Invalid details"

    return render(request, 'new_post.html', context)


@login_required(login_url='login')
def updatePost(request, pk):
    post = Post.objects.get(id=pk)
    context = {'post': post}
    if request.method == "POST":
        if request.user == post.author:
            post.title = request.POST.get('title')
            post.body = request.POST.get('description')
            post.save()
        else:
            return HttpResponse("403 FORBIDDEN")
        return redirect('index')

    return render(request, 'post_update.html', context)
