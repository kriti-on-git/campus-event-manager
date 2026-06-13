// EVENT FILTERING
document.addEventListener("DOMContentLoaded", function () {

    const typeFilter = document.getElementById("typeFilter");
    const cards = document.querySelectorAll(".event-card");

    if (typeFilter) {
        typeFilter.addEventListener("change", function () {
            const value = this.value;

            cards.forEach(card => {
                if (value === "all") {
                    card.style.display = "block";
                } else {
                    card.style.display =
                        card.dataset.type === value ? "block" : "none";
                }
            });
        });
    }

});

document.addEventListener("DOMContentLoaded", function () {

    const typeFilter = document.getElementById("typeFilter");
    const cards = document.querySelectorAll(".event-card");

    if (typeFilter) {
        typeFilter.addEventListener("change", function () {

            const value = this.value;

            cards.forEach(card => {
                if (value === "all") {
                    card.style.display = "block";
                } else {
                    card.style.display =
                        card.dataset.type === value ? "block" : "none";
                }
            });
        });
    }

});

    // Initialize icons correctly
    lucide.createIcons();

    // Auto-highlight active navigation link matching current browser path URL
    document.addEventListener("DOMContentLoaded", () => {
        const currentPath = window.location.pathname;
        document.querySelectorAll('.nav-menu .nav-link').forEach(link => {
            if (currentPath === link.getAttribute('href')) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });
    });

