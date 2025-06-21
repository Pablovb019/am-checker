import {TranslationSystem} from '/static/js/main.js';

const Index = (() => {
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
                responseStep1 = await this.simulateApiCall('/api/fetch-reviews', { payload: { url: url } });
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
                const responseStep2 = await this.simulateApiCall('/api/ml-model-analysis', { payload: { product_id: product_id, reviews: reviews }});
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
            try {
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload)
                });

                if (!response.ok) {
                    let errorData;
                    try {
                        errorData = await response.json();
                    } catch (e) {
                        throw new Error(`HTTP ${response.status}`);
                    }
                    throw new Error(errorData.error || `HTTP ${response.status}`);
                }

                return await response.json();

            } catch (error) {
                console.error('API Error:', error);
                throw error;
            }
        }
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

    /* ======== INITIALIZATION ======== */
    const init = async () => {
        FAQModule.init();
        FormValidator.init();
        ModalManager.init();
    };

    return { init };

})();

// Start application
document.addEventListener('DOMContentLoaded', Index.init);