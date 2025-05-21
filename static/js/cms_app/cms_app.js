/**
 * CozyWish CMS App JavaScript
 * Main JavaScript file for the CMS App
 */

document.addEventListener('DOMContentLoaded', function() {
    // Add hover effect to blog cards
    const blogCards = document.querySelectorAll('.blog-card');
    blogCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px)';
            this.style.boxShadow = '0 15px 35px rgba(47, 22, 15, 0.15)';
        });
        card.addEventListener('mouseleave', function() {
            this.style.transform = '';
            this.style.boxShadow = '';
        });
    });

    // Add hover effect to media items
    const mediaItems = document.querySelectorAll('.media-item');
    mediaItems.forEach(item => {
        item.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 10px 25px rgba(0, 0, 0, 0.15)';
        });
        item.addEventListener('mouseleave', function() {
            this.style.transform = '';
            this.style.boxShadow = '';
        });
    });

    // Add custom styling to pagination
    const paginationLinks = document.querySelectorAll('.pagination .page-link');
    paginationLinks.forEach(link => {
        link.classList.add('rounded-circle');
        link.style.margin = '0 3px';
    });

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Handle dismissible alerts
    const alertCloseButtons = document.querySelectorAll('.alert .btn-close');
    alertCloseButtons.forEach(button => {
        button.addEventListener('click', function() {
            const alert = this.closest('.alert');
            alert.classList.add('fade');
            setTimeout(() => {
                alert.style.display = 'none';
            }, 150);
        });
    });

    // Handle search form submission
    const searchForm = document.querySelector('.search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            const searchInput = this.querySelector('input[type="search"]');
            if (!searchInput.value.trim()) {
                e.preventDefault();
                searchInput.focus();
            }
        });
    }

    // Handle comment form submission
    const commentForm = document.querySelector('.comment-form');
    if (commentForm) {
        commentForm.addEventListener('submit', function(e) {
            const commentInput = this.querySelector('textarea');
            if (!commentInput.value.trim()) {
                e.preventDefault();
                commentInput.focus();
            }
        });
    }

    // Handle category filter
    const categoryFilter = document.querySelector('.category-filter');
    if (categoryFilter) {
        categoryFilter.addEventListener('change', function() {
            const selectedCategory = this.value;
            if (selectedCategory) {
                window.location.href = selectedCategory;
            }
        });
    }

    // Handle back to top button
    const backToTopButton = document.querySelector('.back-to-top');
    if (backToTopButton) {
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                backToTopButton.classList.add('show');
            } else {
                backToTopButton.classList.remove('show');
            }
        });

        backToTopButton.addEventListener('click', function(e) {
            e.preventDefault();
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }

    // Handle image preview for media upload
    const mediaUploadInput = document.querySelector('#id_file');
    const mediaPreview = document.querySelector('#media-preview');
    if (mediaUploadInput && mediaPreview) {
        mediaUploadInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    mediaPreview.innerHTML = `<img src="${e.target.result}" class="img-fluid">`;
                };
                reader.readAsDataURL(this.files[0]);
            }
        });
    }

    // Handle slug generation from title
    const titleInput = document.querySelector('#id_title');
    const slugInput = document.querySelector('#id_slug');
    if (titleInput && slugInput && slugInput.value === '') {
        titleInput.addEventListener('blur', function() {
            const title = this.value;
            if (title) {
                // Simple slug generation (for more complex needs, use a server-side API)
                const slug = title
                    .toLowerCase()
                    .replace(/[^\w\s-]/g, '')
                    .replace(/[\s_-]+/g, '-')
                    .replace(/^-+|-+$/g, '');
                slugInput.value = slug;
            }
        });
    }
});
