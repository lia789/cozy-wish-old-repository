document.addEventListener('DOMContentLoaded', function() {
    // Get all alert messages
    const alerts = document.querySelectorAll('.alert');
    
    alerts.forEach(alert => {
        // Set timeout to remove the alert after 2.5 seconds
        setTimeout(() => {
            // First fade out (using Bootstrap's fade class)
            alert.classList.remove('show');
            
            // After fade animation completes, remove the element
            setTimeout(() => {
                alert.remove();
            }, 150); // Bootstrap's default transition duration
        }, 2500); // 2.5 seconds (2500 milliseconds)
    });
});
