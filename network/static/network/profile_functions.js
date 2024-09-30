document.addEventListener('DOMContentLoaded', function() {

    const csrftoken = CSRF_TOKEN;
    const profilename = PROFILE_NAME;

    console.log(profilename);

    fetch_posts_and_display(profilename);
    
});


function display_followed_by(followed_by) {
    followed_by_div = document.querySelector('#followed_by');
    followed_by_div_num = len(followed_by);
    if (followed_by_div_num > 1) {
        followed_by_div.innerHTML = "Followed by " + len(following_these_users) + "users.";
    } else {
        followed_by_div.innerHTML = "Followed by " + len(following_these_users) + "user.";
    }
}


function display_following_these_users(following_these_users) {
    following_these_users_div = document.querySelector('#following_these_users');
    following_these_users_num = len(following_these_users);
    if (following_these_users_num > 1) {
        following_these_users_div.innerHTML = "Following " + len(following_these_users) + "users.";
    } else {
        following_these_users_div.innerHTML = "Following " + len(following_these_users) + "user.";
    }
}


function fetch_profile_posts(profilename) {
    return fetch('/get_users_posts/' + profilename, {
        method:"POST",
        body: JSON.stringify({
            profile: profilename,
        })
    })
    .then(response => response.json())
    .then(result => {
        // Print result
        console.log("result:");
        console.log(result); 
    });
}


function display_posts(posts) {
    posts_div = document.querySelector('#posts_div');
    posts_div.innerHTML = "";

    console.log("display_posts:");
    console.log(posts);

    posts.forEach(post => {
        
        posts_div.innerHTML = posts_div.innerHTML +     
        '<div><h4>' + post.content + '</h4><div> By: ' + post.creator + 
        ' on ' + post.date.substring(0,10) + 
        ', ' + post.date.substring(11,16) + 
        '</div><div> Likes: ' + post.likes + '</div></div><br>';

    });
}


function fetch_posts_and_display(profile) {
    fetch('/get_users_posts/' + profile, {method:"POST",
        profile: profile
    })
    .then(response => response.json())
    .then(result => {
        // Print result
        console.log("result:");
        console.log(result); 
        display_posts(result.posts);
    });
}