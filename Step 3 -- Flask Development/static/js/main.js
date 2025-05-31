/**
* Template Name: iLanding - Redone from Scratch by Pablo Vilar Bustillo
* Template URL: https://bootstrapmade.com/ilanding-bootstrap-landing-page-template/
* Updated: Nov 12 2024 with Bootstrap v5.3.3
* Author: BootstrapMade.com - Pablo Vilar Bustillo
* License: https://bootstrapmade.com/license/
*/

let TranslationSystem;

/* ======== CORE MODULES ======== */
const App = (() => {
    "use strict";

    /* ======= CONFIGURATION ======== */
    const config = {
        selectors: {
            body: 'body',
            header: '#header',
            mobileNavToggle: '.mobile-nav-toggle',
            themeButton: '.btn-changeTheme',
            scrollTop: '.scroll-top',
            navmenu: '#navmenu a',
            faqItems: '.faq-item h3, .faq-item .faq-toggle'
        },
        classes: {
            scrolled: 'scrolled',
            mobileNavActive: 'mobile-nav-active',
            darkTheme: 'dark-theme'
        }
    };

    /* ======== SCROLL HANDLING ======== */
    const ScrollManager = {
        init() {
            this.handleScrollClasses();
            this.initScrollTop();
            window.addEventListener('load', () => this.handleScrollClasses());
            document.addEventListener('scroll', () => this.handleScrollClasses());
        },

        handleScrollClasses() {
            const body = document.querySelector(config.selectors.body);
            const header = document.querySelector(config.selectors.header);

            if (!header || !body) return;
            const hasStickyClass = ['scroll-up-sticky', 'sticky-top', 'fixed-top'].some(c => header.classList.contains(c));

            if (hasStickyClass) {
                body.classList.toggle(config.classes.scrolled, window.scrollY > 100);
            }
        },

        initScrollTop() {
            const scrollTop = document.querySelector(config.selectors.scrollTop);
            if (!scrollTop) return;

            scrollTop.addEventListener('click', (e) => {
                e.preventDefault();
                window.scrollTo({ top: 0, behavior: 'smooth' });
            });

            const toggleVisibility = () => {
                scrollTop.classList.toggle('active', window.scrollY > 100);
            };

            window.addEventListener('load', toggleVisibility);
            document.addEventListener('scroll', toggleVisibility);
        }
    };

    /* ======== MOBILE NAVIGATION ======== */
    const MobileNav = {
      init() {
          this.toggleBtn = document.querySelector(config.selectors.mobileNavToggle);
          if (!this.toggleBtn) return;

          this.toggleBtn.addEventListener('click', () => this.toggle());
          this.initDropdowns();
      },

      toggle() {
          document.body.classList.toggle(config.classes.mobileNavActive);
          this.toggleBtn.classList.toggle('bi-list');
          this.toggleBtn.classList.toggle('bi-x');
      },

      initDropdowns() {
          document.querySelectorAll('.navmenu .toggle-dropdown').forEach(item => {
              item.addEventListener('click', (e) => {
                  e.preventDefault();
                  item.parentNode.classList.toggle('active');
                  item.parentNode.nextElementSibling.classList.toggle('dropdown-active');
              });
          });
      }
    };

    /* ======== THEME MANAGER ======== */
    const ThemeManager = {
        init() {
            this.themeButton = document.querySelector(config.selectors.themeButton);
            if (!this.themeButton) return;

            this.icon = this.themeButton.querySelector('i');
            this.loadTheme();
            this.setupEventListeners();
        },

        loadTheme() {
            const savedTheme = localStorage.getItem('theme');
            const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            const initialTheme = savedTheme || (systemDark ? 'dark' : 'light');

            document.body.classList.toggle(config.classes.darkTheme, initialTheme === 'dark');
            this.icon.className = initialTheme === 'dark' ? 'bi bi-moon-stars' : 'bi bi-sun';

            this.updateThemeElements();
        },

        setupEventListeners() {
            this.themeButton.addEventListener('click', () => {
                const isDark = document.body.classList.toggle(config.classes.darkTheme);
                localStorage.setItem('theme', isDark ? 'dark' : 'light');
                this.icon.className = isDark ? 'bi bi-moon-stars' : 'bi bi-sun';
                this.updateThemeElements();
                this.animateIcon();
            });
        },

        updateThemeElements() {
            const themeSections = ['#faq', '#section2', '#analysisModal', '#productInfo', '#analysisResults', '#allReviewsModal'];

            themeSections.forEach(selector => {
                const element = document.querySelector(selector);
                if (!element) return;

                const isDark = document.body.classList.contains(config.classes.darkTheme);
                element.classList.toggle('dark-background', isDark);
                element.classList.toggle('light-background', !isDark);
            });

            if (window.location.pathname.startsWith('/result/') || window.location.pathname === '/stats') {
                import('/static/js/stats.js')
                    .then(module => {
                        module.ChartSystem.refreshCharts();
                    })
                    .catch(error => {
                        console.error('Error cargando módulo:', error);
                    });
            }

        },

        animateIcon() {
            this.icon.style.animation = 'iconSpin 0.5s ease';
            setTimeout(() => (this.icon.style.animation = ''), 500);
        }
    };

    /* ======== TRANSLATION SYSTEM ======== */
    TranslationSystem = {
        translations: {},

        async init() {
            try {
                const response = await fetch('/static/json/language.json');
                this.translations = await response.json();
                this.setupLanguage();
                return true;
            } catch (error) {
                console.error('Error loading translations:', error);
                return false;
            }
        },

        setupLanguage() {
            const browserLang = navigator.language.slice(0,2).toLowerCase();
            const savedLang = localStorage.getItem('language');
            const defaultLang = this.translations[savedLang] ? savedLang : this.translations[browserLang] ? browserLang : 'es';

            this.updatePageLanguage(defaultLang);
            this.setupLanguageSwitcher();
        },

        updatePageLanguage(lang) {
            if (!this.translations[lang]) return;

            // Update regular elements
            document.querySelectorAll('[data-translate]').forEach(el => {
                if (el.tagName.toLowerCase() !== 'title') {
                    el.innerHTML = DOMPurify.sanitize(this.translations[lang][el.dataset.translate]);
                }
            });

            // Special elements
            document.title = DOMPurify.sanitize(this.translations[lang].mainTitle);
            this.updateFormElements(lang);
            this.updateLanguageIndicator(lang);
            this.updateToggleTexts(lang);

            // Update charts
            if (window.location.pathname.startsWith('/result/') || window.location.pathname === '/stats') {
                import('/static/js/stats.js')
                    .then(module => {
                        module.ChartSystem.refreshCharts();
                    })
                    .catch(error => {
                        console.error('Error cargando módulo:', error);
                    });
            }
        },

        updateFormElements(lang) {
            const urlInput = document.querySelector('#urlValidator');
            if (urlInput) urlInput.placeholder = this.translations[lang].urlPlaceholder;

            const analyzeBtn = document.querySelector('button[type="submit"]');
            if (analyzeBtn) analyzeBtn.textContent = this.translations[lang].analyzeButton;
        },

        updateLanguageIndicator(lang) {
            const flagElement = document.getElementById('currentFlag');
            const codeElement = document.getElementById('currentLang');
            if (!flagElement || !codeElement) return;

            flagElement.className = `fi fi-${this.translations[lang].flag}`;
            codeElement.textContent = this.translations[lang].code.toUpperCase();
        },

        updateToggleTexts(lang) {
            document.querySelectorAll('.expand-toggle').forEach(toggle => {
                const container = toggle.closest('.review-text-container');
                if (!container) return;

                const isTruncated = container.classList.contains('truncated');
                toggle.textContent = isTruncated ? this.translations[lang]?.showMoreText : this.translations[lang]?.showLessText;
            });
        },

        setupLanguageSwitcher() {
            document.querySelectorAll('.language-option').forEach(option => {
                option.addEventListener('click', async (e) => {
                    e.preventDefault();
                    const lang = e.currentTarget.dataset.lang;
                    if (!this.translations[lang]) return;

                    localStorage.setItem('language', lang);
                    this.updatePageLanguage(lang);
                    FormValidator.validateOnLanguageChange();
                });
            });
        }
    };

    /* ======== HEADER ACTIVE CLASS ======== */
    const HeaderActiveClass = {
        init() {
            let currentPath = window.location.pathname;

            // Caso especial: si la ruta es /result/<product_id>, usar '/'
            if (currentPath.startsWith('/result/')) {
                currentPath = '/';
            }

            const navLinks = document.querySelectorAll('#navmenu a');

            navLinks.forEach(link => {
                const linkPath = link.getAttribute('href');
                if (currentPath === linkPath) {
                    link.classList.add('active');
                } else {
                    link.classList.remove('active');
                }
            });
        }
    }

    /* ======== INITIALIZATION ======== */
    const init = async () => {
        await TranslationSystem.init();
        ScrollManager.init();
        MobileNav.init();
        ThemeManager.init();
        HeaderActiveClass.init();

        // AOS Initialization
        window.AOS?.init({ duration: 600, easing: 'ease-in-out', once: true, mirror: false });
    };

    return { init };

})();

// Export modules
export { TranslationSystem };

// Start application
document.addEventListener('DOMContentLoaded', App.init);