function initMap() {
    const mapOptions = {
        zoom: 12,
        center: { lat: 33.7490, lng: -84.3880 }, // Atlanta coordinates
    };

    const map = new google.maps.Map(document.getElementById('map'), mapOptions);

    // Sample list of restaurants with geolocation
    const restaurants = [
        { id: 1, name: 'Restaurant 1', lat: 33.753746, lng: -84.386330 },
        { id: 2, name: 'Restaurant 2', lat: 33.7550, lng: -84.3900 },
    ];

    restaurants.forEach((restaurant) => {
        const marker = new google.maps.Marker({
            position: { lat: restaurant.lat, lng: restaurant.lng },
            map: map,
            title: restaurant.name,
        });

        marker.addListener('click', function() {
            saveFavorite(restaurant.id);
        });
    });
}


function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}