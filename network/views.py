from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
import json
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers import serialize
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder





from .models import *


def index(request):
    posts = Post.objects.all().order_by('-date')
    for post in posts:
        post.likes = len(Like.objects.filter(post_liked=post.id))
    return render(request, "network/index.html", {
        "posts": posts
    })


@login_required
def following_page(request):
    following_these_users = Follower_list.objects.filter(user=User.objects.get(username=request.user.username)).values()

    print("following these users:")
    print(following_these_users)

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
        
        follower_list = get_or_create_followerlist_for_user(request.user.username)

        if profile in follower_list.followed_users.all():
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
            follower_list.followed_users.add(User.objects.get(username=profile.username))
            follower_list.save()
            following = True
        else:
            try:
                follower_list = Follower_list.objects.get(user=User.objects.get(username=request.user.username))
                print("trying to get follower lis #3:")
                print("iterating over followers in follower_list: ")
                for follower in follower_list.followed_users.all():
                    print(follower.username)
            except ObjectDoesNotExist:
                print("Could not find connection.")
            follower_list.followed_users.remove(User.objects.get(username=profile.username))
            follower_list.save()
            print("am here")
            print(follower_list.followed_users)
    
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
        profile_user = User.objects.get(username=profile)
    except IntegrityError:
        return render(request, "network/register.html", {
            "message": "User does not exist."
        })
    # Get the Follower_list object for the user
    follower_list = get_or_create_followerlist_for_user(profile_user)

    # Retrieve the list of users this user is following
    follower_list = Follower_list.objects.get(user=profile_user)
    print("trying to get follower lis #3:")
    print("iterating over followers in follower_list: ")
    following_these_users = []
    for follower in follower_list.followed_users.all():
        following_these_users.append(follower.username)
    print("following_these_users:")
    print(following_these_users)

    followed_by = []
    for follower_list in Follower_list.objects.filter(
        followed_users__username=profile_user):
        if (follower_list.user.username != profile):
            followed_by.append(follower_list.user.username) 
    print("followed by these users:")
    print(followed_by)

    # posts = list(Post.objects.filter(creator=profile))
    return JsonResponse({"following_these_users": following_these_users,
                         "followed_by": followed_by}, status=200)





    
def get_or_create_followerlist_for_user(user):
    u = User.objects.get(username=user)
    try:
        Fl = Follower_list.objects.get(user=u)
    except:
        Fl = Follower_list.objects.create(user=u)
        Fl.save()
        Fl = Follower_list.objects.get(user=u)

    return Fl


def get_followers_of_user(user):
    # Filter the Follower_list objects where 'user_a' is in the 'follows_user' field
    # followers_lists = Follower_list.objects.filter(user__in=Follower_list.objects.all())
    followers_lists = Follower_list.objects.filter(followed_users=user)
    
    # Get all users who have 'user_a' in their 'follows_user' field
    followers = [follower_list.user for follower_list in followers_lists]
    
    return followers