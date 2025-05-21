/**
 * CozyWish CMS App Media Browser
 * JavaScript for the media browser used in the CMS App
 */

document.addEventListener('DOMContentLoaded', function() {
    // Handle media item selection
    const mediaItems = document.querySelectorAll('.media-item');
    mediaItems.forEach(item => {
        item.addEventListener('click', function() {
            // Toggle selection
            if (this.classList.contains('selected')) {
                this.classList.remove('selected');
                this.style.border = 'none';
                this.style.boxShadow = '';
            } else {
                this.classList.add('selected');
                this.style.border = '2px solid #2F160F';
                this.style.boxShadow = '0 5px 15px rgba(47, 22, 15, 0.2)';
            }
            
            // Update selected count
            const selectedCount = document.querySelectorAll('.media-item.selected').length;
            const selectedCountElement = document.querySelector('.selected-count');
            if (selectedCountElement) {
                selectedCountElement.textContent = selectedCount;
            }
            
            // Show/hide bulk actions
            const bulkActions = document.querySelector('.bulk-actions');
            if (bulkActions) {
                if (selectedCount > 0) {
                    bulkActions.style.display = 'flex';
                } else {
                    bulkActions.style.display = 'none';
                }
            }
        });
    });
    
    // Handle media filter
    const mediaFilter = document.querySelector('.media-filter');
    if (mediaFilter) {
        mediaFilter.addEventListener('change', function() {
            const selectedType = this.value;
            
            mediaItems.forEach(item => {
                if (selectedType === 'all' || item.dataset.mediaType === selectedType) {
                    item.style.display = 'block';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    }
    
    // Handle media search
    const mediaSearch = document.querySelector('.media-search');
    if (mediaSearch) {
        mediaSearch.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            
            mediaItems.forEach(item => {
                const mediaTitle = item.querySelector('.media-title').textContent.toLowerCase();
                
                if (mediaTitle.includes(searchTerm)) {
                    item.style.display = 'block';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    }
    
    // Handle media upload preview
    const mediaUploadInput = document.querySelector('#id_file');
    const mediaPreview = document.querySelector('#media-preview');
    if (mediaUploadInput && mediaPreview) {
        mediaUploadInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const file = this.files[0];
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    // Clear previous preview
                    mediaPreview.innerHTML = '';
                    
                    // Create preview based on file type
                    if (file.type.startsWith('image/')) {
                        // Image preview
                        const img = document.createElement('img');
                        img.src = e.target.result;
                        img.classList.add('img-fluid');
                        mediaPreview.appendChild(img);
                    } else if (file.type.startsWith('video/')) {
                        // Video preview
                        const video = document.createElement('video');
                        video.src = e.target.result;
                        video.controls = true;
                        video.classList.add('img-fluid');
                        mediaPreview.appendChild(video);
                    } else if (file.type === 'application/pdf') {
                        // PDF preview
                        const icon = document.createElement('i');
                        icon.classList.add('fas', 'fa-file-pdf', 'fa-5x', 'text-danger');
                        mediaPreview.appendChild(icon);
                        
                        const text = document.createElement('p');
                        text.textContent = file.name;
                        text.classList.add('mt-2');
                        mediaPreview.appendChild(text);
                    } else {
                        // Generic file preview
                        const icon = document.createElement('i');
                        icon.classList.add('fas', 'fa-file', 'fa-5x', 'text-primary');
                        mediaPreview.appendChild(icon);
                        
                        const text = document.createElement('p');
                        text.textContent = file.name;
                        text.classList.add('mt-2');
                        mediaPreview.appendChild(text);
                    }
                };
                
                reader.readAsDataURL(file);
            }
        });
    }
    
    // Handle bulk delete
    const bulkDeleteButton = document.querySelector('.bulk-delete-button');
    if (bulkDeleteButton) {
        bulkDeleteButton.addEventListener('click', function() {
            const selectedItems = document.querySelectorAll('.media-item.selected');
            const selectedIds = Array.from(selectedItems).map(item => item.dataset.mediaId);
            
            if (selectedIds.length > 0) {
                if (confirm(`Are you sure you want to delete ${selectedIds.length} selected items?`)) {
                    // In a real implementation, you would send an AJAX request to delete the items
                    // For this demo, we'll just remove them from the DOM
                    selectedItems.forEach(item => {
                        item.remove();
                    });
                    
                    // Hide bulk actions
                    const bulkActions = document.querySelector('.bulk-actions');
                    if (bulkActions) {
                        bulkActions.style.display = 'none';
                    }
                    
                    // Show success message
                    const alertContainer = document.querySelector('.alert-container');
                    if (alertContainer) {
                        const alert = document.createElement('div');
                        alert.classList.add('alert', 'alert-success', 'alert-dismissible', 'fade', 'show');
                        alert.innerHTML = `
                            <strong>Success!</strong> ${selectedIds.length} items deleted successfully.
                            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                        `;
                        alertContainer.appendChild(alert);
                        
                        // Auto-dismiss after 5 seconds
                        setTimeout(() => {
                            alert.classList.remove('show');
                            setTimeout(() => {
                                alert.remove();
                            }, 150);
                        }, 5000);
                    }
                }
            }
        });
    }
});
