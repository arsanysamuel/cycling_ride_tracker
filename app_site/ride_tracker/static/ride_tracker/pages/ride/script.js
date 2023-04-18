const LOCATIONINTERVAL = 1000;  // In Milliseconds
const EARTHRADIUS = 6367;  // Average in Km
const speedP = document.getElementById("speedP");
const totalTimeP = document.getElementById("totalTimeP");
const movingTimeP = document.getElementById("movingTimeP");
const startRideDiv = document.getElementById("startRideDiv");
const startRideBtn = document.getElementById("startRideBtn");
const stopRideDiv = document.getElementById("stopRideDiv");
const pauseRideBtn = document.getElementById("pauseRideBtn");
const resumeRideBtn = document.getElementById("resumeRideBtn");
const finishRideBtn = document.getElementById("finishRideBtn");
let geoIntervalId = null;
let totalTimeIntervalId = null;
let movingTimeIntervalId = null;
let totalSec = 0, movingSec = 0;
let ride;

function onGeoReading(position) {
    /* Get geolocation on rides every second */
    // Get speed
    let kph = (Math.round(position.coords.speed * 3600 / 100) / 10).toFixed(1);  // speed is in m/s by default
    document.getElementById("speedP").textContent = String(kph);

    // Get distance
    let prevPoint = localStorage.getItem(String(localStorage.getItem("pts") - 1));  // Get the last point recorded, susbtituting number from a string numerical gives a number
    let dist = 0.0;
    if (prevPoint) {  // is not null
        // Getting long and lat of points
        [lat2, long2] = [position.coords.latitude, position.coords.longitude];
        let prev = prevPoint.split("::");
        [lat1, long1] = [prev[0], prev[1]];

        // Calculating total distance with haversine formula (as the crow flies)
        // https://en.wikipedia.org/wiki/Haversine_formula#Formulation
        let newDist = 2 * EARTHRADIUS * Math.asin(Math.sqrt(
            Math.pow(Math.sin((lat2 - lat1) / 2), 2) + 
            Math.cos(lat1) * Math.cos(lat2) * Math.pow(Math.sin((long2 - long1) / 2), 2)
        ));
        dist = Math.round(newDist + Number(localStorage.getItem("dist")) * 100) / 100;  // Total distance rounded
    }
    document.getElementById("distanceP").textContent = String(dist.toFixed(1));  // Showing to the user
    localStorage.setItem("dist", String(dist));  // Storing value

    // Store longitude, latitude, timestamp inside localStorage
    localStorage.setItem(
        localStorage.getItem("pts"),
        `${position.coords.latitude}::${position.coords.longitude}::${position.timestamp}::${kph}`  // Storing lat,lon,timestamp in localStorage with :: as a delimiter
    );

    // Incrementing points counter
    let npts = Number(localStorage.getItem("pts"));
    localStorage.setItem("pts", String(npts + 1));
}

function formatTime(s) {
    // Convert number of seconds to formatted time
    let hours = String(Number.parseInt(s / 3600)).padStart(2, '0');
    let mins = String(Number.parseInt((s / 60) % 60)).padStart(2, '0');
    let secs = String(Number.parseInt(s % 60)).padStart(2, '0');
    return `${hours}:${mins}:${secs}`;
}


geoReadingHandler = () => {
    navigator.geolocation.getCurrentPosition(onGeoReading, onGeoError, geoOptions);  // onGeoError, geoOptions are defined on the global script
};

movingTimeHandler = () => {
    movingTimeP.textContent = formatTime(movingSec);
    movingSec++;
};

// Event handlers
startRideBtn.addEventListener("click", () => {
    // Switching divs
    startRideDiv.style.display = "none";
    stopRideDiv.style.display = "block";

    // localStorage initialization for a new ride
    localStorage.clear();
    localStorage.setItem("pts", "0");
    localStorage.setItem("dist", "0.0");

    // Getting location in frequency
    geoIntervalId = setInterval(geoReadingHandler, LOCATIONINTERVAL);

    // Starting time intervals
    totalTimeIntervalId = setInterval( () => {
        totalTimeP.textContent = formatTime(totalSec);
        totalSec++;
    }, 1000);
    movingTimeIntervalId = setInterval(movingTimeHandler, 1000);
});

pauseRideBtn.addEventListener("click", () => {
    // Switch buttons
    pauseRideBtn.style.display = "none";
    resumeRideBtn.style.display = "inline-block";

    // Stop moving time
    if (movingTimeIntervalId) {
        clearInterval(movingTimeIntervalId);
    }

    // Stop location reading
    if (geoIntervalId) {
        clearInterval(geoIntervalId);
    }

    // Zero the speedometer
    speedP.textContent = "0.0";
});

resumeRideBtn.addEventListener("click", () => {
    // Switch buttons
    pauseRideBtn.style.display = "inline-block";
    resumeRideBtn.style.display = "none";

    // starting location reading again
    geoIntervalId = setInterval(geoReadingHandler, LOCATIONINTERVAL);

    // Resume moving time
    movingTimeIntervalId = setInterval(movingTimeHandler, 1000);
});

finishRideBtn.addEventListener("click", () => {
    // Show loading overlay
    document.getElementById("loadingOverlay").style.display = "flex";

    // Stop all intervals
    if (geoIntervalId) {
        clearInterval(geoIntervalId);
    }
    if (totalTimeIntervalId) {
        clearInterval(totalTimeIntervalId);
    }
    if (movingTimeIntervalId) {
        clearInterval(movingTimeIntervalId);
    }

    // Creating object from data
    let pts = [];
    for (let i = 0; i < Number(localStorage.getItem("pts")); i++) {
        let pt = localStorage.getItem(`${i}`).split("::");
        pts[i] = {
            latitude: pt[0],
            longitude: pt[1],
            timestamp: pt[2] / 1000,  // JS to Python epochs
            speed: pt[3]
        }
    }

    ride = {
        distance: localStorage.getItem("dist"),
        movingSec: movingSec / 1000,  // JS milliseconds to Python seconds
        totalSec: totalSec / 1000,  // JS milliseconds to Python seconds
        pts: pts
    };
    localStorage.clear();  // Clear localStorage

    // Plot point on map
    plotRoute(ride.pts, "finishRideMap");

    // Show finish ride div
    document.getElementById("finishDiv").style.display = "block";
    document.getElementById("rideDiv").style.display = "none";
});

saveRideBtn.addEventListener("click", () => {
    // Show loading overlay
    document.getElementById("loadingOverlay").style.display = "flex";

    // Getting additional info
    ride.title = document.getElementById("rideTitle").value;
    ride.notes = document.getElementById("rideNotes").value;
    
    // Django CSRF: https://docs.djangoproject.com/en/4.1/howto/csrf/
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');

    // Send a request with the ride object: https://developer.mozilla.org/en-US/docs/Web/Guide/AJAX/Getting_Started
    const httpRequest = new XMLHttpRequest();
    httpRequest.onreadystatechange = () => {  // Server response handler
        if (httpRequest.readyState === XMLHttpRequest.DONE && httpRequest.status === 200) {
            window.location = "/";  // Redirect
        }
    };
    httpRequest.open("POST", finishRideUrl, true);
    httpRequest.setRequestHeader("Content-Type", "application/json")
    httpRequest.setRequestHeader('X-CSRFToken', csrftoken);  // Adding the CSRF token to request header
    httpRequest.send(JSON.stringify(ride));
});

deleteRideBtn.addEventListener("click", () => {
    // Clear localStorage and redirect
    localStorage.clear();
    window.location = "/";
});

