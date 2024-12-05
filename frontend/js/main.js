document.addEventListener("DOMContentLoaded", function() {
    const backendUrl = "https://your-backend-url.com";  // Replace with your backend URL

    fetch(`${backendUrl}/api/servers`)
        .then(response => response.json())
        .then(data => {
            const serversDiv = document.getElementById("servers");
            data.forEach(server => {
                let serverElement = document.createElement("div");
                serverElement.innerHTML = `<a href="configure_server.html?server_id=${server.id}">${server.name}</a>`;
                serversDiv.appendChild(serverElement);
            });
        })
        .catch(error => console.error("Error fetching servers:", error));
});