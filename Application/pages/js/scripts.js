/*!
* Start Bootstrap - Heroic Features v5.0.6 (https://startbootstrap.com/template/heroic-features)
* Copyright 2013-2023 Start Bootstrap
* Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-heroic-features/blob/master/LICENSE)
*/
// This file is intentionally blank
// Use this file to add JavaScript to your project

function startAssessment() {
    // Clear any previous session data to ensure a fresh start
    sessionStorage.clear();
    console.log("Session storage cleared. Starting full assessment.");
    
    // Redirect to the first test: FAQ
    window.location.href = 'faq.html';
}
