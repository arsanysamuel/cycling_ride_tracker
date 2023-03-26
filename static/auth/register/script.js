const regPass = document.getElementById("regPass");
const regRePass = document.getElementById("regRePass");
const registerBtn = document.getElementById("registerBtn");

// Check if password fields match
registerBtn.addEventListener("click", function() {
    if (regPass.value !== regRePass.value) {
        regRePass.setCustomValidity("Passwords mismatch!");  // Prevent from submitting
    } else {
        regRePass.setCustomValidity("");
    }
});
