let map;
let allMarkers = [];
let userLocation = null;
let service;
let title;
let results;
let input;
let token;

// Initial request body for autocomplete
let request = {
    input: "",
    locationRestriction: {
        west: -122.44,
        north: 37.8,
        east: -122.39,
        south: 37.78,
    },
    origin: { lat: 33.749, lng: -84.388 }, // Atlanta coordinates
    includedPrimaryTypes: ["restaurant"],
    language: "en-US",
    region: "us",
};

async function init() {
    token = new google.maps.places.AutocompleteSessionToken();
    title = document.getElementById("title");
    results = document.getElementById("results");
    input = document.getElementById("searchName");
    input.addEventListener("input", makeAcRequest);
    request = refreshToken(request);

    const location = { lat: 33.749, lng: -84.388 }; // Atlanta coordinates
    map = new google.maps.Map(document.getElementById('map'), {
        center: location,
        zoom: 12,
        disableDefaultUI: true,
    });

    // Initialize the Places service
    service = new google.maps.places.PlacesService(map);
}

// Function to fetch autocomplete suggestions
async function makeAcRequest(event) {
    if (event.target.value == "") {
        title.innerText = "";
        results.replaceChildren();
        return;
    }

    request.input = event.target.value;

    const { suggestions } =
        await google.maps.places.AutocompleteSuggestion.fetchAutocompleteSuggestions(request);

    title.innerText = 'Query predictions for "' + request.input + '"';
    results.replaceChildren();

    for (const suggestion of suggestions) {
        const placePrediction = suggestion.placePrediction;
        const a = document.createElement("a");
        a.addEventListener("click", () => {
            onPlaceSelected(placePrediction.toPlace());
        });
        a.innerText = placePrediction.text.toString();

        const li = document.createElement("li");
        li.appendChild(a);
        results.appendChild(li);
    }
}

// Event handler for clicking on a suggested place
async function onPlaceSelected(place) {
    try {
        await place.fetchFields({
            fields: ["displayName", "formattedAddress", "geometry", "placeId"],
        });

        // Update the UI with the selected eatery details
        const placeText = document.createTextNode(
            `${place.displayName}: ${place.formattedAddress}`
        );

        results.replaceChildren(placeText);
        title.innerText = "Selected Eatery:";
        input.value = ""; // Clear the input field

        // Fetch additional restaurant details from the backend
        const response = await fetch(`/get_restaurant_data/?id=${place.placeId}`);
        if (!response.ok) {
            throw new Error('Failed to fetch restaurant details.');
        }

        const restaurant = await response.json();

        if (place.geometry && place.geometry.location) {
            const latLng = place.geometry.location;

            // Create a marker for the selected place
            const marker = new google.maps.Marker({
                position: latLng,
                map: map,
                title: restaurant.name,
            });

            // Create an InfoWindow for the marker
            const infoWindow = new google.maps.InfoWindow({
                content: `
                    <h3>${restaurant.name}</h3>
                    <p>Rating: ${restaurant.rating}</p>
                    <p>Address: ${restaurant.address}</p>
                    <p>Reviews: ${restaurant.reviews}</p>
                `,
            });

            // Show InfoWindow when marker is clicked
            marker.addListener('click', () => {
                infoWindow.open(map, marker);
            });

            // Center the map on the selected place
            map.setCenter(latLng);
            map.setZoom(15);

            // Store the marker for future reference
            allMarkers.push(marker); // Store dynamically created markers
        } else {
            alert('Location details are not available for this place.');
        }

        refreshToken(request);
    } catch (error) {
        console.error('Error selecting place:', error);
        alert('Failed to select place. Please try again.');
    }
}


// Function to filter restaurants based on user input
function filterRestaurants() {
    const nameInput = document.getElementById('searchName').value.toLowerCase();
    const cuisineInput = document.getElementById('searchCuisine').value.toLowerCase();
    const ratingInput = parseFloat(document.getElementById('searchRating').value) || 0;
    const distanceInput = parseFloat(document.getElementById('searchDistance').value) || Infinity;

    allMarkers.forEach(marker => {
        const matchesName = marker.title.toLowerCase().includes(nameInput);

        // Show or hide markers based on the filter criteria
        if (matchesName) {
            marker.setMap(map);
        } else {
            marker.setMap(null);
        }
    });
}

// Helper function to refresh the session token
async function refreshToken(request) {
    token = new google.maps.places.AutocompleteSessionToken();
    request.sessionToken = token;
    return request;
}

// Initialize the Google Maps API
window.initMap = init;
