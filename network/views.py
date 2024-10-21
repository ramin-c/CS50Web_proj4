from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
import json
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator



from django.core.serializers.json import DjangoJSONEncoder
from django.core.serializers import serialize



class LazyEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Paginator.page):
            return str(obj)
        return super().default(obj)






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

    follower_list = get_or_create_followerlist_for_user(request.user.username)
    following_these_users = []
    for follower in follower_list.followed_users.all():
        following_these_users.append(follower.username)
    print("following these users:")
    print(following_these_users)

    posts_from_followed_users = []
    posts = Post.objects.all().order_by('-date')
    for post in posts:
        print(f"creator: {post.creator.username}")
        if post.creator.username in following_these_users:
            posts_from_followed_users.append(post)
            print(f"added post from: {post.creator.username}")

    return render(request, "network/following.html", {
        "posts": posts_from_followed_users
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
    request_data = json.loads(request.body)
    posts = Post.objects.all().order_by('-date').values()
    posts = list(posts)
    for element in posts:
        element['likes'] = len(Like.objects.filter(post_liked=element['id']))
        element['creator'] = User.objects.get(pk=element['creator_id']).username
        
    if not request_data['paginated']:

        return JsonResponse({"posts": posts}, status=200)
    
    else:
        posts_paginated = Paginator(posts, 10)
        print(f"request: posts for page {request_data['page_number']}")
        last_page = False

        if request_data['page_number'] > posts_paginated.num_pages:
            page_to_get = posts_paginated.num_pages
        elif request_data['page_number'] < 1:
            page_to_get = 1
        else:
            page_to_get = request_data['page_number']

        if page_to_get == posts_paginated.num_pages:
            last_page = True
            
        paginated_posts_as_serializable_objects = posts_paginated.page(page_to_get).object_list

        return JsonResponse({"posts": paginated_posts_as_serializable_objects, "current_page": page_to_get, "last_page": last_page}, status=200)


@csrf_exempt
def load_posts_following_page(request):
    request_data = json.loads(request.body)
    user_id = User.objects.get(username=request.user.username).id
    follower_list = Follower_list.objects.get(user=user_id)
    following_these_users = []
    for follower in follower_list.followed_users.all():
        following_these_users.append(follower.username)
    print("following these users:")
    print(following_these_users)

    posts_from_followed_users = []
    posts = Post.objects.all().order_by('-date').values()
    posts = list(posts)
    for post in posts:
        post['likes'] = len(Like.objects.filter(post_liked=post['id']))
        post['creator'] = User.objects.get(pk=post['creator_id']).username
        print(post)
        print(f"creator: {post['creator']}")
        if post['creator'] in following_these_users:
            posts_from_followed_users.append(post)
            print(f"added post from: {post['creator']}")

    print("function returns:")
    posts_from_followed_users = list(posts_from_followed_users)
    print(posts_from_followed_users)


    posts_paginated = Paginator(posts_from_followed_users, 10)
    print(f"request: posts for page {request_data['page_number']}")
    last_page = False

    if request_data['page_number'] > posts_paginated.num_pages:
        page_to_get = posts_paginated.num_pages
    elif request_data['page_number'] < 1:
        page_to_get = 1
    else:
        page_to_get = request_data['page_number']

    if page_to_get == posts_paginated.num_pages:
        last_page = True
        
    paginated_posts_from_followed_users_as_serializable_objects = posts_paginated.page(page_to_get).object_list

    return JsonResponse({"posts": paginated_posts_from_followed_users_as_serializable_objects, "current_page": page_to_get, "last_page": last_page}, status=200)
         

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
    # Get the Follower_list object for current user
    follower_list = get_or_create_followerlist_for_user(profile_user)

    # Retrieve the list of users the current user is following
    follower_list = Follower_list.objects.get(user=profile_user)
    following_these_users = []
    for follower in follower_list.followed_users.all():
        following_these_users.append(follower.username)

    # Retrieve the users that are following the current user
    followed_by = []
    for follower_list in Follower_list.objects.filter(
        followed_users__username=profile_user):
        if (follower_list.user.username != profile):
            followed_by.append(follower_list.user.username) 

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
    followers_lists = Follower_list.objects.filter(followed_users=user)
    
    followers = [follower_list.user for follower_list in followers_lists]
    
    return followers


@login_required
def update_post(request, post_id):
    if request.method == "POST":
        post = Post.objects.get(id=post_id)
        request_data = json.loads(request.body)
        if post.creator.username == request.user.username:
            post.content = request_data['post_content']
            post.edited = True
            post.save()
            if (request_data['request_from_page'] == "profile"):
                return get_profiles_posts(request, request_data['profile'])
            elif (request_data['request_from_page'] == "index"):
                return load_posts(request)
        else:
            return JsonResponse({
            "result": "Access denied. Cannot edit posts of other users."
            }, status=403)
    return JsonResponse({
        "result": "Update posts via POST method only."
    }, status=403)


# toggles likes for posts
def like_post(request, post_id):

    if request.method == "POST":

        request_data = json.loads(request.body)
        try:
            Like_obj = Like.objects.get(liked_by=User.objects.get(username=request_data['username']), 
                                       post_liked=Post.objects.get(id=post_id))
            Like_obj.delete()
            print(Like_obj)
        except:
            print("Object does not exist yet.")
            Like_obj = Like.objects.create(liked_by=User.objects.get(username=request_data['username']), 
                                       post_liked=Post.objects.get(id=post_id))
            Like_obj.save()
            print(Like_obj.liked_by)
            print(Like_obj.post_liked)

        updated_likes = Like.objects.filter(post_liked=Post.objects.get(id=post_id)).count()

        return JsonResponse({"new_likes": updated_likes}, status=200)
    
    return JsonResponse(status=403)