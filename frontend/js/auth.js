document.addEventListener('DOMContentLoaded', function () {
    // Check if the user is authenticated
    const authButton = document.getElementById('authButton');
    const logoutButton = document.getElementById('logoutButton');
    const authMessage = document.getElementById('authMessage');
    
    // Check if user data is in session storage
    const user = JSON.parse(sessionStorage.getItem('discord_user'));

    if (user) {
        // User is logged in, show logout button
        if (authButton) authButton.style.display = 'none';
        if (logoutButton) logoutButton.style.display = 'inline-block';
        if (authMessage) authMessage.innerText = `Welcome, ${user.username}!`;
    } else {
        // User is not logged in, show login button
        if (authButton) authButton.style.display = 'inline-block';
        if (logoutButton) logoutButton.style.display = 'none';
    }

    // Event listener for logging out
    if (logoutButton) {
        logoutButton.addEventListener('click', () => {
            sessionStorage.removeItem('discord_user');
            window.location.href = '/logout';
        });
    }
});

// Handle the callback after OAuth login success
function handleAuthCallback(user) {
    sessionStorage.setItem('discord_user', JSON.stringify(user));
    window.location.href = '/select-server';
}
