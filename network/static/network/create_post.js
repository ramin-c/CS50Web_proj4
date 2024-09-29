document.addEventListener('DOMContentLoaded', function() {

    let posts = fetch_posts_and_display();

  
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
            fetch_posts_and_display();  // Fetch and display the latest posts
        })
        .catch(error => {
            console.error("Error during create_post:", error);
        });
        document.querySelector('#post_content').value = "";
}

function fetch_posts() {
    return fetch('/load_posts', {method:"POST"})
    .then(console.log("Posts:"))
    .then(response => response.json())
    .then(result => {
        // Print result
        console.log(result); 
    });
}


function fetch_posts_and_display() {
    fetch('/load_posts', {method:"POST"})
    .then(response => response.json())
    .then(result => {
        // Print result
        console.log("result:");
        console.log(result); 
        display_posts(result.posts);
    });
}


function display_posts(posts) {
    posts_div = document.querySelector('#posts_div');
    posts_div.innerHTML = "";

    posts.forEach(post => {
        
        posts_div.innerHTML = posts_div.innerHTML +     
        '<div><h4>' + post.content + '</h4><div> By: ' + post.creator + 
        ' on ' + post.date.substring(0,10) + 
        ', ' + post.date.substring(11,16) + 
        '</div><div> Likes: ' + post.likes + '</div></div><br>';

    });
}