document.addEventListener("DOMContentLoaded", () => {
    const API = "http://127.0.0.1:8000";
    
    // Elements
    const foodQuery = document.getElementById("foodQuery");
    const searchResults = document.getElementById("search-results");
    const mealContainer = document.getElementById("meal-input-container");
    const calculateBtn = document.getElementById("calculateMeal");
    const summarySection = document.getElementById("meal-summary");
    
    // Custom Food Elements
    const customBtn = document.getElementById("addCustomBtn");
    const customForm = document.getElementById("custom-food-form");
    const saveCustomBtn = document.getElementById("saveCustom");

    let addedFoods = []; // Global list of selected items

    // --- 1. SEARCH LOGIC ---
    foodQuery.addEventListener("input", async (e) => {
        const query = e.target.value.trim();
        
        // 1. If empty, hide and stop
        if (query.length < 1) {
            searchResults.innerHTML = "";
            searchResults.classList.add("hidden");
            searchResults.style.display = "none";
            return;
        }

        try {
            // 2. Fetch data
            const res = await fetch(`${API}/food/search?query=${query}`);
            const foods = await res.json();
            
            // 3. Clear the box
            searchResults.innerHTML = "";

            if (foods.length > 0) {
                // 4. Build the list
                foods.forEach(food => {
                    const div = document.createElement("div");
                    div.className = "food-item";
                    div.style.padding = "12px"; // Force height
                    div.style.borderBottom = "1px solid #eee";
                    div.style.cursor = "pointer";
                    div.textContent = food.name;
                    
                    div.onclick = () => {
                        addFoodToUI(food);
                        foodQuery.value = "";
                        searchResults.classList.add("hidden");
                        searchResults.style.display = "none";
                    };
                    searchResults.appendChild(div);
                });

                // 5. FORCE VISIBILITY (The "Magic" fix)
                searchResults.classList.remove("hidden");
                searchResults.style.display = "block"; 
                searchResults.style.visibility = "visible";
                searchResults.style.opacity = "1";
            } else {
                searchResults.classList.add("hidden");
                searchResults.style.display = "none";
            }
        } catch (err) {
            console.error("Search error:", err);
        }
    });

    // --- 2. ADD CHIP TO UI ---
    function addFoodToUI(food) {
        const foodDiv = document.createElement("div");
        foodDiv.className = "food-entry";
        const uniqueId = Date.now().toString();
        foodDiv.dataset.id = uniqueId;

        foodDiv.innerHTML = `
            <span class="food-name">${food.name}</span>
            <input type="number" class="gram-input" value="100" min="1">
            <span class="unit">g</span>
            <span class="remove-btn">×</span>
        `;

        // Store reference
        const gramInput = foodDiv.querySelector(".gram-input");
        addedFoods.push({ id: food.id, name: food.name, gramInput, uniqueId });

        // Remove functionality
        foodDiv.querySelector(".remove-btn").onclick = () => {
            foodDiv.remove();
            addedFoods = addedFoods.filter(item => item.uniqueId !== uniqueId);
        };

        // Insert before search box
        const wrapper = document.querySelector(".search-wrapper");
        mealContainer.insertBefore(foodDiv, wrapper);
        gramInput.focus();
    }

    // --- 3. CALCULATE & SAVE MEAL ---
calculateBtn.onclick = async () => {
    if (addedFoods.length === 0) return alert("Add some food first!");

    // 1. Get user stats from the Info page (stored in localStorage)
    const savedStats = JSON.parse(localStorage.getItem('userStats'));
    
    let targetKcal = 2000; 
    let userGoal = "maintain"; 

    if (savedStats) {
        const bmr = (10 * savedStats.weight) + (6.25 * savedStats.height) - (5 * savedStats.age) + 5;
        const tdee = Math.round(bmr * parseFloat(savedStats.activity));
        userGoal = savedStats.goal;
        if (userGoal === 'lose') targetKcal = tdee - 500;
        else if (userGoal === 'gain') targetKcal = tdee + 300;
        else targetKcal = tdee;
    }

    // 2. Prepare the payload
    const payload = {
        foods: addedFoods.map(f => ({ 
            food_id: f.id, 
            grams: parseFloat(f.gramInput.value) 
        })),
        target_calories: targetKcal,
        goal: userGoal
    };

    try {
        const res = await fetch(`${API}/diet`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const data = await res.json();
        
        // --- 3. PERSISTENCE LOGIC (Building User Trust) ---
        const today = new Date().toDateString();
        let dailyLog = JSON.parse(localStorage.getItem('dailyLog')) || { 
            date: today, consumed: 0, protein: 0, carbs: 0, fat: 0 
        };

        // Reset if it's a new day
        if (dailyLog.date !== today) {
            dailyLog = { date: today, consumed: 0, protein: 0, carbs: 0, fat: 0 };
        }

        // Add current meal results to daily totals
        dailyLog.consumed += Math.round(data.calories);
        dailyLog.protein += Math.round(data.protein);
        dailyLog.carbs += Math.round(data.carbs);
        dailyLog.fat += Math.round(data.fat);

        // Save back to storage
        localStorage.setItem('dailyLog', JSON.stringify(dailyLog));

        // --- 4. UPDATE THE UI ---
        document.getElementById("total-calories").textContent = data.calories;
        document.getElementById("total-protein").textContent = data.protein + "g";
        document.getElementById("total-carbs").textContent = data.carbs + "g";
        document.getElementById("total-fat").textContent = data.fat + "g";
        document.getElementById("meal-advice").textContent = data.advice;
        
        // Show the summary section
        document.getElementById("meal-summary").classList.remove("hidden");

        // Update the global progress bar if it exists
        if (typeof updateGlobalProgress === "function") {
            updateGlobalProgress();
        }

        alert("Success! Your meal has been logged for today.");

        // Clear the input area for the next meal
        const chips = mealContainer.querySelectorAll('.food-entry');
        chips.forEach(chip => chip.remove());
        addedFoods = [];

    } catch (error) {
        console.error("Calculation error:", error);
        alert("Failed to calculate diet. Is the backend running?");
    }
};
    // Custom Form Toggle
    customBtn.onclick = () => customForm.classList.toggle("hidden");
    
    saveCustomBtn.onclick = async () => {
        const payload = {
            name: document.getElementById("customName").value,
            calories_per_100g: +document.getElementById("customCalories").value,
            protein_per_100g: +document.getElementById("customProtein").value,
            carbs_per_100g: +document.getElementById("customCarbs").value,
            fat_per_100g: +document.getElementById("customFat").value
        };
        await fetch(`${API}/food/custom`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        alert("Food Saved!");
        customForm.classList.add("hidden");
    };
});

// -------------------- FUTURE PAGE PLACEHOLDERS --------------------
// Example for summary page
if (document.getElementById("summary-section")) {
  // Add summary page JS here later
}

// Example for goals page
if (document.getElementById("goals-section")) {
  // Add goals page JS here later
}

// Example for index page
if (document.getElementById("index-section")) {
  // Add index page JS here later
}
