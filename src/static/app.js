document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");
  let activitiesData = {};

  function showMessage(text, type) {
    messageDiv.textContent = text;
    messageDiv.className = type;
    messageDiv.classList.remove("hidden");

    setTimeout(() => {
      messageDiv.classList.add("hidden");
    }, 5000);
  }

  function renderActivities(activities) {
    activitiesList.innerHTML = "";
    activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

    Object.entries(activities).forEach(([name, details]) => {
      const activityCard = document.createElement("div");
      activityCard.className = "activity-card";

      const spotsLeft = details.max_participants - details.participants.length;
      const participantsMarkup = (details.participants || []).length > 0
        ? (details.participants || [])
            .map(
              (email) => `
                <li class="participant-item">
                  <span class="participant-email">${email}</span>
                  <button
                    class="participant-remove-btn"
                    data-activity="${name}"
                    data-email="${email}"
                    aria-label="Remove ${email}"
                    title="Unregister ${email}"
                  >
                    <span aria-hidden="true">✕</span>
                  </button>
                </li>
              `
            )
            .join("")
        : '<li class="participant-item participant-item-empty">No participants yet.</li>';

      activityCard.innerHTML = `
        <h4>${name}</h4>
        <p>${details.description}</p>
        <p><strong>Schedule:</strong> ${details.schedule}</p>
        <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
        <div class="participants-section">
          <strong>Participants</strong>
          <ul class="participants-list">${participantsMarkup}</ul>
        </div>
      `;

      activitiesList.appendChild(activityCard);

      const option = document.createElement("option");
      option.value = name;
      option.textContent = name;
      activitySelect.appendChild(option);
    });
  }

  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();
      activitiesData = activities;
      renderActivities(activitiesData);
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  activitiesList.addEventListener("click", async (event) => {
    const button = event.target.closest(".participant-remove-btn");

    if (!button) {
      return;
    }

    const activity = button.dataset.activity;
    const email = button.dataset.email;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        { method: "DELETE" }
      );
      const result = await response.json();

      if (response.ok) {
        showMessage(result.message, "success");
        if (activitiesData[activity] && Array.isArray(activitiesData[activity].participants)) {
          activitiesData[activity].participants = activitiesData[activity].participants.filter((participant) => participant !== email);
          renderActivities(activitiesData);
        }
        await fetchActivities();
      } else {
        showMessage(result.detail || "Unable to unregister participant.", "error");
      }
    } catch (error) {
      showMessage("Failed to unregister. Please try again.", "error");
      console.error("Error unregistering participant:", error);
    }
  });

  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        { method: "POST" }
      );

      const result = await response.json();

      if (response.ok) {
        showMessage(result.message, "success");
        signupForm.reset();
        if (activitiesData[activity] && Array.isArray(activitiesData[activity].participants)) {
          activitiesData[activity].participants.push(email);
          renderActivities(activitiesData);
        }
        await fetchActivities();
      } else {
        showMessage(result.detail || "An error occurred", "error");
      }
    } catch (error) {
      showMessage("Failed to sign up. Please try again.", "error");
      console.error("Error signing up:", error);
    }
  });

  fetchActivities();
});
