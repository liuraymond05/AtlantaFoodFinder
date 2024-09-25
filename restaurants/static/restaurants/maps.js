let map;
let markers = [];

function initMap() {
    map = new google.maps.Map(document.getElementById("map"), {
        center: { lat: 33.749, lng: -84.388 },  // Atlanta
        zoom: 12,
    });

    // Example restaurant data (replace this with your real data)
    const restaurants = [
        {
            name: "Restaurant 1",
            latitude: 33.753746,
            longitude: -84.386330,
            rating: 4.5,
            address: "123 Main St, Atlanta, GA",
            reviews: "Great food, nice atmosphere."
        },
        {
            name: "Restaurant 2",
            latitude: 33.759598,
            longitude: -84.389868,
            rating: 4.0,
            address: "456 Broad St, Atlanta, GA",
            reviews: "Lovely staff and delicious meals."
        },
    ];

    // Place markers for restaurants
    restaurants.forEach(restaurant => {
        addRestaurantMarker(restaurant);
    });
}

function addRestaurantMarker(restaurant) {
    const marker = new google.maps.Marker({
        position: { lat: restaurant.latitude, lng: restaurant.longitude },
        map: map,
        title: restaurant.name,
    });

    const infoWindow = new google.maps.InfoWindow({
        content: `
            <h3>${restaurant.name}</h3>
            <p>Rating: ${restaurant.rating}</p>
            <p>Address: ${restaurant.address}</p>
            <p>Reviews: ${restaurant.reviews}</p>
        `,
    });

    // Show restaurant details when marker is clicked
    marker.addListener('click', () => {
        infoWindow.open(map, marker);
    });

    markers.push(marker);
}

// Clear existing markers from the map
function clearMarkers() {
    markers.forEach(marker => marker.setMap(null));
    markers = [];
}

window.initMap = initMap;
// Event handler for clicking on a suggested place.
async function onPlaceSelected(place) {
    // Fetch fields for the selected place, including the name and address
    await place.fetchFields({
        fields: ["displayName", "formattedAddress", "geometry"],
    });

    // Create the text to show the selected eatery details.
    let placeText = document.createTextNode(
        place.displayName + ": " + place.formattedAddress,
    );

    // Update the results with the selected eatery.
    results.replaceChildren(placeText);
    title.innerText = "Selected Eatery:";
    input.value = "";

    // If the place has valid geometry (latitude and longitude), place a marker on the map.
    if (place.geometry && place.geometry.location) {
        const latLng = place.geometry.location;

        // Create a marker for the selected place.
        const marker = new google.maps.Marker({
            position: latLng,
            map: map,
            title: place.displayName,
        });

        // Optionally, add an InfoWindow with more details about the place.
        const infoWindow = new google.maps.InfoWindow({
            content: `<h3>${place.displayName}</h3>
                      <p>Address: ${place.formattedAddress}</p>`,
        });

        // Add an event listener to open the InfoWindow when the marker is clicked.
        marker.addListener('click', () => {
            infoWindow.open(map, marker);
        });

        // Center the map on the selected place.
        map.setCenter(latLng);
        map.setZoom(15);

        // If desired, store the marker in an array or use it for future references.
        allMarkers.push(marker);
    } else {
        alert('Location details are not available for this place.');
    }

    refreshToken(request);
}
