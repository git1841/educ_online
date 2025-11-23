// Attendre que le DOM soit chargé
document.addEventListener('DOMContentLoaded', function () {

    // Navigation scroll effect
    const navbar = document.querySelector('.custom-navbar');
    window.addEventListener('scroll', function () {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    // Smooth scrolling pour les liens de navigation
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href.startsWith('#')) {
                e.preventDefault();
                const targetId = href;
                const targetSection = document.querySelector(targetId);
                if (targetSection) {
                    const offsetTop = targetSection.offsetTop - 80;
                    window.scrollTo({
                        top: offsetTop,
                        behavior: 'smooth'
                    });
                }
            }
        });
    });

    // Carrousel automatique
    let currentSlide = 0;
    const slides = document.querySelectorAll('.carousel-slide');
    const indicators = document.querySelectorAll('.indicator');
    const totalSlides = slides.length;
    let autoSlideInterval;

    function showSlide(index) {
        // Masquer tous les slides
        slides.forEach(slide => slide.classList.remove('active'));
        indicators.forEach(indicator => indicator.classList.remove('active'));

        // Afficher le slide actuel
        slides[index].classList.add('active');
        indicators[index].classList.add('active');
    }

    function nextSlide() {
        currentSlide = (currentSlide + 1) % totalSlides;
        showSlide(currentSlide);
    }

    function prevSlide() {
        currentSlide = (currentSlide - 1 + totalSlides) % totalSlides;
        showSlide(currentSlide);
    }

    function startAutoSlide() {
        autoSlideInterval = setInterval(nextSlide, 4000); // Change toutes les 4 secondes
    }

    function stopAutoSlide() {
        clearInterval(autoSlideInterval);
    }

    // Gestion des indicateurs
    indicators.forEach((indicator, index) => {
        indicator.addEventListener('click', () => {
            currentSlide = index;
            showSlide(currentSlide);
            stopAutoSlide();
            startAutoSlide(); // Redémarrer le carrousel après interaction
        });
    });

    // Démarrer le carrousel automatique
    startAutoSlide();

    // Pause au survol du carrousel
    const carouselContainer = document.querySelector('.hero-carousel-container');
    carouselContainer.addEventListener('mouseenter', stopAutoSlide);
    carouselContainer.addEventListener('mouseleave', startAutoSlide);

    // Animation au scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function (entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                n
            }
        });
    }, observerOptions);

    // Observer les éléments pour l'animation
    const animateElements = document.querySelectorAll('.feature-card, .cours-card, .exercise-category, .ressource-card, .stat-card');
    animateElements.forEach(el => {
        observer.observe(el);
    });

    // Animation des statistiques
    const stats = document.querySelectorAll('.stat-number');
    const statsObserver = new IntersectionObserver(function (entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const target = entry.target;
                const finalValue = parseInt(target.getAttribute('data-count'));
                animateCounter(target, finalValue);
                statsObserver.unobserve(target);
            }
        });
    }, { threshold: 0.5 });

    stats.forEach(stat => {
        statsObserver.observe(stat);
    });

    function animateCounter(element, target) {
        let current = 0;
        const increment = target / 100;
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            element.textContent = Math.floor(current);
        }, 20);
    }

    // Particules animées pour la section hero
    createParticles();

    function createParticles() {
        const container = document.getElementById('particles-container');
        if (!container) return;

        const particleCount = 50;

        for (let i = 0; i < particleCount; i++) {
            const particle = document.createElement('div');
            particle.style.cssText = `
                position: absolute;
                width: ${Math.random() * 4 + 1}px;
                height: ${Math.random() * 4 + 1}px;
                background: rgba(99, 102, 241, ${Math.random() * 0.5 + 0.1});
                border-radius: 50%;
                left: ${Math.random() * 100}%;
                top: ${Math.random() * 100}%;
                animation: floatParticle ${Math.random() * 20 + 10}s linear infinite;
            `;
            container.appendChild(particle);
        }
    }

    // Ajouter CSS pour les particules
    const style = document.createElement('style');
    style.textContent = `
        @keyframes floatParticle {
            0% { transform: translateY(0px) translateX(0px) rotate(0deg); opacity: 0; }
            10% { opacity: 1; }
            90% { opacity: 1; }
            100% { transform: translateY(-100vh) translateX(50px) rotate(360deg); opacity: 0; }
        }
    `;
    document.head.appendChild(style);

    // Animation d'écriture pour le titre hero
    function typeWriter() {
        const title = document.querySelector('.hero-title');
        if (!title) return;

        const text = title.innerHTML;
        title.innerHTML = '';
        title.style.opacity = '1';

        let i = 0;
        const typeInterval = setInterval(() => {
            title.innerHTML = text.substring(0, i) + '<span class="cursor">|</span>';
            i++;

            if (i > text.length) {
                clearInterval(typeInterval);
                title.innerHTML = text;
            }
        }, 50);
    }

    // Lancer l'animation d'écriture après un délai
    setTimeout(typeWriter, 1000);

    // Effet de survol pour les cartes de cours
    const coursCards = document.querySelectorAll('.cours-card');
    coursCards.forEach(card => {
        card.addEventListener('mouseenter', function () {
            this.style.transform = 'translateY(-10px) scale(1.02)';
        });

        card.addEventListener('mouseleave', function () {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });

    // Gestion du menu mobile
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');

    if (navbarToggler && navbarCollapse) {
        navbarToggler.addEventListener('click', function () {
            navbarCollapse.classList.toggle('show');
        });
    }

    // Fermer le menu mobile après avoir cliqué sur un lien
    const mobileNavLinks = document.querySelectorAll('.navbar-nav .nav-link');
    mobileNavLinks.forEach(link => {
        link.addEventListener('click', function () {
            if (window.innerWidth < 992) {
                navbarCollapse.classList.remove('show');
            }
        });
    });

    // Effet de parallax pour la section hero
    window.addEventListener('scroll', function () {
        const scrolled = window.pageYOffset;
        const heroSection = document.querySelector('.hero-section');
        const heroParticles = document.querySelector('.hero-particles');

        if (heroSection && scrolled < heroSection.offsetHeight) {
            const rate = scrolled * -0.5;
            if (heroParticles) {
                heroParticles.style.transform = `translateY(${rate}px)`;
            }
        }
    });

    // Animation de scroll progressif
    let ticking = false;
    function updateScrollProgress() {
        const scrollTop = window.pageYOffset;
        const docHeight = document.body.scrollHeight - window.innerHeight;
        const scrollPercent = (scrollTop / docHeight) * 100;

        document.documentElement.style.setProperty('--scroll-progress', scrollPercent + '%');
        ticking = false;
    }

    function requestTick() {
        if (!ticking) {
            requestAnimationFrame(updateScrollProgress);
            ticking = true;
        }
    }

    window.addEventListener('scroll', requestTick);

    // Initialisation des animations
    setTimeout(() => {
        document.body.classList.add('loaded');
    }, 500);

    // Console log pour le débogage
    console.log("EduMath-Info - Site d'apprentissage chargé avec succès!");
    console.log("Carrousel automatique activé avec", totalSlides, "images");
    console.log("Fonctionnalités activées:");
    console.log("- Navigation avec effet de scroll");
    console.log("- Animations au défilement");
    console.log("- Particules animées");
    console.log("- Compteurs de statistiques");
    console.log("- Carrousel automatique d'images");
    console.log("- Design responsive");
    console.log("- Animation d'écriture du titre");
});


// Fonction utilitaire pour les délais d'animation
function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Fonction pour animer les éléments avec différents délais
async function staggerAnimation(elements, animationClass, delayMs = 100) {
    for (let i = 0; i < elements.length; i++) {
        setTimeout(() => {
            elements[i].classList.add(animationClass);
        }, i * delayMs);
    }
}

// Export des fonctions pour une utilisation externe
window.EduMathInfo = {
    delay,
    staggerAnimation
};