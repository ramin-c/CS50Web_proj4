let csrftoken;
let profilename;
let username;
let current_page;


document.addEventListener('DOMContentLoaded', function() {

    csrftoken = CSRF_TOKEN;
    profilename = PROFILE_NAME;
    username = current_username;

    console.log(profilename);

    current_page = 1

    if (current_page == 1) {
        document.getElementById('prev').parentElement.classList.add("disabled");
    }
    

    let posts = fetch_profile_posts(profilename);
    display_posts(posts);

    fetch_following_data(profilename);
    
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

    return fetch('/get_follow_data/' + profile, {method:"POST",
        profile: profile
    })
    .then(response => response.json())
    .then(result => {
        // Print result
        console.log("result following_data:");
        console.log(result.followed_by); 
        console.log(result.following_these_users); 
        display_following_data(result);
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
        display_posts(result.posts, username, csrftoken);
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

        let edited = "";

        if (post.creator == username) {


            const escaped_post_content = encodeURIComponent(post.content);
            const JSON_string_post_content = JSON.stringify(post.content);


            if (post.edited == true) {
                edited = "<span>. (Edited post)</span>";
            }



            posts_div.innerHTML += `   
            <div>
                <h4>${post.content}</h4>
                <button class="btn btn-primary" onlick="turn_into_textarea()"
                            onclick="turn_into_textarea_and_update_post(${post.id}, '${escaped_post_content}', this)">
                    Edit post
                </button>
                <div> By: <a href="/profile/${post.creator}">${post.creator}</a> 
                    on ${post.date.substring(0, 10)}, ${post.date.substring(11, 16)}
                </div>
                <div>Likes: ${post.likes}${edited}</div>
            </div>
            <br>`;
        } else {
            posts_div.innerHTML = posts_div.innerHTML +     
            '<div><h4>' + post.content + '</h4><div> By: <a href="/profile/' + post.creator + '">' +
            post.creator + '</a> on ' + post.date.substring(0,10) + 
            ', ' + post.date.substring(11,16) + 
            '</div><a href="#" id="' + post.id + '-like"onclick="like(event, ' + post.id + ')"> Likes: ' + post.likes + '</a>' + edited + '</div></div><br>';
        }
        
    });
}


function display_following_data(following_data) {
    console.log("in display_following_data()");
    console.log("following_these_users data: ");
    console.log(following_data.following_these_users.length);


    followed_by_div = document.querySelector('#followed_by');
    following_these_users_div = document.querySelector('#following_these_users');

    if (following_data.followed_by.length == 1) {
        followed_by_div.innerHTML = "Followed by " + following_data.followed_by.length + " user.";
    } else {
        followed_by_div.innerHTML = "Followed by " + following_data.followed_by.length + " users.";
    }

    if (following_data.following_these_users.length == 1) {
        following_these_users_div.innerHTML = "Following " + following_data.following_these_users.length + " user.";
    } else {
        following_these_users_div.innerHTML = "Following " + following_data.following_these_users.length + " users.";
    }
}


function turn_into_textarea_and_update_post(post_id, post_content, element) {
    // update_post(post_id, post_content, csrftoken, username);
    turn_into_textarea(element, post_content, post_id);
}


function update_post(post_id, post_content) {
    const decoded_post_content = decodeURIComponent(post_content);
    const current_date = new Date() / 1000;
    console.log("post_id:" + post_id);
    console.log("csrftoken:" + csrftoken);
    return fetch('/update_post/' + post_id, {
        method: 'POST',
          body: JSON.stringify({
            post_id: post_id,
            post_content: decoded_post_content,
            post_date: current_date,
            profile: profilename,
            request_from_page: "profile"
          }),
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken  // Include the CSRF token in the headers
          }
    }).then(response => response.json())
    .then(result => {
        // Print result
        console.log("result profile posts:");
        console.log(result); 
        display_posts(result.posts, username, csrftoken);
    });
}


function turn_into_textarea(element, post_content, post_id) {

    // Create a container ul
    let ul_with_textarea = document.createElement('ul');
    ul_with_textarea.id = "posts_div";

    // Create the textarea
    let textarea = document.createElement('textarea');
    textarea.value = decodeURIComponent(post_content); // Set the value of the textarea

    // Create the button
    let button = document.createElement('button');
    button.className = 'btn btn-primary'; // Add class to button
    // button.onclick = 
    button.onclick = function() { update_post(post_id, textarea.value, csrftoken, username); }
    button.textContent = 'Send'; // Set button text

    // Append the textarea and button to the container
    ul_with_textarea.appendChild(textarea);
    ul_with_textarea.appendChild(button);


    console.log("turn this into textarea");
    element.parentNode.parentNode.replaceWith(ul_with_textarea);
}


function load_posts_next(element) {
    //document.querySelector.getElementById("prev").parentElement.classList.remove("disabled");
    document.getElementById('prev').parentElement.classList.remove("disabled");
    fetch_posts_and_display(current_page + 1);

}


function load_posts_prev(element) {
    if (current_page < 3) {
        current_page = 1;
        document.getElementById('prev').parentElement.classList.add("disabled");
    }
    console.log("current page: " + current_page); 
    fetch_posts_and_display(current_page - 1);
}


function like(event, post_id) {

    event.preventDefault();

    console.log("liking post: " + post_id);

    fetch('/like_post/' + post_id, {
        method: 'POST',
          body: JSON.stringify({
            post_id: post_id,
            username: username
          }),
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken  // Include the CSRF token in the headers
          }
    }).then(response =>response.json())
    .then(result => {
        console.log("like set to: " + result.new_likes);
        elementValues = document.getElementById(post_id + "-like").innerHTML.split(' ');
        document.getElementById(post_id + "-like").innerHTML = "Likes: " + result.new_likes;
    });
}