document.addEventListener('scroll', function() {
    const containers = document.querySelectorAll('.image-container');
    const scrollTop = document.documentElement.scrollTop || document.body.scrollTop;
    const viewportHeight = window.innerHeight;

    containers.forEach((container, index) => {
        const containerTop = container.offsetTop;
        const containerBottom = containerTop + container.offsetHeight;

        // Adjust the visibility range to make images stay longer
        if (scrollTop >= containerTop - viewportHeight / 2 && scrollTop < containerBottom - container.offsetHeight / 2) {
            container.style.opacity = 1;
        } else {
            container.style.opacity = 0;
        }
    });
});
