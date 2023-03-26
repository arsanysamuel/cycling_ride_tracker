const indexMap = L.map("indexMap");
const indexMapMarker = L.marker();

function onLocationSuccess(position) {
    /* Plot map and show user location on it on index page */
    // Get coordinates: https://developer.mozilla.org/en-US/docs/Web/API/Geolocation_API/Using_the_Geolocation_API
    let latitude = position.coords.latitude;
    let longitude = position.coords.longitude;

    // Embed map to page with a location marker: https://leafletjs.com/examples/quick-start/
    indexMap.setView([latitude, longitude], 16);
    indexMapMarker.setLatLng([latitude, longitude]).addTo(indexMap);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(indexMap);
}

navigator.geolocation.watchPosition(onLocationSuccess, onGeoError, geoOptions);  // onGeoError, geoOptions defined in global script
