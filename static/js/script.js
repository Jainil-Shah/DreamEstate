
document.getElementById('signup-form').addEventListener('submit', function (event) {
    // Prevent form submission
    event.preventDefault();

    // Get the password and confirm password values
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm-password').value;

    // Get the warning div to display message
    const warningDiv = document.getElementById('password-warning');

    // Check if the passwords match
    if (password !== confirmPassword) {
        // If passwords don't match, display a warning message
        warningDiv.textContent = "Passwords do not match!";
        warningDiv.style.color = 'red';
    } else {
        // If passwords match, you can submit the form or perform other actions
        warningDiv.textContent = "";
        
        // Submit the form using its ID
        document.getElementById('signup-form').submit();

        //NOTE: IF FOMR DATA IS NOT SUBMITING THEN COMMETNOUT THE UPPER LINE AND UNCOMMENT THE BELOW CODE : "this.submit()"
        // You can uncomment the following line to actually submit the form if desired
        //this.submit();
    }
});

document.getElementById('role-toggle').addEventListener('change', function () {
    var roleInput = document.getElementById('role');
    roleInput.value = this.checked ? 'seller' : 'buyer';
});


// max function
function max(arr) {
    let maxVal = arr[0];
    for (let i = 1; i < arr.length; i++) {
      if (arr[i] > maxVal) {
        maxVal = arr[i];
      }
    }
    return maxVal;
  }
  

function openEnquiryModal(element) {
    const propertyType = element.dataset.type;
    const sellerEmail = element.dataset.email;
    // Now use propertyType and sellerEmail as needed in the modal
    console.log(propertyType, sellerEmail);
}


// Properties page Authentication : 

// document.addEventListener('DOMContentLoaded', function() {
//     const propertyLink = document.getElementById('property-link');
    
//     if (propertyLink) {
//         propertyLink.addEventListener('click', function(event) {
//             event.preventDefault(); // Prevent the default link behavior
            
//             // Read the data attribute and convert it to boolean
//             const isAuthenticated = propertyLink.getAttribute('data-authenticated') === 'true';
            
//             if (isAuthenticated) {
//                 // Redirect to the properties page
//                 window.location.href = propertyLink.href;
//             } else {
//                 // Redirect to the login page
//                 window.location.href = "{{ url_for('login') }}";
//             }
//         });
//     }
// });




// document.addEventListener('DOMContentLoaded', function () {
//     const slides = document.querySelectorAll('.banner-slide');
//     let currentSlide = 0;

//     function showSlide(index) {
//         slides.forEach((slide, i) => {
//             slide.classList.toggle('active', i === index);
//         });
//     }

//     function nextSlide() {
//         currentSlide = (currentSlide + 1) % slides.length;
//         showSlide(currentSlide);
//     }

//     setInterval(nextSlide, 30000); // Change slide every 30 seconds
// });
