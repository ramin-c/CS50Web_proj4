document.addEventListener('DOMContentLoaded', function() {

    const csrftoken = CSRF_TOKEN;
    const profilename = PROFILE_NAME;

    console.log(profilename);

    let posts = fetch_profile_posts(profilename);
    display_posts(posts);

    let following_data = fetch_following_data(profilename);

    display_following_data(following_data);
    
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


function fetch_following_data(profile) {
    fetch('/get_follow_data/' + profile, {method:"POST",
        profile: profile
    })
    .then(response => response.json())
    .then(result => {
        // Print result
        console.log("result following data:");
        console.log(result); 
        display_following_data(result);
        return result;
    });
}


function fetch_profile_posts(profile) {
    return fetch('/get_users_posts/' + profile, {method:"POST",
        profile: profile
    })
    .then(response => response.json())
    .then(result => {
        // Print result
        console.log("result profile posts:");
        console.log(result); 
        display_posts(result.posts);
        return result;
    });
}


function display_posts(posts) {
    posts_div = document.querySelector('#posts_div');
    posts_div.innerHTML = "";

    console.log("display_posts:");
    console.log(posts);

    console.log("type of posts is arra:");
    console.log(Array.isArray(posts.posts));

    // Convert posts to array
    posts = Array.from(posts);

    posts.forEach(post => {
        
        posts_div.innerHTML = posts_div.innerHTML +     
        '<div><h4>' + post.content + '</h4><div> By: ' + post.creator + 
        ' on ' + post.date.substring(0,10) + 
        ', ' + post.date.substring(11,16) + 
        '</div><div> Likes: ' + post.likes + '</div></div><br>';

    });
}


function display_following_data(following_data) {
    console.log("in display_following_data()");
    followed_by_div = document.querySelector('#followed_by');
    following_these_users = document.querySelector('#following_these_users');


    if (following_data.followed_by.length == 1) {
        followed_by_div.innerHTML = "Followed by " + following_data.followed_by.length + " user.";
    } else {
        followed_by_div.innerHTML = "Followed by " + following_data.followed_by.length + " user.";
    }

    if (following_data.following_these_users.length == 1) {
        following_these_users.innerHTML = "Following " + following_data.following_these_users.length + " user.";
    } else {
        following_these_users.innerHTML = "Following " + following_data.following_these_users.length + " users.";
    }
}