/**
 * Location search and autocomplete functionality for CozyWish
 */

document.addEventListener('DOMContentLoaded', function() {
    // Location search autocomplete
    const locationInput = document.getElementById('id_location');
    const locationList = document.getElementById('locationList');
    
    if (locationInput) {
        // Create datalist if it doesn't exist
        if (!locationList) {
            const datalist = document.createElement('datalist');
            datalist.id = 'locationList';
            document.body.appendChild(datalist);
        }
        
        // Add event listener for input changes
        locationInput.addEventListener('input', function() {
            const query = this.value.trim();
            
            if (query.length >= 2) {
                // Fetch location suggestions
                fetch(`/venues/api/location-suggestions/?query=${encodeURIComponent(query)}`)
                    .then(response => response.json())
                    .then(data => {
                        // Clear existing options
                        locationList.innerHTML = '';
                        
                        // Add new options
                        data.suggestions.forEach(suggestion => {
                            const option = document.createElement('option');
                            option.value = suggestion.text;
                            option.dataset.id = suggestion.id;
                            option.dataset.city = suggestion.city;
                            option.dataset.state = suggestion.state;
                            option.dataset.county = suggestion.county;
                            locationList.appendChild(option);
                        });
                    })
                    .catch(error => console.error('Error fetching location suggestions:', error));
            }
        });
    }
    
    // State, county, city dropdowns for venue form
    const stateInput = document.getElementById('id_state');
    const countyInput = document.getElementById('id_county');
    const cityInput = document.getElementById('id_city');
    const usCityIdInput = document.getElementById('id_us_city_id');
    
    // Create datalists if they don't exist
    if (stateInput && !document.getElementById('stateList')) {
        const datalist = document.createElement('datalist');
        datalist.id = 'stateList';
        document.body.appendChild(datalist);
        
        // Fetch all states
        fetch('/venues/api/location-data/')
            .then(response => response.json())
            .then(data => {
                // Add options
                data.states.forEach(state => {
                    const option = document.createElement('option');
                    option.value = state;
                    datalist.appendChild(option);
                });
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
    
    // Add event listeners for state and county changes
    if (stateInput) {
        stateInput.addEventListener('change', function() {
            const state = this.value.trim();
            
            if (state) {
                // Fetch counties for the selected state
                fetch(`/venues/api/location-data/?state=${encodeURIComponent(state)}`)
                    .then(response => response.json())
                    .then(data => {
                        // Clear existing options
                        const countyList = document.getElementById('countyList');
                        countyList.innerHTML = '';
                        
                        // Add new options
                        data.counties.forEach(county => {
                            const option = document.createElement('option');
                            option.value = county;
                            countyList.appendChild(option);
                        });
                        
                        // Clear city input
                        if (cityInput) {
                            cityInput.value = '';
                        }
                    })
                    .catch(error => console.error('Error fetching counties:', error));
            }
        });
    }
    
    if (countyInput) {
        countyInput.addEventListener('change', function() {
            const state = stateInput.value.trim();
            const county = this.value.trim();
            
            if (state && county) {
                // Fetch cities for the selected state and county
                fetch(`/venues/api/location-data/?state=${encodeURIComponent(state)}&county=${encodeURIComponent(county)}`)
                    .then(response => response.json())
                    .then(data => {
                        // Clear existing options
                        const cityList = document.getElementById('cityList');
                        cityList.innerHTML = '';
                        
                        // Add new options
                        data.cities.forEach(city => {
                            const option = document.createElement('option');
                            option.value = city;
                            cityList.appendChild(option);
                        });
                    })
                    .catch(error => console.error('Error fetching cities:', error));
            }
        });
    }
    
    // When a city is selected, try to find the matching US city
    if (cityInput) {
        cityInput.addEventListener('change', function() {
            const state = stateInput.value.trim();
            const county = countyInput.value.trim();
            const city = this.value.trim();
            
            if (state && city) {
                // Find the matching US city
                fetch(`/venues/api/location-suggestions/?query=${encodeURIComponent(city + ' ' + state)}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.suggestions.length > 0) {
                            // Find the best match
                            const match = data.suggestions.find(s => 
                                s.city.toLowerCase() === city.toLowerCase() && 
                                (s.state.toLowerCase() === state.toLowerCase() || s.state_id.toLowerCase() === state.toLowerCase())
                            );
                            
                            if (match && usCityIdInput) {
                                usCityIdInput.value = match.id;
                            }
                        }
                    })
                    .catch(error => console.error('Error finding US city:', error));
            }
        });
    }
});
