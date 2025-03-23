document.addEventListener("DOMContentLoaded", function () {
    let currentStep = 1;
    const totalSteps = document.querySelectorAll('.form-step').length;

    const nextBtn = document.getElementById("nextBtn");
    const prevBtn = document.getElementById("prevBtn");

    // Function to show the current step
    function showStep(step) {
        document.querySelectorAll(".form-step").forEach((el) => el.classList.remove("active"));
        document.querySelector(`[data-step="${step}"]`).classList.add("active");

        // Manage buttons visibility
        prevBtn.disabled = step === 1;
        nextBtn.textContent = step === totalSteps ? "Submit" : "Next";
    }

    // Validate current step before proceeding
    function validateStep(step) {
        const currentStepElement = document.querySelector(`[data-step="${step}"]`);
        const requiredInputs = currentStepElement.querySelectorAll("input[required], textarea[required], select[required]");
        let isValid = true;

        requiredInputs.forEach((input) => {
            if (!input.value.trim()) {
                isValid = false;
                input.classList.add("error");
            } else {
                input.classList.remove("error");
            }
        });

        if (!isValid) alert("Please fill out all required fields.");
        return isValid;
    }

    // Handle Next button click
    nextBtn.addEventListener("click", function () {
        if (currentStep < totalSteps) {
            if (validateStep(currentStep)) {
                currentStep++;
                showStep(currentStep);
            }
        } else {
            submitForm();
        }
    });

    // Handle Previous button click
    prevBtn.addEventListener("click", function () {
        if (currentStep > 1) {
            currentStep--;
            showStep(currentStep);
        }
    });

    // Function to submit the form
    function submitForm() {
        const formData = new FormData(document.getElementById("medicalHistoryForm"));
        const data = {};
        formData.forEach((value, key) => {
            data[key] = value;
        });

        console.log("Form Data:", data);
        alert("Form submitted successfully!");

        // Retrieve the URL from the hidden input
        const indexUrl = document.getElementById("indexUrl").value;
        window.location.href = indexUrl; // Redirect to index.html after submission
    }

    // Handle "Other" checkbox logic
    const otherCheckbox = document.getElementById("otherCheckbox");
    if (otherCheckbox) {
        otherCheckbox.addEventListener("change", function () {
            document.getElementById("otherInput").disabled = !this.checked;
        });
    }

    // Initialize first step
    showStep(currentStep);
});