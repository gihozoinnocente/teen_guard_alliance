document.getElementById('reg-form').addEventListener('submit', async(e)=>{
  e.preventDefault();
  const firstName = document.getElementById('firstName').value;
  const lastName = document.getElementById('lastName').value;
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;
  // const year = document.getElementById('Dropdown').value;
  const confirmPassword = document.getElementById('cpassword').value;

  
  if(!firstName || !lastName || !email || !password  || !confirmPassword){
    showErrorMessage('Please enter all credentials');
  }
  if(password.length < 8){
    showErrorMessage('password must be at least 8 characters')
  }
  if(password !== confirmPassword){
    showErrorMessage('Password and confirm password should match');
  }
})
// Function to show success message
function showSuccessMessage(message) {
  Toastify({
      text: message || "Operation completed successfully!",
      duration: 3000,
      close: true,
      background:"green",
      className: "toastify-success"
  }).showToast();
}

// Function to show error message
function showErrorMessage(message) {
  Toastify({
      text: message || "Error: Something went wrong!",
      duration: 3000,
      close: true,
      backgroundColor:"red",
      className: "toastify-error"
  }).showToast();
}


// Sending data in database
document.addEventListener('DOMContentLoaded', function() {
  console.log('DOM fully loaded');
  const registrationForm = document.getElementById('reg-form');
  console.log(registrationForm);
  if (registrationForm) {
      registrationForm.addEventListener('submit', function(event) {
          event.preventDefault();
          const formData = {
              firstName: document.getElementById('firstName').value,
              lastName: document.getElementById('lastName').value,
              email: document.getElementById('email').value,
              password: document.getElementById('password').value,
              cpassword: document.getElementById('cpassword').value,

          };
          fetch('http://127.0.0.1:3400/register', {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json',
              },
              body: JSON.stringify(formData)
          })
          .then(response => response.json())
          .then(data => {
              document.getElementById('registrationMessage').textContent = data.message;
              if (data.redirect_url) {
                window.location.href = data.redirect_url;
            }
            });
      });
  } else {
      console.log('registrationForm not found');
  }
});