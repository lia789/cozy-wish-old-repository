/**
 * Image utilities for client-side validation and preview
 */

class ImageUtils {
    /**
     * Image specifications by type
     */
    static IMAGE_SPECS = {
        'profile': {
            maxWidth: 800,
            maxHeight: 800,
            aspectRatio: 1.0,  // 1:1 square
            maxFileSize: 100 * 1024,  // 100KB
            allowedExtensions: ['.jpg', '.jpeg', '.png']
        },
        'logo': {
            maxWidth: 500,
            maxHeight: 500,
            aspectRatio: null,  // Varies
            maxFileSize: 150 * 1024,  // 150KB
            allowedExtensions: ['.png', '.jpg', '.jpeg']
        },
        'venue': {
            maxWidth: 1200,
            maxHeight: 800,
            aspectRatio: 1.5,  // 3:2
            maxFileSize: 500 * 1024,  // 500KB
            allowedExtensions: ['.jpg', '.jpeg', '.png']
        }
    };

    /**
     * Validate file extension
     * @param {File} file - The file to validate
     * @param {string} imageType - Type of image (profile, logo, venue)
     * @returns {boolean} - Whether the file extension is valid
     */
    static validateExtension(file, imageType = 'profile') {
        const fileName = file.name.toLowerCase();
        const fileExt = '.' + fileName.split('.').pop();
        const allowedExtensions = this.IMAGE_SPECS[imageType]?.allowedExtensions || ['.jpg', '.jpeg', '.png'];
        
        return allowedExtensions.includes(fileExt);
    }

    /**
     * Validate file size
     * @param {File} file - The file to validate
     * @param {string} imageType - Type of image (profile, logo, venue)
     * @returns {boolean} - Whether the file size is valid
     */
    static validateSize(file, imageType = 'profile') {
        const maxSize = this.IMAGE_SPECS[imageType]?.maxFileSize || 500 * 1024;
        return file.size <= maxSize;
    }

    /**
     * Get image dimensions
     * @param {File} file - The image file
     * @returns {Promise<{width: number, height: number}>} - Image dimensions
     */
    static getImageDimensions(file) {
        return new Promise((resolve, reject) => {
            const img = new Image();
            img.onload = () => {
                resolve({
                    width: img.width,
                    height: img.height
                });
            };
            img.onerror = () => {
                reject(new Error('Failed to load image'));
            };
            img.src = URL.createObjectURL(file);
        });
    }

    /**
     * Validate image dimensions and aspect ratio
     * @param {File} file - The image file
     * @param {string} imageType - Type of image (profile, logo, venue)
     * @returns {Promise<{isValid: boolean, message: string}>} - Validation result
     */
    static async validateDimensions(file, imageType = 'profile') {
        try {
            const { width, height } = await this.getImageDimensions(file);
            const specs = this.IMAGE_SPECS[imageType] || this.IMAGE_SPECS.profile;
            
            // Check maximum dimensions
            if (width > specs.maxWidth || height > specs.maxHeight) {
                return {
                    isValid: false,
                    message: `Image dimensions (${width}x${height}) exceed the maximum allowed (${specs.maxWidth}x${specs.maxHeight})`
                };
            }
            
            // Check aspect ratio if specified
            if (specs.aspectRatio) {
                const imageRatio = width / height;
                const allowedVariance = 0.1;
                
                if (Math.abs(imageRatio - specs.aspectRatio) > allowedVariance) {
                    return {
                        isValid: false,
                        message: `Image aspect ratio (${imageRatio.toFixed(2)}) should be close to ${specs.aspectRatio.toFixed(2)}`
                    };
                }
            }
            
            return {
                isValid: true,
                message: 'Image dimensions are valid'
            };
        } catch (error) {
            return {
                isValid: false,
                message: 'Failed to validate image dimensions'
            };
        }
    }

    /**
     * Validate an image file
     * @param {File} file - The image file
     * @param {string} imageType - Type of image (profile, logo, venue)
     * @returns {Promise<{isValid: boolean, errors: string[]}>} - Validation result
     */
    static async validateImage(file, imageType = 'profile') {
        const errors = [];
        
        // Validate file extension
        if (!this.validateExtension(file, imageType)) {
            const allowedExtensions = this.IMAGE_SPECS[imageType]?.allowedExtensions.join(', ') || '.jpg, .jpeg, .png';
            errors.push(`Invalid file extension. Allowed extensions: ${allowedExtensions}`);
        }
        
        // Validate file size
        if (!this.validateSize(file, imageType)) {
            const maxSizeKB = this.IMAGE_SPECS[imageType]?.maxFileSize / 1024 || 500;
            errors.push(`File size (${(file.size / 1024).toFixed(1)}KB) exceeds the maximum allowed (${maxSizeKB}KB)`);
        }
        
        // Validate dimensions
        const dimensionResult = await this.validateDimensions(file, imageType);
        if (!dimensionResult.isValid) {
            errors.push(dimensionResult.message);
        }
        
        return {
            isValid: errors.length === 0,
            errors
        };
    }

    /**
     * Create an image preview
     * @param {File} file - The image file
     * @param {HTMLElement} previewElement - The element to show the preview in
     */
    static createPreview(file, previewElement) {
        if (!file || !previewElement) return;
        
        const reader = new FileReader();
        reader.onload = (e) => {
            previewElement.innerHTML = `<img src="${e.target.result}" class="img-fluid rounded-3" alt="Preview">`;
        };
        reader.readAsDataURL(file);
    }
}
