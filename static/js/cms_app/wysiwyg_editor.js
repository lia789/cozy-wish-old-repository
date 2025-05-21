/**
 * CozyWish CMS App WYSIWYG Editor
 * JavaScript for the WYSIWYG editor used in the CMS App
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Summernote WYSIWYG editor
    const contentEditor = document.querySelector('#id_content');
    if (contentEditor) {
        $(contentEditor).summernote({
            height: 400,
            toolbar: [
                ['style', ['style']],
                ['font', ['bold', 'italic', 'underline', 'clear']],
                ['fontname', ['fontname']],
                ['color', ['color']],
                ['para', ['ul', 'ol', 'paragraph']],
                ['table', ['table']],
                ['insert', ['link', 'picture', 'video']],
                ['view', ['fullscreen', 'codeview', 'help']]
            ],
            callbacks: {
                onImageUpload: function(files) {
                    // This is a placeholder for image upload functionality
                    // In a real implementation, you would upload the image to the server
                    // and then insert the image URL into the editor
                    alert('Image upload is not implemented in this demo. Please use the media library to upload images and then insert them using the link tool.');
                }
            },
            placeholder: 'Write your content here...',
            styleTags: [
                'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote'
            ],
            fontNames: [
                'Arial', 'Arial Black', 'Comic Sans MS', 'Courier New', 'Helvetica', 'Impact', 'Tahoma', 'Times New Roman', 'Verdana', 'Roboto', 'Yeseva One'
            ],
            popover: {
                image: [
                    ['image', ['resizeFull', 'resizeHalf', 'resizeQuarter', 'resizeNone']],
                    ['float', ['floatLeft', 'floatRight', 'floatNone']],
                    ['remove', ['removeMedia']]
                ],
                link: [
                    ['link', ['linkDialogShow', 'unlink']]
                ],
                table: [
                    ['add', ['addRowDown', 'addRowUp', 'addColLeft', 'addColRight']],
                    ['delete', ['deleteRow', 'deleteCol', 'deleteTable']]
                ],
                air: [
                    ['color', ['color']],
                    ['font', ['bold', 'underline', 'clear']],
                    ['para', ['ul', 'paragraph']],
                    ['table', ['table']],
                    ['insert', ['link', 'picture']]
                ]
            }
        });

        // Add custom styles to Summernote
        const noteEditorFrames = document.querySelectorAll('.note-editor.note-frame');
        noteEditorFrames.forEach(frame => {
            frame.style.borderRadius = '0.5rem';
            frame.style.border = '1px solid rgba(0,0,0,0.1)';
            frame.style.overflow = 'hidden';
        });

        const noteToolbars = document.querySelectorAll('.note-toolbar');
        noteToolbars.forEach(toolbar => {
            toolbar.style.backgroundColor = '#f8f9fa';
            toolbar.style.borderBottom = '1px solid rgba(0,0,0,0.1)';
            toolbar.style.padding = '0.5rem';
        });

        const noteStatusbars = document.querySelectorAll('.note-statusbar');
        noteStatusbars.forEach(statusbar => {
            statusbar.style.backgroundColor = '#f8f9fa';
            statusbar.style.borderTop = '1px solid rgba(0,0,0,0.1)';
        });
    }

    // Initialize Summernote for excerpt field if it exists
    const excerptEditor = document.querySelector('#id_excerpt');
    if (excerptEditor) {
        $(excerptEditor).summernote({
            height: 150,
            toolbar: [
                ['style', ['bold', 'italic', 'underline', 'clear']],
                ['para', ['ul', 'ol', 'paragraph']],
                ['insert', ['link']],
                ['view', ['fullscreen', 'codeview']]
            ],
            placeholder: 'Write a brief excerpt here...'
        });
    }

    // Handle media browser integration
    const mediaBrowserButton = document.querySelector('.media-browser-button');
    if (mediaBrowserButton) {
        mediaBrowserButton.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Open media browser modal
            const mediaBrowserModal = new bootstrap.Modal(document.getElementById('mediaBrowserModal'));
            mediaBrowserModal.show();
            
            // Handle media selection
            const selectMediaButtons = document.querySelectorAll('.select-media-button');
            selectMediaButtons.forEach(button => {
                button.addEventListener('click', function() {
                    const mediaUrl = this.dataset.mediaUrl;
                    const mediaType = this.dataset.mediaType;
                    
                    // Insert media into editor based on type
                    if (mediaType.startsWith('image/')) {
                        $(contentEditor).summernote('insertImage', mediaUrl, function($image) {
                            $image.css('max-width', '100%');
                        });
                    } else {
                        $(contentEditor).summernote('createLink', {
                            text: 'Download File',
                            url: mediaUrl,
                            isNewWindow: true
                        });
                    }
                    
                    // Close modal
                    mediaBrowserModal.hide();
                });
            });
        });
    }
});
