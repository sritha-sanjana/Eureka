let currentStep = 1;
const totalSteps = 4;
let teamSize = 2; // Default team size

function getApiBaseUrl() {
    if (window.location.port === "8000" || window.location.port === "8080") {
        return "";
    }

    return "http://127.0.0.1:8000";
}

// Initialize the form on page load
document.addEventListener("DOMContentLoaded", () => {
    updateStepper();
    renderTeamMembersInput();
});

// Stepper visual updates
function updateStepper() {
    // Update step nodes
    document.querySelectorAll(".step-node").forEach(node => {
        const stepNum = parseInt(node.getAttribute("data-step"));
        node.classList.remove("active", "completed");
        
        if (stepNum === currentStep) {
            node.classList.add("active");
        } else if (stepNum < currentStep) {
            node.classList.add("completed");
        }
    });

    // Update progress bar width
    const progressPercent = ((currentStep - 1) / (totalSteps - 1)) * 100;
    document.getElementById("stepper-progress").style.width = `${progressPercent}%`;

    // Toggle Form Step views
    document.querySelectorAll(".form-step").forEach(step => {
        step.classList.remove("active");
        if (parseInt(step.getAttribute("data-step")) === currentStep) {
            step.classList.add("active");
        }
    });

    // Handle button availability
    const btnBack = document.getElementById("btn-back");
    const btnNext = document.getElementById("btn-next");

    if (currentStep === 1) {
        btnBack.disabled = true;
        btnBack.style.opacity = "0.5";
        btnBack.style.cursor = "not-allowed";
    } else {
        btnBack.disabled = false;
        btnBack.style.opacity = "1";
        btnBack.style.cursor = "pointer";
    }

    if (currentStep === totalSteps) {
        btnNext.innerHTML = `Submit Application <i class="fa-solid fa-paper-plane"></i>`;
        btnNext.style.background = "linear-gradient(135deg, #10b981, #059669)"; // Green color on last step
    } else {
        btnNext.innerHTML = `Next <i class="fa-solid fa-arrow-right"></i>`;
        btnNext.style.background = ""; // Restore default theme gradient
    }
}

// Check validation of inputs in the active step
function validateStep(step) {
    let isValid = true;
    const activeStepView = document.querySelector(`.form-step[data-step="${step}"]`);
    const inputs = activeStepView.querySelectorAll("input[required], select[required], textarea[required]");

    // Reset old errors
    activeStepView.querySelectorAll(".error-msg-inline").forEach(el => el.remove());
    activeStepView.querySelectorAll(".input-error").forEach(el => el.classList.remove("input-error"));

    inputs.forEach(input => {
        // Skip validation if input parent is hidden (e.g. conditional fields)
        let parent = input.parentElement;
        let isHidden = false;
        while (parent && parent.tagName !== "FORM") {
            if (parent.style.display === "none") {
                isHidden = true;
                break;
            }
            parent = parent.parentElement;
        }
        if (isHidden) return;

        let errorText = "";

        if (!input.value.trim()) {
            errorText = "This field is required.";
        } else if (input.type === "email" && !validateEmailRegex(input.value)) {
            errorText = "Please enter a valid email address.";
        } else if (input.type === "tel") {
            const digits = input.value.replace(/\D/g, "");
            if (digits.length !== 10) {
                errorText = "Phone number must be exactly 10 digits.";
            }
        } else if (input.tagName === "TEXTAREA" && input.value.trim().length < 10) {
            errorText = "Please write a minimum of 10 characters.";
        }

        if (errorText) {
            isValid = false;
            input.classList.add("input-error");
            
            const errorDiv = document.createElement("div");
            errorDiv.className = "error-msg error-msg-inline";
            errorDiv.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i> ${errorText}`;
            input.parentElement.appendChild(errorDiv);
        }
    });

    // Custom check for file upload on Step 4
    if (step === 4) {
        const hasPitchChoice = document.querySelector('input[name="has_pitch_deck_choice"]:checked').value === "yes";
        const fileInput = document.getElementById("pitch_file");
        if (hasPitchChoice && !fileInput.files.length) {
            isValid = false;
            const container = document.querySelector(".upload-container");
            container.style.borderColor = "var(--error)";
            
            let fileErr = document.getElementById("file-error-missing");
            if (!fileErr) {
                fileErr = document.createElement("div");
                fileErr.id = "file-error-missing";
                fileErr.className = "error-msg";
                fileErr.style.marginTop = "0.75rem";
                fileErr.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i> Please select a PDF file to upload.`;
                container.parentElement.appendChild(fileErr);
            }
        }
    }

    return isValid;
}

function validateEmailRegex(email) {
    const re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(String(email).toLowerCase());
}

// Stepper Navigation
function navigateStep(direction) {
    // If going forward, validate current step first
    if (direction === 1) {
        if (!validateStep(currentStep)) {
            // Scroll to the first error input
            const firstError = document.querySelector(".input-error");
            if (firstError) {
                firstError.scrollIntoView({ behavior: "smooth", block: "center" });
            }
            return;
        }
    }

    if (direction === 1 && currentStep === totalSteps) {
        // Last step submit is handled via submitForm() trigger on button click
        document.getElementById("registration-form").requestSubmit();
        return;
    }

    currentStep += direction;
    updateStepper();
    window.scrollTo({ top: 150, behavior: "smooth" });
}

// Team Member size selection counter updates
function adjustTeamSize(change) {
    const newSize = teamSize + change;
    if (newSize >= 2 && newSize <= 5) {
        teamSize = newSize;
        document.getElementById("team-size-display").innerText = teamSize;
        renderTeamMembersInput();
    }
}

// Render inputs for other team members dynamically
function renderTeamMembersInput() {
    const container = document.getElementById("dynamic-members-container");
    container.innerHTML = ""; // Clear existing

    // Loop from 2 to teamSize (e.g. if team size is 3, render member 2 and member 3 inputs)
    for (let i = 2; i <= teamSize; i++) {
        const memberCard = document.createElement("div");
        memberCard.className = "team-member-block";
        memberCard.innerHTML = `
            <div class="team-member-title">
                <span><i class="fa-solid fa-user-group"></i> Team Member ${i}</span>
            </div>
            
            <div class="form-group">
                <label for="m${i}_name">Full Name <span>*</span></label>
                <input type="text" id="m${i}_name" class="input-field" placeholder="Enter member ${i}'s name" required>
            </div>

            <div class="form-row">
                <div class="form-group">
                    <label for="m${i}_email">Email Address <span>*</span></label>
                    <input type="email" id="m${i}_email" class="input-field" placeholder="member${i}@college.edu" required>
                </div>
                <div class="form-group">
                    <label for="m${i}_phone">Phone Number <span>*</span></label>
                    <input type="tel" id="m${i}_phone" class="input-field" placeholder="e.g. 9876543210" required>
                </div>
            </div>

            <div class="form-row">
                <div class="form-group">
                    <label for="m${i}_college">College Name <span>*</span></label>
                    <input type="text" id="m${i}_college" class="input-field" placeholder="College / University Name" required>
                </div>
                <div class="form-group">
                    <label for="m${i}_bank_account">Bank Account Number</label>
                    <input type="text" id="m${i}_bank_account" class="input-field" placeholder="Optional account number">
                </div>
            </div>
        `;
        container.appendChild(memberCard);
    }
}

// Conditional fields toggles
function toggleExistingStartupFields(show) {
    const block = document.getElementById("existing-startup-fields");
    block.style.display = show ? "block" : "none";
    
    // Add required attributes if shown to trigger validation
    document.getElementById("startup_website").required = false; // keep website optional
}

function togglePitchDeckField(show) {
    const block = document.getElementById("pitch-deck-upload-field");
    block.style.display = show ? "block" : "none";
    
    // Reset file validations
    const container = document.querySelector(".upload-container");
    container.style.borderColor = "";
    const fileErr = document.getElementById("file-error-missing");
    if (fileErr) fileErr.remove();
}

// PDF file selector changes
function handleFileSelected(input) {
    const file = input.files[0];
    const statusText = document.getElementById("upload-status-text");
    const fileError = document.getElementById("file-error");
    const container = document.querySelector(".upload-container");
    
    // Reset indicators
    fileError.style.display = "none";
    container.style.borderColor = "";
    const fileErr = document.getElementById("file-error-missing");
    if (fileErr) fileErr.remove();

    if (!file) {
        statusText.innerHTML = `<span>Click to select</span> or drag PDF file here`;
        return;
    }

    // Check type is PDF
    if (file.type !== "application/pdf" && !file.name.toLowerCase().endsWith(".pdf")) {
        fileError.style.display = "flex";
        statusText.innerHTML = `<span>Click to select</span> or drag PDF file here`;
        input.value = ""; // clear selected
        return;
    }

    // Check size < 10MB
    const maxBytes = 10 * 1024 * 1024;
    if (file.size > maxBytes) {
        fileError.innerText = "File size exceeds the 10 MB maximum allowed limit.";
        fileError.style.display = "flex";
        statusText.innerHTML = `<span>Click to select</span> or drag PDF file here`;
        input.value = ""; // clear
        return;
    }

    // Success display file name
    statusText.innerHTML = `<i class="fa-solid fa-file-pdf" style="color: var(--error); margin-right: 0.5rem;"></i> <strong>${file.name}</strong> (${(file.size / (1024 * 1024)).toFixed(2)} MB)`;
    container.style.borderColor = "var(--success)";
}

// Drag and drop file uploads
const dropZone = document.querySelector(".upload-container");
if (dropZone) {
    ["dragenter", "dragover"].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            dropZone.style.borderColor = "var(--primary)";
        }, false);
    });

    ["dragleave", "drop"].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            dropZone.style.borderColor = "";
        }, false);
    });

    dropZone.addEventListener("drop", (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        const fileInput = document.getElementById("pitch_file");
        
        if (files.length) {
            fileInput.files = files;
            handleFileSelected(fileInput);
        }
    });
}

// Submit forms to endpoint REST api
async function submitForm(event) {
    event.preventDefault();

    if (!validateStep(currentStep)) return;

    // Show loading overlay
    const loader = document.getElementById("loader-overlay");
    loader.style.display = "flex";

    // 1. Gather Team Lead Details (from Step 1)
    const teamMembers = [{
        name: document.getElementById("lead_name").value,
        email: document.getElementById("lead_email").value,
        phone: document.getElementById("lead_phone").value,
        college: document.getElementById("lead_college").value,
        department: document.getElementById("lead_department").value,
        year: document.getElementById("lead_year").value,
        bank_account: document.getElementById("lead_bank_account").value,
        is_lead: true
    }];

    // 2. Gather Other Dynamic Team Members (from Step 3)
    for (let i = 2; i <= teamSize; i++) {
        teamMembers.push({
            name: document.getElementById(`m${i}_name`).value,
            email: document.getElementById(`m${i}_email`).value,
            phone: document.getElementById(`m${i}_phone`).value,
            college: document.getElementById(`m${i}_college`).value,
            department: "", // Optional for other members
            year: "",       // Optional for other members
            bank_account: document.getElementById(`m${i}_bank_account`).value || "",
            is_lead: false
        });
    }

    const isExisting = document.querySelector('input[name="is_existing_startup"]:checked').value === "yes";
    const hasPitch = document.querySelector('input[name="has_pitch_deck_choice"]:checked').value === "yes";

    // 3. Construct Registration JSON body
    const registrationJson = {
        startup_name: document.getElementById("startup_name").value,
        category: document.getElementById("startup_category").value,
        stage: document.getElementById("startup_stage").value,
        description: document.getElementById("startup_description").value,
        problem_statement: document.getElementById("problem_statement").value,
        solution: document.getElementById("solution_details").value,
        is_existing: isExisting,
        website: isExisting ? document.getElementById("startup_website").value : null,
        current_stage: isExisting ? document.getElementById("startup_stage").value : null, // stage choice
        team_size: teamSize,
        revenue: isExisting ? document.getElementById("existing_revenue").value : null,
        registration_details: isExisting ? document.getElementById("existing_details").value : null,
        has_pitch_deck: hasPitch,
        team_members: teamMembers
    };

    // 4. Form Multipart Form Data
    const formData = new FormData();
    formData.append("data", JSON.stringify(registrationJson));
    
    const fileInput = document.getElementById("pitch_file");
    if (hasPitch && fileInput.files.length) {
        formData.append("pitch_deck", fileInput.files[0]);
    }

    try {
        const response = await fetch(`${getApiBaseUrl()}/api/eureka/register`, {
            method: "POST",
            body: formData
        });

        const resData = await response.json();
        
        if (!response.ok) {
            // Retrieve validation error messages
            let errMsg = resData.detail;
            if (resData.detail && resData.detail.errors) {
                errMsg = resData.detail.errors.join("\n");
            } else if (typeof resData.detail === "object") {
                errMsg = JSON.stringify(resData.detail);
            }
            throw new Error(errMsg || "An error occurred during submission.");
        }

        // 5. Submit success transitions
        loader.style.display = "none";
        document.getElementById("form-header-area").style.display = "none";
        document.getElementById("registration-form").style.display = "none";
        
        document.getElementById("success-reg-id").innerText = resData.registration_id;
        document.getElementById("success-screen").style.display = "block";
        window.scrollTo({ top: 100, behavior: "smooth" });

    } catch (error) {
        loader.style.display = "none";
        alert(`Application Submission Failed:\n\n${error.message}`);
    }
}
