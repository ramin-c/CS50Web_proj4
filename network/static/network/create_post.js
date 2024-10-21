let username;
let profilename;
let csrftoken;
let current_page;

document.addEventListener('DOMContentLoaded', function() {

    username = current_username;
    profilename = PROFILE_NAME;
    csrftoken = CSRF_TOKEN;

    current_page = 1

    if (current_page == 1) {
        document.getElementById('prev').parentElement.classList.add("disabled");
    }

    let posts = fetch_posts_and_display(current_page);

  
    // Create Post
    document.querySelector('input[type="submit"]').addEventListener('click', (event) => {
        event.preventDefault();
        const current_date = new Date() / 1000;
        const post = {
            content: document.querySelector('#post_content').value,
            date: current_date,
            creator: JSON.parse(document.getElementById('user_id').textContent)
        }
        const csrftoken = CSRF_TOKEN;
        // console.log(post);
        create_post(post, csrftoken);
    });
});

function create_post(post, csrftoken) {
    console.log("create_post(post):");
    console.log(post);

        fetch('/create_post', {
          method: 'POST',
          body: JSON.stringify({
              content: post.content,
              creator: post.creator,
              date: post.date
          }),
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken  // Include the CSRF token in the headers
          }
        })
        .then(response => response.json())  // Wait for the POST request to complete
        .then(result => {
            console.log("Result from create_post:", result);
            // After the post is successfully created, fetch the updated list of posts
            fetch_posts_and_display(current_page);  // Fetch and display the latest posts
        })
        .catch(error => {
            console.error("Error during create_post:", error);
        });
        document.querySelector('#post_content').value = "";
}

function fetch_posts(page_number) {
    return fetch('/load_posts', {method:"POST",
        body: JSON.stringify({
            paginated: true,
            page_number: page_number
          }),
    })
    .then(console.log("Posts:"))
    .then(response => response.json())
    .then(result => {
        // Print result
        console.log(result); 
        current_page = result.current_page;

        if (result.last_page) {
            document.getElementById('next').parentElement.classList.add("disabled");
        } else {
            document.getElementById('next').parentElement.classList.remove("disabled");
        }
    });
}


function fetch_posts_and_display(page_number) {
    fetch('/load_posts', {method:"POST",
        body: JSON.stringify({
        paginated: true,
        page_number: page_number
      }),})
    .then(response => response.json())
    .then(result => {
        // Print result
        console.log("result:");
        console.log(result); 
        current_page = result.current_page;

        if (result.last_page) {
            document.getElementById('next').parentElement.classList.add("disabled");
        } else {
            document.getElementById('next').parentElement.classList.remove("disabled");
        }


        display_posts(result.posts);
    });
}


function display_posts(posts) {
    posts_div = document.querySelector('#posts_div');
    posts_div.innerHTML = "";

    // Convert posts to array
    posts = Array.from(posts);

    posts.forEach(post => {

        console.log("create_posts.js – am here: ");
        console.log(post);

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
                <div><a href="#" id="${post.id}-like" onclick="like(event, ${post.id})"> Likes: ${post.likes}</a>${edited}</div>
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

function turn_into_textarea_and_update_post(post_id, post_content, element) {
    // update_post(post_id, post_content, csrftoken, username);
    turn_into_textarea(element, post_content, post_id);
}


function update_post(post_id, post_content) {
    const decoded_post_content = decodeURIComponent(post_content);
    const current_date = new Date() / 1000;
    console.log("post_id: " + post_id);
    console.log("csrftoken: " + csrftoken);
    console.log("profilename: " + csrftoken);
    return fetch('/update_post/' + post_id, {
        method: 'POST',
          body: JSON.stringify({
            post_id: post_id,
            post_content: decoded_post_content,
            post_date: current_date,
            request_from_page: "index",
            paginated: true,
            page_number: current_page
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
        display_posts(result.posts);
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


function load_posts_next(event, element) {

    event.preventDefault();

    //document.querySelector.getElementById("prev").parentElement.classList.remove("disabled");
    document.getElementById('prev').parentElement.classList.remove("disabled");
    fetch_posts_and_display(current_page + 1);

}


function load_posts_prev(event, element) {

    event.preventDefault();

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