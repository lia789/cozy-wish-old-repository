// Accounts App JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Password visibility toggle
    const togglePasswordButtons = document.querySelectorAll('.toggle-password');
    
    togglePasswordButtons.forEach(button => {
        button.addEventListener('click', function() {
            const passwordField = document.querySelector(this.getAttribute('data-target'));
            
            // Toggle password visibility
            if (passwordField.type === 'password') {
                passwordField.type = 'text';
                this.innerHTML = '<i class="fas fa-eye-slash"></i>';
                this.setAttribute('title', 'Hide password');
            } else {
                passwordField.type = 'password';
                this.innerHTML = '<i class="fas fa-eye"></i>';
                this.setAttribute('title', 'Show password');
            }
        });
    });

    // Profile picture upload
    const profilePictureEdit = document.querySelector('.profile-picture-edit');
    const profilePictureInput = document.querySelector('input[type="file"][name="profile_picture"]');
    
    if (profilePictureEdit && profilePictureInput) {
        profilePictureEdit.addEventListener('click', function() {
            profilePictureInput.click();
        });
        
        // Preview uploaded image
        profilePictureInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                const profilePicture = document.querySelector('.profile-picture') || 
                                      document.querySelector('.profile-picture-placeholder');
                
                reader.onload = function(e) {
                    // If there's an existing image, update its src
                    if (profilePicture.tagName === 'IMG') {
                        profilePicture.src = e.target.result;
                    } 
                    // If it's a placeholder, replace it with an image
                    else {
                        const img = document.createElement('img');
                        img.src = e.target.result;
                        img.alt = 'Profile Picture';
                        img.className = 'profile-picture';
                        profilePicture.parentNode.replaceChild(img, profilePicture);
                    }
                };
                
                reader.readAsDataURL(this.files[0]);
            }
        });
    }
});
