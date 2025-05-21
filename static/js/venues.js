// Venues App JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize carousels with a slight delay between slides
    const carousels = document.querySelectorAll('.carousel');
    carousels.forEach(carousel => {
        new bootstrap.Carousel(carousel, {
            interval: 5000
        });
    });

    // Handle search form submission
    const searchForm = document.getElementById('search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            const searchInput = document.getElementById('search-input');
            if (searchInput.value.trim() === '') {
                e.preventDefault();
                searchInput.focus();
            }
        });
    }

    // Handle filter form changes for venue listing page
    const filterForms = document.querySelectorAll('form[action*="venue_list"]');
    filterForms.forEach(filterForm => {
        const filterSelects = filterForm.querySelectorAll('select');
        filterSelects.forEach(select => {
            select.addEventListener('change', function() {
                // Don't auto-submit on mobile to avoid unexpected page reloads
                if (window.innerWidth >= 768) {
                    filterForm.submit();
                }
            });
        });
    });

    // Add hover effects to venue cards
    const venueCards = document.querySelectorAll('.service-card');
    venueCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.classList.add('shadow-lg');
            this.style.transform = 'translateY(-5px)';
            this.style.transition = 'transform 0.3s ease, box-shadow 0.3s ease';
        });

        card.addEventListener('mouseleave', function() {
            this.classList.remove('shadow-lg');
            this.style.transform = 'translateY(0)';
        });
    });

    // Initialize filter form elements
    initializeFilterForm();

    // Initialize map if venue has coordinates
    initializeMap();
});

// Function to initialize map on venue detail page
function initializeMap() {
    const mapContainer = document.querySelector('.venue-map');
    if (!mapContainer) return;

    // This is a placeholder for actual map implementation
    // In a real application, you would use Google Maps, Leaflet, or another mapping library
    mapContainer.innerHTML = `
        <div class="d-flex align-items-center justify-content-center h-100 bg-light">
            <p class="text-center">
                <i class="bi bi-map fs-1 text-primary"></i><br>
                Map would be displayed here with the venue location.<br>
                <small class="text-muted">Implement with Google Maps or Leaflet in production.</small>
            </p>
        </div>
    `;
}

// Function to initialize filter form elements
function initializeFilterForm() {
    // Make sure location_search.js is loaded and working
    const stateInput = document.getElementById('id_state');
    const countyInput = document.getElementById('id_county');
    const cityInput = document.getElementById('id_city');

    // If any of these inputs exist but their datalists don't, create them
    if (stateInput && !document.getElementById('stateList')) {
        const datalist = document.createElement('datalist');
        datalist.id = 'stateList';
        document.body.appendChild(datalist);

        // Fetch all states
        fetch('/venues/api/location-data/')
            .then(response => response.json())
            .then(data => {
                // Add options
                if (data.states) {
                    data.states.forEach(state => {
                        const option = document.createElement('option');
                        option.value = state;
                        datalist.appendChild(option);
                    });
                }
            })
            .catch(error => console.error('Error fetching states:', error));
    }

    if (countyInput && !document.getElementById('countyList')) {
        const datalist = document.createElement('datalist');
        datalist.id = 'countyList';
        document.body.appendChild(datalist);
    }

    if (cityInput && !document.getElementById('cityList')) {
        const datalist = document.createElement('datalist');
        datalist.id = 'cityList';
        document.body.appendChild(datalist);
    }
}
