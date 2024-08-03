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
document.getElementById('reg-form').addEventListener('submit', async function(event) {
  event.preventDefault();

  const firstName = document.getElementById('firstName').value;
  const lastName = document.getElementById('lastName').value;
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;
  const cpassword = document.getElementById('cpassword').value;
  const roleElement = document.querySelector('select[name="role"]');
  const role = roleElement ? roleElement.value : null;

  // Validate password matching
  if (password !== cpassword) {
    Toastify({
      text: "Passwords do not match.",
      duration: 3000,
      gravity: "top",
      position: "right",
      backgroundColor: "red"
    }).showToast();
    return;
  }

  if (!role) {
    Toastify({
      text: "Please select a role.",
      duration: 3000,
      gravity: "top",
      position: "right",
      backgroundColor: "red"
    }).showToast();
    return;
  }

  const formData = {
    firstName,
    lastName,
    email,
    password,
    cpassword,
    role
  };

  try {
    const response = await fetch('http://localhost:3400/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(formData)
    });

    const data = await response.json();

    if (response.ok) {
      Toastify({
        text: data.message,
        duration: 3000,
        gravity: "top",
        position: "right",
        backgroundColor: "green"
      }).showToast();
      setTimeout(() => {
        window.location.href = data.redirect_url;
      }, 2000);
    } else {
      Toastify({
        text: data.message,
        duration: 3000,
        gravity: "top",
        position: "right",
        backgroundColor: "red"
      }).showToast();
    }
  } catch (error) {
    console.error('Error:', error);
    Toastify({
      text: "An error occurred. Please try again.",
      duration: 3000,
      gravity: "top",
      position: "right",
      backgroundColor: "red"
    }).showToast();
  }
});
