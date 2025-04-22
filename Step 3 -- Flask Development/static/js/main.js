/**
* Template Name: iLanding - Redone from Scratch by Pablo Vilar Bustillo
* Template URL: https://bootstrapmade.com/ilanding-bootstrap-landing-page-template/
* Updated: Nov 12 2024 with Bootstrap v5.3.3
* Author: BootstrapMade.com - Pablo Vilar Bustillo
* License: https://bootstrapmade.com/license/
*/

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

            ChartSystem.refreshCharts();
        },

        animateIcon() {
            this.icon.style.animation = 'iconSpin 0.5s ease';
            setTimeout(() => (this.icon.style.animation = ''), 500);
        }
    };

    /* ======== TRANSLATION SYSTEM ======== */
    const TranslationSystem = {
        translations: {},

        async init() {
            try {
                const response = await fetch('/static/json/language.json');
                this.translations = await response.json();
                this.setupLanguage();
            } catch (error) {
                console.error('Error loading translations:', error);
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
            ChartSystem.refreshCharts();
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

    /* ======== FAQ MODULE ======== */
    const FAQModule = {
        init() {
            this.setupFAQToggle();
        },

        setupFAQToggle() {
            document.querySelectorAll(config.selectors.faqItems).forEach(item => {
                item.addEventListener('click', () => {
                    item.parentNode.classList.toggle('faq-active');
                });
            });
        }
    };

    /* ======== FORM VALIDATION SYSTEM ======== */
    const FormValidator = {
        init() {
            this.forms = document.querySelectorAll('.needs-validation');
            this.urlInput = document.getElementById('urlValidator');
            if (!this.urlInput) return;

            this.setupFormValidation();
            this.setupInputValidation();
        },

        async validateAmazonUrl(url) {
            const strictDomainRegex = /^(https?:\/\/)?(www\.)?(amazon\.com|amazon\.co\.uk)(\/(.)+)?$/i;
            const productPathRegex = /\/dp\//i;

            if (!url) return { isValid: false, errorType: 'required' };
            if (!strictDomainRegex.test(url)) return { isValid: false, errorType: 'domain' };
            if (!productPathRegex.test(url)) return { isValid: false, errorType: 'product' };

            try {
                const endpoint = '/api/validate-url';
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url })
                });

                const result = await response.json();
                return { isValid: result.isValid, errorType: result.isValid ? null : 'invalid' };
            } catch {
                return { isValid: false, errorType: 'connection_error' };
            }
        },

        showError(errorType) {
            const lang = localStorage.getItem('language') || 'es';
            const messages = TranslationSystem.translations[lang];
            if (!messages) return;

            const feedback = this.urlInput.closest('.input-group').querySelector('.invalid-feedback');
            this.urlInput.classList.add('is-invalid');
            feedback.textContent = messages[errorType] || messages.invalid;
        },

        setupFormValidation() {
            this.forms.forEach(form => {
                form.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    const validation = await this.validateAmazonUrl(this.urlInput.value);

                    if (validation.isValid && form.checkValidity()) {
                        const analysisModal = new bootstrap.Modal('#analysisModal', {
                            backdrop: 'static',
                            keyboard: false
                        });

                        const btnClose = document.querySelector('#analysisModal .btn-close');
                        if (btnClose) btnClose.classList.add('d-none');

                        // Limpiar estado anterior al mostrar nuevo modal
                        document.querySelectorAll('[data-step]').forEach(step => {
                            const lang = localStorage.getItem('language') || 'es';
                            const translations = TranslationSystem.translations[lang];
                            step.style.opacity = '1';
                            step.style.transform = 'none';
                            // Reset icons and messages in case an error occurred in a previous analysis
                            step.querySelector('.spinner-border').classList.add('d-none');
                            step.querySelector('.check-icon').classList.add('d-none');
                            step.querySelector('.error-icon').classList.add('d-none');

                            step.querySelector('.step-title').textContent = translations[`step${step.dataset.step}Title`];
                            step.querySelector('.step-title').classList .remove('text-success', 'text-danger');
                            step.querySelector('.step-message').textContent = translations[`step${step.dataset.step}Description`];
                            step.querySelector('.step-message').classList.remove('text-success', 'text-danger');
                        });

                        analysisModal.show();
                        await AnalysisModule.startAnalysis(this.urlInput.value);
                    } else {
                        this.showError(validation.errorType);
                    }
                    form.classList.add('was-validated');
                });
            });
        },

        setupInputValidation() {
            this.urlInput.addEventListener('input', () => {
                this.urlInput.classList.remove('is-invalid');
                this.urlInput.closest('.input-group').querySelector('.invalid-feedback').textContent = '';
            });
        },

        validateOnLanguageChange() {
            const urlInput = document.getElementById('urlValidator');
            if (urlInput && urlInput.value) FormValidator.validateAmazonUrl(urlInput.value);
        }
    };

    /* ======== ANALYSIS MODULE ======== */
    const AnalysisModule = {
        async startAnalysis(url) {
            let responseStep1;
            let lang = localStorage.getItem('language') || 'es';
            const btnClose = document.querySelector('#analysisModal .btn-close');
            const translations = TranslationSystem.translations[lang];
            try {
                this.updateStepUI(1, 'start', null, translations.step1Description);
                responseStep1 = await this.simulateApiCall('/api/fetch-reviews', { url })
                this.updateStepUI(1, 'end', null, translations.step1Description_completed);

            } catch (error) {
                this.updateStepUI(1, 'error', translations.errorTitle_step1, translations.errorDescription_step1);
                this.updateStepUI(2, 'error', translations.errorTitle_step2, translations.errorDescription_step2);
                const analysisModal = bootstrap.Modal.getInstance(document.getElementById('analysisModal'));
                if (analysisModal) {
                    analysisModal._config.backdrop = 'none';
                    btnClose.classList.remove('d-none');
                }
                throw error;
            }

            try {
                const { product_id, reviews } = responseStep1;
                this.updateStepUI(2, 'start', null, translations.step2Description);
                const responseStep2 = await this.simulateApiCall('/api/ml-model-analysis', { product_id, reviews });
                this.updateStepUI(2, 'end', null, translations.step2Description_completed);

                window.location.href = `/result/${encodeURIComponent(product_id)}`;
                const analysisModal = bootstrap.Modal.getInstance(document.getElementById('analysisModal'));
                if (analysisModal) analysisModal.hide();
                return responseStep2;

            } catch (error) {
                this.updateStepUI(2, 'error', translations.errorTitle_step2, translations.errorDescription_step2);
                const analysisModal = bootstrap.Modal.getInstance(document.getElementById('analysisModal'));
                if (analysisModal) {
                    analysisModal._config.backdrop = 'none';
                    btnClose.classList.remove('d-none');
                }
                throw error;
            }
        },

        updateStepUI(stepNumber, status, title, message) {
            const step = document.querySelector(`[data-step="${stepNumber}"]`);
            const spinner = step.querySelector('.spinner-border');
            const checkIcon = step.querySelector('.check-icon');
            const errorIcon = step.querySelector('.error-icon');
            const stepTitle = step.querySelector('.step-title');
            const stepMessage = step.querySelector('.step-message');
            const actualTheme = localStorage.getItem('theme');

            // Reset all states
            spinner.classList.add('d-none');
            stepTitle.classList.remove('text-success', 'text-danger');
            stepMessage.classList.remove('text-success', 'text-danger');

            // Update content
            stepMessage.textContent = message;

            switch(status) {
                case 'start':
                    spinner.classList.remove('d-none', 'spinner-border-sm');
                    step.style.opacity = '1';
                    step.style.transform = 'translateY(0)';
                    break;

                case 'end':
                    if (actualTheme === 'dark') {
                        stepTitle.classList.add('text-success-dark');
                        stepMessage.classList.add('text-success-dark');
                        checkIcon.classList.add('text-success-dark');
                    } else {
                        stepTitle.classList.add('text-success');
                        stepMessage.classList.add('text-success');
                        checkIcon.classList.add('text-success');
                    }
                    checkIcon.classList.remove('d-none');
                    step.style.opacity = '0.8';
                    break;

                case 'error':
                    stepTitle.textContent = title;
                    if (actualTheme === 'dark') {
                        stepTitle.classList.add('text-danger-dark');
                        stepMessage.classList.add('text-danger-dark');
                        errorIcon.classList.add('text-danger-dark');
                    } else {
                        stepTitle.classList.add('text-danger');
                        stepMessage.classList.add('text-danger');
                        errorIcon.classList.add('text-danger');
                    }
                    errorIcon.classList.remove('d-none');
                    step.style.opacity = '0.8';
                    break;
            }

            // Scroll handling
            const container = document.querySelector('#analysisModal .modal-body');
            container.scrollTo ({
                top: step.offsetTop - container.offsetTop - 20,
                behavior: 'smooth'
            });
        },

        async simulateApiCall(endpoint, payload) {
            return new Promise((resolve, reject) => {
                setTimeout(async () => {
                    try {
                        const response = await fetch(endpoint, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({ payload })
                        });

                        if (response.status !== 200) {
                            throw new Error('Error in API call');
                        } else {
                            const result = await response.json();
                            resolve(result);
                        }

                    } catch (error) {
                        reject({
                            message: 'Failed to complete operation',
                        });
                    }
                }, 500);
            });
        }
    };

    /* ======== PROGRESS CIRCLES ======== */
    const ProgressCircles = {
        init() {
            this.initProgressCircles();
        },

        getProgressColor(value) {
            const red = Math.round(255 - (value * 255));
            const green = Math.round(150 + (value * 105));
            const blue = Math.round(70 - (value * 20));
            return `rgb(${red}, ${green}, ${blue})`;
        },

        formatPercentage(value) {
            const formatted = (value * 100).toFixed(4);
            return formatted.endsWith('.0000')
                ? `${Math.round(value * 100)}%`
                : `${Number(formatted).toFixed(2).replace(/\.?0+$/, '')} %`;
        },

        initProgressCircles() {
            const self = this;
            $('[data-class="review-circle"], [data-class="result-circle"]').each(function() {
                const $element = $(this);
                const rawValue = parseFloat($element.data('value')) || 0;
                const max = parseFloat($element.data('max')) || 100;
                const percentage = rawValue / max;

                if ($element.data('circle-progress')) {
                    $element.circleProgress('destroy');
                }

                $element.circleProgress({
                    value: percentage,
                    size: 150,
                    thickness: 12,
                    fill: { color: self.getProgressColor(percentage) },
                    emptyFill: 'rgba(13, 131, 253, 0.1)',
                    startAngle: -Math.PI/2,
                    animation: false,
                    lineCap: 'round'
                });

                const $container = $element.parent();
                let $text = $container.find('.circle-text-overlay');
                const displayValue = self.formatPercentage(percentage);

                if ($text.length === 0) {
                    $text = $('<div class="circle-text-overlay"></div>');
                    $container.append($text);
                }

                $text.text(displayValue);
            });

            if (window.location.pathname === '/recent') {
                $('[data-class="recent-circle"]').each(function() {
                    const $element = $(this);
                    const rawValue = parseFloat($element.data('value')) || 0;
                    const max = parseFloat($element.data('max')) || 100;
                    const percentage = rawValue / max;

                    $(this).circleProgress({
                        value: percentage,
                        size: 80,
                        thickness: 8,
                        fill: { color: self.getProgressColor(percentage) },
                        emptyFill: 'rgba(13, 131, 253, 0.1)',
                        startAngle: -Math.PI/2,
                        animation: false,
                        lineCap: 'round'
                    });

                    const $container = $element.parent();
                    let $text = $container.find('.circle-text-overlay');
                    const displayValue = self.formatPercentage(percentage);

                    if ($text.length === 0) {
                        $text = $('<div class="circle-text-overlay"></div>');
                        $container.append($text);
                    }

                    $text.text(displayValue);
                });
            }
        }
    };

    /* ======== PAGINATION SYSTEM ======== */
    const PaginationSystem = {
        mainState: {
            currentPage: 1,
            reviewsPerPage: 10,
            allReviews: []
        },

        modalState: {
            currentPage: 1,
            reviewsPerPage: 10,
            allReviews: []
        },

        init() {
            if (!document.getElementById('reviewsContainer')) return;
            this.setupPaginationControls();
            this.setupModalPagination();
            window.addEventListener('resize', () => this.checkTextOverflow());
        },

        setupPaginationControls() {
            document.getElementById('prevPage')?.addEventListener('click', () => this.handlePagination(-1, true));
            document.getElementById('nextPage')?.addEventListener('click', () => this.handlePagination(1, true));
        },

        handlePagination(direction, isModal = false) {
            const state = isModal ? this.modalState : this.mainState;
            const newPage = state.currentPage + direction;
            const maxPage = Math.ceil(state.allReviews.length / state.reviewsPerPage);

            state.currentPage = Math.max(1, Math.min(newPage, maxPage));
            this.updatePaginationDisplay(isModal);
        },

        setupModalPagination() {
            document.getElementById('allReviewsModal')?.addEventListener('show.bs.modal', () => {
                // Get all hidden templates
                const templates = document.querySelectorAll('#reviewTemplates .review-template');

                // Reset and populate modal state
                this.modalState.allReviews = Array.from(templates).map(template => template.cloneNode(true));
                this.modalState.currentPage = 1;
                this.modalState.reviewsPerPage = 10;

                this.updatePaginationDisplay(true);
            });
        },

        updatePaginationDisplay(isModal = false) {
            const state = isModal ? this.modalState : this.mainState;
            const lang = localStorage.getItem('language') || 'es';
            const translations = TranslationSystem.translations[lang] || {};
            const container = document.getElementById('reviewsContainer');

            const paginationInfo = document.getElementById('paginationInfo');
            const totalReviews = state.allReviews.length;

            const prevButton = document.getElementById('prevPage');
            const nextButton = document.getElementById('nextPage');

            container.innerHTML = '';

            // Calculate visible range
            const start = (state.currentPage - 1) * state.reviewsPerPage;
            const end = start + state.reviewsPerPage;
            const reviewsToShow = state.allReviews.slice(start, end);

            // Add clones with animation
            reviewsToShow.forEach((reviewClone, index) => {
                reviewClone.style.opacity = '0';
                reviewClone.style.transform = 'translateY(20px)';
                container.appendChild(reviewClone);

                // Animate after short delay
                setTimeout(() => {
                    reviewClone.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
                    reviewClone.style.opacity = '1';
                    reviewClone.style.transform = 'translateY(0)';
                }, index * 50);
            });

            // Actualizar controles
            prevButton.disabled = state.currentPage === 1;
            nextButton.disabled = end >= totalReviews;

            // Texto de paginación
            paginationInfo.textContent = `${translations.showing || 'Mostrando'} ${start + 1}-${Math.min(end, totalReviews)} ${translations.of || 'de'} ${totalReviews} ${translations.reviews || 'reseñas'}`;

            // Forzar redibujado del modal
            if (isModal) {
                container.scrollTo({
                    top: 0,
                    behavior: 'smooth'
                });

                ProgressCircles.initProgressCircles();
            }
        },
    };

    /* ======== EXPAND TOGGLE HANDLER ======== */
    const ExpandToggleHandler = {
        handleToggle(e) {
            const toggle = e.target.closest('.expand-toggle');
            if (!toggle) return;

            const container = toggle.closest('.review-text-container');
            if (!container) return;

            const textElement = container.querySelector('.review-text');
            if (!textElement) return;

            const lang = localStorage.getItem('language') || 'es';
            const translations = TranslationSystem.translations[lang] || {};

            const isTruncated = container.classList.contains('truncated');
            if (isTruncated) {
                container.classList.remove('truncated');
                textElement.style.maxHeight = 'none';
                toggle.textContent = translations.showLessText;
            } else {
                container.classList.add('truncated');
                const lineHeight = parseInt(getComputedStyle(textElement).lineHeight);
                textElement.style.maxHeight = `${lineHeight * 3}px`;
                toggle.textContent = translations.showMoreText;
            }
        },

        updateToggleVisibility() {
            let containerHeight = 0;
            document.querySelectorAll('.review-text-container').forEach(container => {
                if (containerHeight < container.getBoundingClientRect().height) {
                    containerHeight = container.getBoundingClientRect().height;
                }

                const textElement = container.querySelector('.review-text');
                if (!textElement) return;

                const textLength = textElement.scrollHeight;
                const lineHeight = parseInt(getComputedStyle(textElement).lineHeight);
                const maxHeight = lineHeight * 4;

                if (textLength < maxHeight) {
                    // No need to truncate
                    container.classList.remove('truncated');
                    textElement.style.maxHeight = 'none';

                    const toggle = container.querySelector('.expand-toggle');
                    if (toggle) {
                        toggle.style.display = 'none';
                    }

                    // Compensate for the height of the text
                    container.style.height = `${containerHeight}px`;
                }
            });
        },

        init() {
            document.addEventListener('DOMContentLoaded', () => this.updateToggleVisibility());
            document.addEventListener('click', (e) => this.handleToggle(e));

            window.addEventListener('load', () => this.updateToggleVisibility());
            window.addEventListener('resize', () => this.updateToggleVisibility());
        },
    };

    /* ======== MODAL ARIA-LABEL ======== */
    const ModalManager = {
        init() {
            const modalReview = document.getElementById('allReviewsModal');
            if (modalReview) {
                modalReview.addEventListener('hide.bs.modal', function () {
                    const activeElement = document.activeElement;
                    if (this.contains(activeElement)) {
                        activeElement.blur();
                    }
                });
            }

            const analysisModal = document.getElementById('analysisModal');
            if (analysisModal) {
                analysisModal.addEventListener('hide.bs.modal', function () {
                    const activeElement = document.activeElement;
                    if (this.contains(activeElement)) {
                        activeElement.blur();
                    }
                });
            }
        }
    };

    /* ======== CHART SYSTEM ======== */
    const ChartSystem = {
        statsData: null,
        currentCharts: {},
        currentActivePill: null,
        hasData: false,


        init() {
            const dataContainer = document.getElementById('statsDataContainer');
            if (!dataContainer) {
                this.hasData = false;
                return;
            }

            try {
                this.statsData = JSON.parse(dataContainer.dataset.stats.replace(/&quot;/g, '"'));
                this.validatedStats = this.validateStats(this.statsData);
                this.validatedStats.sort((a, b) => new Date(a.snapshot_date) - new Date(b.snapshot_date));
                this.currentActivePill = document.querySelector('.date-pill.active');
                this.hasData = true;

                this.initTrendChart();
                this.initDatePills();
                this.updateCharts(this.validatedStats[0]);
            } catch (error) {
                console.error("Error parsing stats data:", error);
                this.hasData = false;
            }
        },

        validateStats(stats) {
            return stats.map(stat => ({
                ...stat,
                total_products: Number(stat.total_products),
                total_reviews: Number(stat.total_reviews),
                total_users: Number(stat.total_users),
                percent_authentic_products: Number(stat.percent_authentic_products),
                percent_robotized_reviews: Number(stat.percent_robotized_reviews),
            }));
        },

        refreshCharts() {
            if (!this.hasData) return;

            if (this.currentCharts.trend) {
                this.currentCharts.trend.destroy();
            }
            if (this.currentCharts.category) {
                this.currentCharts.category.destroy();
            }

            this.initTrendChart();
            this.updateCharts(this.validatedStats[this.currentActivePill.dataset.index]);
        },

        initTrendChart() {
            if (!this.validatedStats || !this.validatedStats.map) return;

            const rootStyles = getComputedStyle(document.documentElement);
            const accentColor = rootStyles.getPropertyValue('--accent-color').trim();
            const headingColor = rootStyles.getPropertyValue('--heading-color').trim();
            const surfaceColor = rootStyles.getPropertyValue('--surface-color').trim();

            const chartGridColor = rootStyles.getPropertyValue('--chart-grid-color').trim();
            const chartTextColor = rootStyles.getPropertyValue('--chart-text-color').trim();

            const headingFont = rootStyles.getPropertyValue('--heading-font').trim();
            const defaultFont = rootStyles.getPropertyValue('--default-font').trim();

            const lang = localStorage.getItem('language') || 'es';
            const ctx = document.getElementById('trendChart');
            const translations = TranslationSystem.translations[lang] || {};

            this.currentCharts.trend = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: this.validatedStats.map(d => new Date(d.snapshot_date).toLocaleDateString(lang, {
                        day: '2-digit',
                        month: 'short'
                    })),
                    datasets: [{
                        label: translations.dailyReviews,
                        data: this.validatedStats.map(d => d.total_reviews),
                        borderColor: accentColor,
                        backgroundColor: accentColor,
                        tension: 0.4,
                        fill: false
                    }]
                },
                options: {
                    maintainAspectRatio: false,
                    responsive: true,
                    plugins: {
                        legend: { position: 'bottom', labels: { color: chartTextColor }, font: { family: headingFont } },
                        tooltip: {mode: 'index', backgroundColor: surfaceColor, titleColor: headingColor, bodyColor: headingColor, borderColor: accentColor}
                    },
                    scales: {
                        x: {
                            grid: { color: chartGridColor },
                            ticks: { color: chartTextColor, font: { family: defaultFont } }
                        },
                        y: {
                            grid: { color: chartGridColor },
                            ticks: { color: chartTextColor, font: { family: defaultFont } }
                        }
                    }
                }
            });
        },

        initDatePills() {
            document.querySelectorAll('.date-pill').forEach(pill => {
                pill.addEventListener('click', (e) => {
                    if (e.currentTarget.classList.contains('active')) return;

                    this.currentActivePill.classList.remove('active');
                    e.currentTarget.classList.add('active');
                    this.currentActivePill = e.currentTarget;

                    const index = parseInt(e.currentTarget.dataset.index);
                    this.updateCharts(this.validatedStats[index]);
                });
            });
        },

        updateCharts(selectedData) {
            if (!this.hasData || !selectedData) return;

            this.animateValue('totalProducts', this.safeNumber(selectedData.total_products));
            this.animateValue('totalReviews', this.safeNumber(selectedData.total_reviews));
            this.animateValue('activeUsers', this.safeNumber(selectedData.total_users));
            this.animateValue('avgAuthenticity', this.safeNumber(selectedData.percent_authentic_products), true);
            this.animateValue('authenticPercent', this.safeNumber(selectedData.percent_authentic_products), true);
            this.animateValue('robotizedPercent', this.safeNumber(selectedData.percent_robotized_reviews), true);

            this.updateCategoryChart(selectedData);
            this.updateCategoryCards(selectedData);
        },

        safeNumber(value) {
            const num = Number(value);
            return isNaN(num) ? 0 : num;
        },

        animateValue(elementId, value, isPercentage = false) {
            const element = document.getElementById(elementId);
            const current = parseFloat(element.textContent.replace(/[%,]/g, '')) || 0;
            const suffix = isPercentage ? '%' : '';
            const decimals = (elementId === 'avgAuthenticity' || elementId.includes('Percent')) ? 2 : 0;

            const countUp = new CountUp(element, current, value, decimals, 1, {
                useEasing: true,
                useGrouping: true,
                separator: ',',
                decimal: '.',
                suffix: suffix
            });

            if (!countUp.error) countUp.start();
        },

        updateCategoryChart(selectedData) {
            const lang = localStorage.getItem('language') || 'es';
            const ctx = document.getElementById('categoryChart');
            const translations = TranslationSystem.translations[lang] || {};

            const rootStyles = getComputedStyle(document.documentElement);
            const accentColor = rootStyles.getPropertyValue('--accent-color').trim();
            const secondaryColor = rootStyles.getPropertyValue('--secondary-color').trim();
            const headingColor = rootStyles.getPropertyValue('--heading-color').trim();
            const surfaceColor = rootStyles.getPropertyValue('--surface-color').trim();

            const chartGridColor = rootStyles.getPropertyValue('--chart-grid-color').trim();
            const chartTextColor = rootStyles.getPropertyValue('--chart-text-color').trim();

            const headingFont = rootStyles.getPropertyValue('--heading-font').trim();

            if (this.currentCharts.category) this.currentCharts.category.destroy();

            this.currentCharts.category = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: [
                        translations.authentic,
                        translations.robotized
                    ],
                    datasets: [{
                        data: [
                            selectedData.percent_authentic_products,
                            selectedData.percent_robotized_reviews
                        ],
                        backgroundColor: [accentColor, secondaryColor],
                        borderColor: surfaceColor,
                        borderWidth: 2,
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'bottom', labels: { color: chartTextColor }, font: { family: headingFont } },
                        tooltip: {mode: 'index', backgroundColor: surfaceColor, titleColor: headingColor, bodyColor: headingColor, borderColor: accentColor}
                    },
                }
            });
        },

        updateCategoryCards(selectedData) {
            const lang = localStorage.getItem('language') || 'es';
            const cards = document.querySelectorAll('.category-card');
            const dataMapping = [
                { key: 'best_category_authentic_products', type: 'text' },
                { key: 'worst_category_robotized_products', type: 'text' },
                { key: 'best_category_reviews_authentic', type: 'text' },
                { key: 'worst_category_reviews_robotized', type: 'text' },
                { key: 'day_most_analysis', type: 'date' },
                { key: 'hour_interval_most_analysis', type: 'text' }
            ];

            cards.forEach((card, index) => {
                const { key, type } = dataMapping[index];
                const element = card.querySelector('.category-name');
                const value = selectedData[key];

                if (type === 'date') {
                    element.textContent = new Date(value).toLocaleDateString(lang, {
                        day: '2-digit',
                        month: '2-digit',
                        year: 'numeric'
                    });
                } else {
                    element.textContent = value;
                }
            });
        }
    };

    /* ======== INITIALIZATION ======== */
    const init = () => {
        ScrollManager.init();
        MobileNav.init();
        ThemeManager.init();
        TranslationSystem.init();
        HeaderActiveClass.init();
        FAQModule.init()
        FormValidator.init();
        ProgressCircles.init();
        PaginationSystem.init();
        ExpandToggleHandler.init();
        ModalManager.init();
        ChartSystem.init();

        // AOS Initialization
        window.AOS?.init({ duration: 600, easing: 'ease-in-out', once: true, mirror: false });
    };

    return { init };

})();

// Start application
document.addEventListener('DOMContentLoaded', App.init);