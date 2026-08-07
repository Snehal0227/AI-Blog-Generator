

function generateBlog() {

    let topic = document.getElementById("topic").value;

    if (topic == "") {

        alert("Please enter a blog topic.");

        return;

    }

    fetch("/generate_blog", {

        method: "POST",

        body: new URLSearchParams({

            topic: topic

        })

    })

    .then(response => response.text())

    .then(data => {

        document.getElementById("content").value = data;

    })

    .catch(error => {

        alert("Error generating blog!");

    });

}



function confirmDelete() {

    return confirm("Are you sure you want to delete this blog?");

}



function showLoading(button) {

    button.innerHTML = "Generating...";

    button.disabled = true;

}



function showSuccess(message) {

    alert(message);

}