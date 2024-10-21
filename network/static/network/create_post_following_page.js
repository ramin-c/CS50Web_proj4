let current_page;


document.addEventListener('DOMContentLoaded', function() {

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
    return fetch('/load_posts_following_page', {method:"POST",
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
    fetch('/load_posts_following_page', {method:"POST",
        body: JSON.stringify({
            paginated: true,
            page_number: page_number
          }),
    })
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

    posts.forEach(post => {
        
        posts_div.innerHTML = posts_div.innerHTML +     
        '<div><h4>' + post.content + '</h4><div> By: <a href="/profile/' + post.creator + '">' +
        post.creator + '</a> on ' + post.date.substring(0,10) + 
        ', ' + post.date.substring(11,16) + 
        '</div><div> Likes: ' + post.likes + '</div></div><br>';

    });
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