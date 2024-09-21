document.addEventListener("DOMContentLoaded", function () {
    // JavaScript code to enhance interactivity or handle dynamic elements

    // Example: Smooth scrolling to sections
    document.querySelectorAll('nav ul li a').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            targetElement.scrollIntoView({ behavior: 'smooth' });
        });
    });

    console.log("Website is loaded and scripts are active.");
});
