/**
 * Synaptica — Animations Module
 * Hero particles, scroll observers, counter animations, and utilities.
 */
const Animations = {
    heroCanvas: null,
    heroCtx: null,
    particles: [],
    animationId: null,

    init() {
        this.initScrollReveal();
        this.initHeroCanvas();
    },

    // ── Scroll Reveal ───────────────────────────────────────
    initScrollReveal() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                }
            });
        }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

        document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
    },

    observeNewElements() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                }
            });
        }, { threshold: 0.1 });
        document.querySelectorAll('.reveal:not(.visible)').forEach(el => observer.observe(el));
    },

    // ── Staggered Card Entry ────────────────────────────────
    staggerCards(container, delay = 60) {
        const cards = container.querySelectorAll('[data-stagger]');
        cards.forEach((card, i) => {
            setTimeout(() => card.classList.add('entered'), i * delay);
        });
    },

    // ── Counter Animation ───────────────────────────────────
    animateCounters() {
        const counters = document.querySelectorAll('.counter');
        counters.forEach(counter => {
            const target = parseInt(counter.getAttribute('data-target')) || 0;
            if (target === 0) return;
            const duration = 1500;
            const start = performance.now();
            const startVal = 0;

            const step = (timestamp) => {
                const progress = Math.min((timestamp - start) / duration, 1);
                const eased = 1 - Math.pow(1 - progress, 3); // easeOutCubic
                const current = Math.round(startVal + (target - startVal) * eased);
                counter.textContent = current.toLocaleString();
                if (progress < 1) requestAnimationFrame(step);
            };
            requestAnimationFrame(step);
        });
    },

    // ── Hero GSAP Animation ────────────────────────────────
    initHeroCanvas() {
        if (typeof gsap === 'undefined' || typeof CustomEase === 'undefined') return;
        
        gsap.registerPlugin(CustomEase);

        const customEaseIn = CustomEase.create('custom-ease-in', '0.52, 0.00, 0.48, 1.00');
        const fourtyFrames = 1.3333333;
        const fiftyFrames = 1.66666;
        const twoFrames = 0.666666;
        const fourFrames = 0.133333;
        const sixFrames = 0.2;

        const header = document.querySelector('.navbar'); // Or header if present
        const book = document.querySelector('.first-desc span');
        const open = document.querySelector('.second-desc span');
        const copy = document.querySelector('.copyright span');
        const scrollToRows = document.querySelectorAll('.scroll-to .scroll-to__row span');
        const btnCircle = document.querySelector('.book-btn__circle');
        const btnText = document.querySelector('.btn-text span');
        const eve = document.querySelector('#eve span');
        const ry = document.querySelector('#ry span');
        const fo = document.querySelector('#fo span');
        const ssil = document.querySelector('#ssil span');
        const tells = document.querySelector('#tells span');
        const a = document.querySelector('#a span');
        const st = document.querySelector('#st span');
        const ory = document.querySelector('#ory span');

        // Check if elements exist before animating
        if (!eve) return;

        const showElements = () => {
            const timeline = gsap.timeline();
            timeline
                  .fromTo(btnCircle, { autoAlpha: 0 }, { autoAlpha: 1, duration: fourtyFrames, ease: customEaseIn}, 0)
                  .fromTo(btnCircle, { scale: 0.417 }, { scale: 1, duration: fourtyFrames, ease: customEaseIn}, 0)
                  // .fromTo(header, {y: '-3.47vw'}, {y: '0vw', duration: fourtyFrames, ease: customEaseIn}, 0)
                  .fromTo(eve, {x: '18.75vw'}, { x: '0vw', duration: fiftyFrames, ease: customEaseIn}, 0)
                  .fromTo(book, {y: '3.47vw'}, {y: '0vw', duration: fourtyFrames, ease: customEaseIn}, twoFrames)
                  .fromTo(fo, {x: '14.58vw'}, { x: '0vw', duration: fiftyFrames, ease: customEaseIn}, twoFrames)
                  .fromTo(a, {x: '-8.33vw'}, { x: '0vw', duration: fiftyFrames, ease: customEaseIn}, twoFrames)
                  .fromTo(ory, {x: '-22.22vw'}, { x: '0vw', duration: fiftyFrames, ease: customEaseIn}, twoFrames)
                  .fromTo(open, {y: '2.08vw'}, {y: '0vw', duration: fourtyFrames, ease: customEaseIn}, fourFrames)
                  .fromTo(btnText, {y: '2.77vw'}, {y: '0vw', duration: fourtyFrames, ease: customEaseIn}, fourFrames)
                  .fromTo(ry, {x: '-13.88vw'}, { x: '0vw', duration: fiftyFrames, ease: customEaseIn}, fourFrames)
                  .fromTo(ssil, {x: '-21.52vw'}, { x: '0vw', duration: fiftyFrames, ease: customEaseIn}, fourFrames)
                  .fromTo(tells, {x: '29.86vw'}, { x: '0vw', duration: fiftyFrames, ease: customEaseIn}, fourFrames)
                  .fromTo(st, {x: '13.19vw'}, { x: '0vw', duration: fiftyFrames, ease: customEaseIn}, fourFrames)
                  .fromTo(copy, {y: '2.77vw'}, {y: '0vw', duration: fourtyFrames, ease: customEaseIn}, sixFrames)
                  .fromTo(scrollToRows, {y: '3.47vw'}, {y: '0vw', duration: fourtyFrames, ease: customEaseIn}, sixFrames);
            return timeline;
        };
        
        showElements();
    },

    stopHeroAnimation() {
        // Not strictly needed for GSAP timelines as they end, but can kill tweens if navigating away fast
        if (typeof gsap !== 'undefined') gsap.killTweensOf('.hero *');
    },

    // ── Toast Notifications ─────────────────────────────────
    showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        if (!container) return;
        const toast = document.createElement('div');
        toast.className = 'toast';
        const icons = { info: 'ℹ️', success: '✅', error: '❌', warning: '⚠️' };
        toast.innerHTML = `${icons[type] || ''} ${message}`;
        container.appendChild(toast);
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(20px)';
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    }
};
