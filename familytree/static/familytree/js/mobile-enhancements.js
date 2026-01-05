/**
 * MALBAT.ORG - Mobile Touch Enhancements
 * Improves touch interactions and mobile UX
 */

(function() {
    'use strict';

    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    function init() {
        // 1. Add haptic-like feedback for buttons (visual only)
        addTouchFeedback();
        
        // 2. Prevent double-tap zoom on buttons
        preventDoubleTapZoom();
        
        // 3. Smooth scroll for anchor links
        enableSmoothScroll();
        
        // 4. Add swipe gestures for cards (optional)
        // addSwipeGestures();
        
        // 5. Improve form input experience
        improveFormInputs();
        
        // 6. Add loading states to buttons
        addLoadingStates();
        
        // 7. Auto-hide navbar on scroll (optional)
        // autoHideNavbar();
        
        // 8. Optimize images for mobile
        optimizeImages();
        
        console.log('✓ Mobile enhancements loaded');
    }

    /**
     * Add visual touch feedback to interactive elements
     */
    function addTouchFeedback() {
        // Add active class on touchstart for instant feedback
        const touchTargets = document.querySelectorAll('.btn, .nav-link, .card a, .list-group-item');
        
        touchTargets.forEach(element => {
            element.addEventListener('touchstart', function() {
                this.classList.add('touch-active');
            }, { passive: true });
            
            element.addEventListener('touchend', function() {
                setTimeout(() => {
                    this.classList.remove('touch-active');
                }, 150);
            }, { passive: true });
            
            element.addEventListener('touchcancel', function() {
                this.classList.remove('touch-active');
            }, { passive: true });
        });
        
        // Add CSS for touch-active state if not already present
        if (!document.getElementById('touch-feedback-styles')) {
            const style = document.createElement('style');
            style.id = 'touch-feedback-styles';
            style.textContent = `
                .touch-active {
                    opacity: 0.7;
                    transition: opacity 0.1s ease;
                }
                .btn.touch-active {
                    transform: scale(0.97);
                }
                .card.touch-active {
                    transform: scale(0.98);
                }
            `;
            document.head.appendChild(style);
        }
    }

    /**
     * Prevent double-tap zoom on buttons and interactive elements
     */
    function preventDoubleTapZoom() {
        const elements = document.querySelectorAll('.btn, .nav-link, button');
        
        elements.forEach(element => {
            element.addEventListener('touchend', function(e) {
                e.preventDefault();
                e.target.click();
            }, { passive: false });
        });
    }

    /**
     * Enable smooth scrolling for anchor links
     */
    function enableSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                const href = this.getAttribute('href');
                if (href !== '#' && href !== '#!') {
                    const target = document.querySelector(href);
                    if (target) {
                        e.preventDefault();
                        target.scrollIntoView({
                            behavior: 'smooth',
                            block: 'start'
                        });
                    }
                }
            });
        });
    }

    /**
     * Improve form input experience on mobile
     */
    function improveFormInputs() {
        const inputs = document.querySelectorAll('input, textarea, select');
        
        inputs.forEach(input => {
            // Auto-scroll to input when focused (prevents keyboard covering input)
            input.addEventListener('focus', function() {
                setTimeout(() => {
                    this.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }, 300);
            });
            
            // Add proper input types for mobile keyboards
            if (input.type === 'text') {
                const name = input.name || input.id || '';
                if (name.includes('email')) {
                    input.type = 'email';
                } else if (name.includes('phone') || name.includes('tel')) {
                    input.type = 'tel';
                } else if (name.includes('url') || name.includes('website')) {
                    input.type = 'url';
                }
            }
        });
        
        // Prevent zoom on input focus for iOS
        const viewport = document.querySelector('meta[name=viewport]');
        if (viewport) {
            const content = viewport.getAttribute('content');
            if (!content.includes('maximum-scale')) {
                viewport.setAttribute('content', content + ', maximum-scale=1.0');
            }
        }
    }

    /**
     * Add loading states to form submit buttons
     */
    function addLoadingStates() {
        const forms = document.querySelectorAll('form');
        
        forms.forEach(form => {
            form.addEventListener('submit', function() {
                const submitBtn = this.querySelector('button[type="submit"], input[type="submit"]');
                if (submitBtn) {
                    const originalText = submitBtn.innerHTML || submitBtn.value;
                    const loadingText = '<i class="bi bi-hourglass-split"></i> ' + 
                                      (submitBtn.getAttribute('data-loading-text') || 'Chargement...');
                    
                    if (submitBtn.tagName === 'BUTTON') {
                        submitBtn.innerHTML = loadingText;
                    } else {
                        submitBtn.value = 'Chargement...';
                    }
                    
                    submitBtn.disabled = true;
                    
                    // Reset after 10 seconds as fallback
                    setTimeout(() => {
                        if (submitBtn.tagName === 'BUTTON') {
                            submitBtn.innerHTML = originalText;
                        } else {
                            submitBtn.value = originalText;
                        }
                        submitBtn.disabled = false;
                    }, 10000);
                }
            });
        });
    }

    /**
     * Auto-hide navbar on scroll down, show on scroll up
     */
    function autoHideNavbar() {
        const navbar = document.querySelector('.navbar');
        if (!navbar) return;
        
        let lastScrollTop = 0;
        const scrollThreshold = 100;
        
        window.addEventListener('scroll', function() {
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            
            if (Math.abs(scrollTop - lastScrollTop) < scrollThreshold) {
                return;
            }
            
            if (scrollTop > lastScrollTop && scrollTop > navbar.offsetHeight) {
                // Scrolling down
                navbar.style.transform = 'translateY(-100%)';
            } else {
                // Scrolling up
                navbar.style.transform = 'translateY(0)';
            }
            
            lastScrollTop = scrollTop;
        }, { passive: true });
        
        // Add transition
        navbar.style.transition = 'transform 0.3s ease';
        navbar.style.position = 'sticky';
        navbar.style.top = '0';
        navbar.style.zIndex = '1030';
    }

    /**
     * Optimize images for mobile viewport
     */
    function optimizeImages() {
        const images = document.querySelectorAll('img[src*="/media/"], img[src*="/static/"]');
        
        images.forEach(img => {
            // Add loading="lazy" for images below the fold
            if (!img.hasAttribute('loading')) {
                const rect = img.getBoundingClientRect();
                if (rect.top > window.innerHeight) {
                    img.setAttribute('loading', 'lazy');
                }
            }
            
            // Add alt text if missing
            if (!img.alt) {
                img.alt = 'Image';
            }
        });
    }

    /**
     * Add swipe gestures for card navigation (optional feature)
     */
    function addSwipeGestures() {
        const cards = document.querySelectorAll('.card a[href*="person_detail"]');
        
        cards.forEach(card => {
            let touchStartX = 0;
            let touchEndX = 0;
            
            card.addEventListener('touchstart', function(e) {
                touchStartX = e.changedTouches[0].screenX;
            }, { passive: true });
            
            card.addEventListener('touchend', function(e) {
                touchEndX = e.changedTouches[0].screenX;
                handleSwipe(this);
            }, { passive: true });
            
            function handleSwipe(element) {
                const swipeThreshold = 50;
                const diff = touchStartX - touchEndX;
                
                if (Math.abs(diff) > swipeThreshold) {
                    if (diff > 0) {
                        // Swiped left - could trigger next person
                        console.log('Swiped left');
                    } else {
                        // Swiped right - could trigger previous person
                        console.log('Swiped right');
                    }
                }
            }
        });
    }

    /**
     * Detect if user is on a touch device
     */
    function isTouchDevice() {
        return (('ontouchstart' in window) ||
                (navigator.maxTouchPoints > 0) ||
                (navigator.msMaxTouchPoints > 0));
    }

    /**
     * Add device class to body for CSS targeting
     */
    (function addDeviceClass() {
        const body = document.body;
        
        if (isTouchDevice()) {
            body.classList.add('touch-device');
        } else {
            body.classList.add('no-touch');
        }
        
        // Detect mobile browser
        if (/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)) {
            body.classList.add('mobile-browser');
        }
        
        // Detect iOS
        if (/iPad|iPhone|iPod/.test(navigator.userAgent)) {
            body.classList.add('ios-device');
        }
        
        // Detect Android
        if (/Android/.test(navigator.userAgent)) {
            body.classList.add('android-device');
        }
    })();

    /**
     * Handle orientation changes
     */
    window.addEventListener('orientationchange', function() {
        // Force reflow after orientation change
        setTimeout(() => {
            document.body.style.display = 'none';
            document.body.offsetHeight; // Force reflow
            document.body.style.display = '';
        }, 100);
    });

    /**
     * Improve Copy ID functionality
     */
    (function improveCopyButton() {
        const copyButtons = document.querySelectorAll('.copy-id-btn');
        
        copyButtons.forEach(btn => {
            // Remove existing event listeners by cloning
            const newBtn = btn.cloneNode(true);
            btn.parentNode.replaceChild(newBtn, btn);
            
            newBtn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                const id = this.dataset.id;
                
                // Modern clipboard API
                if (navigator.clipboard) {
                    navigator.clipboard.writeText(id).then(() => {
                        showCopySuccess(this);
                    }).catch(err => {
                        console.error('Failed to copy:', err);
                        fallbackCopy(id);
                        showCopySuccess(this);
                    });
                } else {
                    fallbackCopy(id);
                    showCopySuccess(this);
                }
            });
        });
        
        function showCopySuccess(button) {
            const originalHtml = button.innerHTML;
            button.innerHTML = '<i class="bi bi-check-lg"></i>';
            button.classList.add('btn-success');
            button.classList.remove('btn-outline-secondary');
            
            setTimeout(() => {
                button.innerHTML = originalHtml;
                button.classList.remove('btn-success');
                button.classList.add('btn-outline-secondary');
            }, 2000);
            
            // Show toast if available
            const toast = document.getElementById('copyToast');
            if (toast && typeof bootstrap !== 'undefined') {
                const bsToast = new bootstrap.Toast(toast);
                bsToast.show();
            }
        }
        
        function fallbackCopy(text) {
            const textArea = document.createElement('textarea');
            textArea.value = text;
            textArea.style.position = 'fixed';
            textArea.style.left = '-9999px';
            document.body.appendChild(textArea);
            textArea.select();
            try {
                document.execCommand('copy');
            } catch (err) {
                console.error('Fallback copy failed:', err);
            }
            document.body.removeChild(textArea);
        }
    })();

})();
