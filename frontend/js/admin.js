const LIMIT = 10;
let currentPage = 1;
let loadedRegistrations = [];
let searchTimeout = null;

function getApiBaseUrl() {
    if (window.location.port === "8000" || window.location.port === "8080") {
        return "";
    }

    return "http://127.0.0.1:8000";
}

document.addEventListener("DOMContentLoaded", () => {
    checkAuth();
});

// Check if admin is logged in
function checkAuth() {
    const token = localStorage.getItem("eureka_admin_token");
    const loginBox = document.getElementById("login-container");
    const dashBox = document.getElementById("dashboard-container");

    if (token) {
        loginBox.style.display = "none";
        dashBox.style.display = "block";
        fetchRegistrations();
    } else {
        loginBox.style.display = "block";
        dashBox.style.display = "none";
    }
}

// Admin login submission
async function adminLogin(event) {
    event.preventDefault();
    const username = document.getElementById("admin_user").value;
    const password = document.getElementById("admin_pass").value;
    const errDiv = document.getElementById("login-error");

    errDiv.style.display = "none";

    try {
        const response = await fetch(`${getApiBaseUrl()}/api/eureka/admin/login`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ username, password })
        });

        if (!response.ok) {
            throw new Error("Invalid credentials");
        }

        const data = await response.json();
        localStorage.setItem("eureka_admin_token", data.access_token);
        checkAuth();
    } catch (err) {
        errDiv.style.display = "flex";
    }
}

// Admin logout
function adminLogout() {
    localStorage.removeItem("eureka_admin_token");
    window.location.reload();
}

// Fetch registrations with parameters
async function fetchRegistrations() {
    const token = localStorage.getItem("eureka_admin_token");
    if (!token) return;

    const tbody = document.getElementById("registrations-tbody");
    tbody.innerHTML = `
        <tr>
            <td colspan="8" style="text-align: center; color: var(--text-secondary); padding: 3rem;">
                <i class="fa-solid fa-circle-notch fa-spin" style="font-size: 2rem; margin-bottom: 0.5rem; display: block; color: var(--primary);"></i>
                Refreshing list...
            </td>
        </tr>
    `;

    // Gather filter parameters
    const searchVal = document.getElementById("search-input").value;
    const categoryVal = document.getElementById("filter-category").value;
    const statusVal = document.getElementById("filter-status").value;

    const skip = (currentPage - 1) * LIMIT;
    
    let url = `${getApiBaseUrl()}/api/eureka/admin/registrations?skip=${skip}&limit=${LIMIT}`;
    if (searchVal) url += `&search=${encodeURIComponent(searchVal)}`;
    if (categoryVal) url += `&category=${encodeURIComponent(categoryVal)}`;
    if (statusVal) url += `&status=${encodeURIComponent(statusVal)}`;

    try {
        const response = await fetch(url, {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (response.status === 401) {
            // Token expired or invalid
            adminLogout();
            return;
        }

        if (!response.ok) {
            throw new Error("Failed to fetch registrations");
        }

        const data = await response.json();
        loadedRegistrations = data.registrations;
        
        // 1. Update stats cards
        document.getElementById("stat-total").innerText = data.counts.total;
        document.getElementById("stat-pending").innerText = data.counts.pending;
        document.getElementById("stat-approved").innerText = data.counts.approved;
        document.getElementById("stat-rejected").innerText = data.counts.rejected;

        // 2. Render table
        renderTableRows(data.registrations);

        // 3. Update pagination
        updatePaginationUI(data.total, skip);

    } catch (error) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" style="text-align: center; color: var(--error); padding: 3rem;">
                    <i class="fa-solid fa-triangle-exclamation" style="font-size: 2rem; margin-bottom: 0.5rem; display: block;"></i>
                    Failed to load applications. ${error.message}
                </td>
            </tr>
        `;
    }
}

// Render dynamic rows
function renderTableRows(registrations) {
    const tbody = document.getElementById("registrations-tbody");
    tbody.innerHTML = "";

    if (!registrations || registrations.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" style="text-align: center; color: var(--text-secondary); padding: 3rem;">
                    No registration records match your filters.
                </td>
            </tr>
        `;
        return;
    }

    registrations.forEach(reg => {
        // Find lead name
        const lead = reg.team_members.find(m => m.is_lead) || reg.team_members[0];
        const leadName = lead ? lead.name : "N/A";
        
        // Format creation date
        const dateStr = new Date(reg.created_at).toLocaleDateString("en-US", {
            month: "short",
            day: "numeric",
            hour: "2-digit",
            minute: "2-digit"
        });

        // Status Badge Style
        let badgeClass = "badge-pending";
        if (reg.status === "Approved") badgeClass = "badge-approved";
        if (reg.status === "Rejected") badgeClass = "badge-rejected";

        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td><strong style="color: var(--cyan);">${reg.registration_id}</strong></td>
            <td><strong>${escapeHtml(reg.startup_name)}</strong></td>
            <td>${reg.category}</td>
            <td>${escapeHtml(leadName)}</td>
            <td style="text-align: center;">${reg.team_size}</td>
            <td>${dateStr}</td>
            <td><span class="badge ${badgeClass}">${reg.status}</span></td>
            <td style="text-align: center;">
                <button class="btn btn-secondary" onclick="openDetails(${reg.id})" style="padding: 0.4rem 0.85rem; font-size: 0.8rem; border-radius: 0.4rem;">
                    <i class="fa-solid fa-eye"></i> View details
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

// HTML Escaper for security
function escapeHtml(str) {
    if (!str) return "";
    return str
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Pagination handler
function updatePaginationUI(total, skip) {
    const start = total === 0 ? 0 : skip + 1;
    const end = Math.min(skip + LIMIT, total);
    
    document.getElementById("pagination-info").innerText = `Showing ${start}-${end} of ${total} applications`;

    const btnPrev = document.getElementById("btn-prev");
    const btnNext = document.getElementById("btn-next");

    btnPrev.disabled = currentPage === 1;
    btnPrev.style.opacity = currentPage === 1 ? "0.5" : "1";
    btnPrev.style.cursor = currentPage === 1 ? "not-allowed" : "pointer";

    const hasNext = (skip + LIMIT) < total;
    btnNext.disabled = !hasNext;
    btnNext.style.opacity = hasNext ? "1" : "0.5";
    btnNext.style.cursor = hasNext ? "pointer" : "not-allowed";
}

function changePage(direction) {
    currentPage += direction;
    fetchRegistrations();
}

// Search and Filter updates with a small typing delay (debounce)
function handleSearchFilterChange() {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        currentPage = 1;
        fetchRegistrations();
    }, 300);
}

// View Application Detail Modal functions
function openDetails(dbId) {
    const reg = loadedRegistrations.find(r => r.id === dbId);
    if (!reg) return;

    // Fill Startup Details
    document.getElementById("det-db-id").value = reg.id;
    document.getElementById("det-startup-name").innerText = reg.startup_name;
    document.getElementById("det-category").innerText = reg.category;
    document.getElementById("det-stage").innerText = reg.stage;
    document.getElementById("det-reg-id").innerText = reg.registration_id;
    
    document.getElementById("det-desc").innerText = reg.description;
    document.getElementById("det-problem").innerText = reg.problem_statement;
    document.getElementById("det-solution").innerText = reg.solution;

    // Conditional Area
    const conditionalSec = document.getElementById("det-conditional-section");
    if (reg.is_existing) {
        conditionalSec.style.display = "block";
        document.getElementById("det-website").innerText = reg.website || "N/A";
        if (reg.website && reg.website.startsWith("http")) {
            document.getElementById("det-website").innerHTML = `<a href="${reg.website}" target="_blank" style="color: var(--cyan);">${reg.website}</a>`;
        }
        document.getElementById("det-revenue").innerText = reg.revenue || "No Revenue";
        document.getElementById("det-reg-details").innerText = reg.registration_details || "N/A";
    } else {
        conditionalSec.style.display = "none";
    }

    // Dynamic Team Lists
    document.getElementById("det-team-size").innerText = reg.team_size;
    const teamList = document.getElementById("det-members-list");
    teamList.innerHTML = "";
    
    // Sort so Lead is first
    const sortedMembers = [...reg.team_members].sort((a, b) => b.is_lead - a.is_lead);

    sortedMembers.forEach((member, i) => {
        const item = document.createElement("div");
        item.style.padding = "1rem";
        item.style.background = member.is_lead ? "rgba(99, 102, 241, 0.04)" : "rgba(255, 255, 255, 0.01)";
        item.style.border = `1px solid ${member.is_lead ? "var(--border-color-glow)" : "var(--border-color)"}`;
        item.style.borderRadius = "0.5rem";
        
        item.innerHTML = `
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                <strong style="color: #fff; font-size: 0.95rem;">${escapeHtml(member.name)}</strong>
                <span class="badge" style="background: ${member.is_lead ? "var(--primary-glow)" : "rgba(255,255,255,0.05)"}; color: #fff; font-size: 0.65rem;">
                    ${member.is_lead ? "Team Lead" : `Member ${i+1}`}
                </span>
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 0.5rem; font-size: 0.85rem; color: var(--text-secondary);">
                <div><i class="fa-solid fa-envelope"></i> ${escapeHtml(member.email)}</div>
                <div><i class="fa-solid fa-phone"></i> ${escapeHtml(member.phone)}</div>
                <div><i class="fa-solid fa-graduation-cap"></i> ${escapeHtml(member.college)}</div>
                <div><i class="fa-solid fa-building-columns"></i> Bank A/C: ${escapeHtml(member.bank_account) || "N/A"}</div>
            </div>
        `;
        teamList.appendChild(item);
    });

    // File Pitch Deck pdf section
    const pdfSec = document.getElementById("det-pdf-section");
    if (reg.has_pitch_deck && reg.pitch_deck_path) {
        pdfSec.style.display = "block";
        document.getElementById("det-pdf-download").href = reg.pitch_deck_path;
    } else {
        pdfSec.style.display = "none";
    }

    // Modal Status display
    const statusBadge = document.getElementById("det-status-badge");
    statusBadge.innerText = reg.status;
    statusBadge.className = "badge";
    if (reg.status === "Approved") statusBadge.classList.add("badge-approved");
    else if (reg.status === "Rejected") statusBadge.classList.add("badge-rejected");
    else statusBadge.classList.add("badge-pending");

    toggleModal("details-modal", true);
}

function toggleModal(id, show) {
    const modal = document.getElementById(id);
    if (show) {
        modal.classList.add("active");
        document.body.style.overflow = "hidden";
    } else {
        modal.classList.remove("active");
        document.body.style.overflow = "";
    }
}

// Update status (Approve / Reject)
async function updateStatusFromModal(newStatus) {
    const token = localStorage.getItem("eureka_admin_token");
    const dbId = document.getElementById("det-db-id").value;
    
    if (!token || !dbId) return;

    try {
        const response = await fetch(`${getApiBaseUrl()}/api/eureka/admin/registrations/${dbId}/status`, {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({ status: newStatus })
        });

        if (!response.ok) {
            throw new Error("Failed to update status");
        }

        toggleModal("details-modal", false);
        fetchRegistrations(); // refresh
    } catch (err) {
        alert(`Failed to update application status:\n${err.message}`);
    }
}

// Export excel with bearer credentials
async function exportExcel() {
    const token = localStorage.getItem("eureka_admin_token");
    if (!token) return;

    // Build URL with exact filters
    const searchVal = document.getElementById("search-input").value;
    const categoryVal = document.getElementById("filter-category").value;
    const statusVal = document.getElementById("filter-status").value;

    let url = `${getApiBaseUrl()}/api/eureka/admin/export?`;
    if (searchVal) url += `&search=${encodeURIComponent(searchVal)}`;
    if (categoryVal) url += `&category=${encodeURIComponent(categoryVal)}`;
    if (statusVal) url += `&status=${encodeURIComponent(statusVal)}`;

    try {
        const response = await fetch(url, {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error("Failed to export database spreadsheet");
        }

        const blob = await response.blob();
        
        // Trigger browser file download
        const downloadUrl = window.URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = downloadUrl;
        link.download = `Eureka_Registrations_${new Date().toISOString().slice(0,10)}.xlsx`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(downloadUrl);

    } catch (error) {
        alert(`spreadsheet download failed: ${error.message}`);
    }
}
