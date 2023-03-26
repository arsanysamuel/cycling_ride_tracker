/* --------- Globals ---------- */
const navLinks = document.getElementsByClassName("nav-link");

// Activate navigation current link item for layout
if (navLinks) {  // if the navlinks exist
    for (let i = 0; i < navLinks.length; i++) {
        if (navLinks[i].pathname == window.location.pathname) {
            navLinks[i].classList.add("active")
        }
    }
}

// Geolocation options: https://developer.mozilla.org/en-US/docs/Web/API/Geolocation/getCurrentPosition
const geoOptions = {
    maximumAge: 100,  // Milliseconds
    enableHighAccuracy: true,
}

function onGeoError(err) {
    /* Display alert in case of location fetching faliure */
    alert(`Error parsing your location, make sure you've enabled the location service access.\n${err.message}`)
}

function plotRoute(ridePts, mapId) {
    /* Plot route from localStorage points on map */
    let mapElement = L.map(mapId);

    // Put points into array
    let pts = [];
    for (let i = 0; i < ridePts.length; i++) {
        pts[i] = [ridePts[i].latitude, ridePts[i].longitude];
    }

    // https://leafletjs.com/reference.html#polyline
    let route = L.polyline(pts, {color: "red"});
    route.addTo(mapElement);
    let bounds = route.getBounds();
    if (Object.keys(bounds).length > 0) {
        mapElement.fitBounds(route.getBounds());
    } else {
        let placeholder = document.createElement("h4");
        placeholder.classList.add("my-5");
        placeholder.innerText = "No route was logged, it looks like you're standing still.";
        document.getElementById("rideContentDiv").replaceWith(placeholder);
        document.getElementById("saveRideBtn").style.display = "none";
    }

    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(mapElement);

    // Disable all interactions with the map
    mapElement.dragging.disable();
    mapElement.touchZoom.disable();
    mapElement.doubleClickZoom.disable();
    mapElement.scrollWheelZoom.disable();
    mapElement.boxZoom.disable();
    mapElement.keyboard.disable()
}

