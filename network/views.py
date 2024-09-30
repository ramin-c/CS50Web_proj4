from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
import json
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist



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
         element['creator'] = User.objects.get(pk=element['creator_id']).username
         
    return JsonResponse({"posts": posts}, status=200)


def user_profile(request, profile):

    try:
        profile = User.objects.get(username=profile)
    except:
        return render(request, "network/profile.html", {
            "message": "User does not exist."
        })
    try:
        posts = list(Post.objects.filter(creator=profile.id))
    except IntegrityError:
            return render(request, "network/register.html", {
                "posts": posts
            })
    
    follower_list = None
    following = False

    if request.user.username == profile.username:
        return render(request, "network/profile.html", {
        "profile": profile.username,
        "following": following
    })

    if request.user.is_authenticated and request.method != "POST":
        try:
            follower_list = Follower_list.objects.get(user=User.objects.get(username=request.user.username))
            print("trying to get follower list #1:")
            print(follower_list)
        except ObjectDoesNotExist:
            print("Could not find connection.")
        if follower_list is not None:
            if len(Follower_list.objects.filter(
                user=User.objects.get(username=request.user.username), 
                follows_user=User.objects.get(username=profile.username))) > 0:
                following = True


    
    if request.user.is_authenticated and request.method == "POST":
        if request.POST.get('action', False) == 'follow':
            try:
                follower_list = Follower_list.objects.get(user=User.objects.get(username=request.user.username))
                print("trying to get follower lis #2:")
                print(follower_list)
            except ObjectDoesNotExist:
                print("Could not find connection.")
            if follower_list is None:
                follower_list = Follower_list.objects.create(user=User.objects.get(username=request.user.username))
            follower_list.follows_user.add(User.objects.get(username=profile.username))
            follower_list.save()
            following = True
        else:
            try:
                follower_list = Follower_list.objects.get(user=User.objects.get(username=request.user.username))
                print("trying to get follower lis #3:")
                print(follower_list)
            except ObjectDoesNotExist:
                print("Could not find connection.")
            follower_list.follows_user.remove(User.objects.get(username=profile.username))
            follower_list.save()
            print("am here")
            print(follower_list.follows_user)
    
    return render(request, "network/profile.html", {
        "profile": profile.username,
        "following": following
    })

    

@csrf_exempt
def get_profiles_posts(request, profile):

    try:
        profile = User.objects.get(username=profile)
    except IntegrityError:
        return render(request, "network/register.html", {
            "message": "User does not exist."
        })
    posts = list(Post.objects.filter(creator=profile).order_by('-date').values())
    for post in posts:
        post['likes'] = len(Like.objects.filter(post_liked=post['id']))
        post['creator'] = User.objects.get(pk=post['creator_id']).username
    return JsonResponse({"posts": posts}, status=200)


@csrf_exempt
def get_follow_data(request, profile):
    try:
        profile = User.objects.get(username=profile)
    except IntegrityError:
        return render(request, "network/register.html", {
            "message": "User does not exist."
        })
    following_these_users = list(Follower_list.objects.filter(follows_user=User.objects.get(username=profile)).values())
    followed_by = list(Follower_list.objects.filter(user=User.objects.get(username=profile)).values())
    print(Follower_list.id)
    print(Follower_list.follows_user)
    # posts = list(Post.objects.filter(creator=profile))
    return JsonResponse({"following_these_users": following_these_users,
                         "followed_by": followed_by}, status=200)