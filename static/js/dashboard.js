




const sidebar = document.getElementById("sidebar");
const menuButton = document.getElementById("menuButton");

if (sidebar && menuButton) {
    menuButton.addEventListener("click", () => {
        sidebar.classList.toggle("open");
    });
}

// Close mobile navigation after selecting a section
document.querySelectorAll(".nav-item[href^='#']").forEach(link => {
    link.addEventListener("click", () => {
        sidebar?.classList.remove("open");
    });
});

// Highlight the current navigation section
const sections = document.querySelectorAll(
    ".main-content section[id]"
);

const navLinks = document.querySelectorAll(
    ".sidebar-nav .nav-item[href^='#']"
);

const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            navLinks.forEach(link => {
                link.classList.toggle(
                    "active",
                    link.getAttribute("href") ===
                    "#" + entry.target.id
                );
            });
        }
    });
}, {
    rootMargin: "-20% 0px -65% 0px"
});

sections.forEach(section => observer.observe(section));