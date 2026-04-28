document.addEventListener("DOMContentLoaded", function() {
    setupSmoothScroll();
    setupIntersectionObserver();
    window.addEventListener('scroll', handleScrollEffects);
});


function setupSmoothScroll() {
    const previewLinks = document.querySelectorAll("aside .preview-link");
    previewLinks.forEach(link => {
        link.addEventListener("click", function(event) {
            event.preventDefault(); 
            const targetId = this.getAttribute("href");
            const targetArticle = document.querySelector(targetId);
            if (targetArticle) {
                targetArticle.scrollIntoView({
                    behavior: "smooth", 
                    block: "start"      
                });
            }
        });
    });
}


function setupIntersectionObserver() {
    const observerCallback = (entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add("is-visible");
                observer.unobserve(entry.target);
            }
        });
    };

    const observerOptions = {
        threshold: 0.1 
    };

    const observer = new IntersectionObserver(observerCallback, observerOptions);

    const articles = document.querySelectorAll("main article");
    articles.forEach(article => {
        observer.observe(article);
    });
}

function handleScrollEffects() {
    const bannerImg = document.querySelector('.header-banner-img');
    let scrollPosition = window.scrollY;
    if (bannerImg) {
        bannerImg.style.transform = `translateY(${scrollPosition * 0.5}px)`; 
    }
}