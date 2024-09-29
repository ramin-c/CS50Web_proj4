from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
import json
from django.views.decorators.csrf import csrf_exempt


from .models import *


def index(request):
    posts = Post.objects.all().order_by('-date')
    for post in posts:
        post.likes = len(Like.objects.filter(post_liked=post.id))
    return render(request, "network/index.html", {
        "posts": posts
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


@login_required
def create_post(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    
     # Check if post has content
    post = json.loads(request.body)
    if post['content'] == "":
        return JsonResponse({
            "error": "Cannot create empty post."
        }, status=400)
    
    # validate creator id
    try:
        User.objects.get(pk=post['creator'])
    except User.DoesNotExist:
        return JsonResponse({
            "error": f"User with id {post['creator']} does not exist."
        }, status=400)


    # Create post
    Post.objects.create(creator=User.objects.get(pk=post['creator']), date=post['date'], content=post['content']).save()

    posts = Post.objects.all().order_by('-date').values()
    posts = list(posts)
    for element in posts:
         element['likes'] = len(Like.objects.filter(post_liked=element['id']))


    return JsonResponse({"message": "Post created.",
                         "posts": posts}, status=201)

@csrf_exempt
def load_posts(request):
    posts = Post.objects.all().order_by('-date').values()
    posts = list(posts)
    for element in posts:
         element['likes'] = len(Like.objects.filter(post_liked=element['id']))

    return JsonResponse({"posts": posts}, status=200)
