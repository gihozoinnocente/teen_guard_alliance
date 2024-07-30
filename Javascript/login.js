//login
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded');
    const loginForm = document.getElementById('login-form');
    console.log(loginForm)
    if (loginForm) {
        loginForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const formData = {
                firstName: document.getElementById('username').value,
                password: document.getElementById('password').value,
            };
            fetch('http://127.0.0.1:3400/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('loginMessage').textContent = data.message;
                if (data.redirect_url) {
                  window.location.href = data.redirect_url;
              }
              });
        });
    } else {
        console.log('login Form not found');
    }
  });