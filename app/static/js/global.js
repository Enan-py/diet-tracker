/* global.js - Runs on EVERY page */

function updateGlobalProgress() {
    // 1. Get the data
    const stats = JSON.parse(localStorage.getItem('userStats'));
    const log = JSON.parse(localStorage.getItem('dailyLog'));
    const bar = document.getElementById('global-progress-fill');

    // 2. Safety Check: Do we have everything we need?
    if (!stats || !log || !bar) {
        if(bar) bar.style.width = "0%"; // Default to empty if no data
        return;
    }

    // Convert strings to numbers to prevent calculation errors
    const weight = parseFloat(stats.weight);
    const height = parseFloat(stats.height);
    const age = parseInt(stats.age);
    const activity = parseFloat(stats.activity);

    const bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5;
    const tdee = Math.round(bmr * activity);
    
    let target = tdee;
    if (stats.goal === 'lose') target = tdee - 500;
    else if (stats.goal === 'gain') target = tdee + 300;

    // 4. Update the width
    // We limit it to 100% so it doesn't overflow the screen
    const percent = Math.min((log.consumed / target) * 100, 100);
    
    bar.style.width = percent + "%";

    // Optional: Change color if they exceeded their goal (for weight loss)
    if (log.consumed > target && stats.goal === 'lose') {
        bar.style.backgroundColor = "#ff5252"; // Turn red if overeating
    }
}

// Run immediately when the page loads
document.addEventListener('DOMContentLoaded', updateGlobalProgress);