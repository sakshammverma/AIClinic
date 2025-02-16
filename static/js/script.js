document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('symptomForm');
    const resultsSection = document.getElementById('results');
    const diseaseElement = document.getElementById('disease');
    const descriptionElement = document.getElementById('description');
    const precautionsElement = document.getElementById('precautions');
    const medicationsElement = document.getElementById('medications');
    const workoutsElement = document.getElementById('workouts');
    const dietsElement = document.getElementById('diets');
    
    // Handle form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault(); // Prevent default form submission

        // Get the input value
        const symptomsInput = document.getElementById('symptoms');
        const symptoms = symptomsInput.value.trim();

        if (!symptoms) {
            alert("Please enter symptoms.");
            return;
        }

        // Show loading state
        diseaseElement.textContent = "Loading...";
        descriptionElement.textContent = "";
        precautionsElement.innerHTML = "";
        medicationsElement.innerHTML = "";
        workoutsElement.innerHTML = "";
        dietsElement.innerHTML = "";
        resultsSection.classList.remove('hidden');

        try {
            // Send POST request to the backend
            const response = await axios.post('/predict', { symptoms });

            // Handle the response
            const data = response.data;

            // Populate the results
            diseaseElement.textContent = data.disease || "No disease detected";
            descriptionElement.textContent = data.description || "No description available";
            precautionsElement.innerHTML = data.precautions?.map(item => `<li>${item}</li>`).join('') || "<li>No precautions available</li>";
            medicationsElement.innerHTML = data.medications?.map(item => `<li>${item}</li>`).join('') || "<li>No medications available</li>";
            workoutsElement.innerHTML = data.workouts?.map(item => `<li>${item}</li>`).join('') || "<li>No workouts available</li>";
            dietsElement.innerHTML = data.diets?.map(item => `<li>${item}</li>`).join('') || "<li>No diets available</li>";
        } catch (error) {
            console.error("Error fetching prediction:", error);
            diseaseElement.textContent = "An error occurred. Please try again.";
            resultsSection.classList.remove('hidden');
        }
    });
});
