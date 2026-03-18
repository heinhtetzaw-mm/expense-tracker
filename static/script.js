document.addEventListener("DOMContentLoaded", () => {
    setTodayDate();
    animateTotals();
    setupDeleteConfirm();
    showToast();
});

function setTodayDate() {
    const dateInput = document.querySelector('input[name="date"]');
    if (!dateInput) return;

    if (!dateInput.value) {
        const today = new Date().toISOString().split("T")[0];
        dateInput.value = today;
    }
}

function animateTotals() {
    const totalValues = document.querySelectorAll(".value");

    totalValues.forEach((el) => {
        const finalValue = parseFloat(el.textContent) || 0;
        let current = 0;
        const duration = 600;
        const stepTime = 20;
        const steps = duration / stepTime;
        const increment = finalValue / steps;

        const timer = setInterval(() => {
            current += increment;

            if (current >= finalValue) {
                current = finalValue;
                clearInterval(timer);
            }

            if (Number.isInteger(finalValue)) {
                el.textContent = Math.floor(current);
            } else {
                el.textContent = current.toFixed(2);
            }
        }, stepTime);
    });
}

function setupDeleteConfirm() {
    const deleteForms = document.querySelectorAll('form[action^="/delete/"]');

    deleteForms.forEach((form) => {
        form.addEventListener("submit", (event) => {
            const confirmed = confirm("Are you sure you want to delete this expense?");
            if (!confirmed) {
                event.preventDefault();
            }
        });
    });
}

function showToast() {
    const toast = document.querySelector(".toast");
    if (!toast) return;

    toast.classList.add("show");

    setTimeout(() => {
        toast.classList.remove("show");
    }, 2500);
}