/**
* Template Name: iLanding
* Template URL: https://bootstrapmade.com/ilanding-bootstrap-landing-page-template/
* Updated: Nov 12 2024 with Bootstrap v5.3.3
* Author: BootstrapMade.com
* License: https://bootstrapmade.com/license/
*/

(function() {
  "use strict";

  /**
   * Apply .scrolled class to the body as the page is scrolled down
   */
  function toggleScrolled() {
    const selectBody = document.querySelector('body');
    const selectHeader = document.querySelector('#header');
    if (!selectHeader.classList.contains('scroll-up-sticky') && !selectHeader.classList.contains('sticky-top') && !selectHeader.classList.contains('fixed-top')) return;
    window.scrollY > 100 ? selectBody.classList.add('scrolled') : selectBody.classList.remove('scrolled');
  }

  document.addEventListener('scroll', toggleScrolled);
  window.addEventListener('load', toggleScrolled);

  /**
   * Mobile nav toggle
   */
  const mobileNavToggleBtn = document.querySelector('.mobile-nav-toggle');

  function mobileNavToogle() {
    document.querySelector('body').classList.toggle('mobile-nav-active');
    mobileNavToggleBtn.classList.toggle('bi-list');
    mobileNavToggleBtn.classList.toggle('bi-x');
  }
  if (mobileNavToggleBtn) {
    mobileNavToggleBtn.addEventListener('click', mobileNavToogle);
  }

  /**
   * Toggle dark and light theme with .btn-changeTheme
   */
document.addEventListener('DOMContentLoaded', function() {
  const themeButton = document.querySelector('.btn-changeTheme');
  const icon = themeButton.querySelector('i');

  // Obtener tema guardado o preferencias del sistema
  const savedTheme = localStorage.getItem('theme');
  const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const initialTheme = savedTheme || (systemDark ? 'dark' : 'light');
  if (initialTheme === 'dark' && window.location.pathname === '/') {
    updateFAQSection();
    updateSection2Section();
    updateAnalyzeModalSection();
    updateModalSection();
  }

  // Aplicar tema inicial
  document.body.classList.toggle('dark-theme', initialTheme === 'dark');
  icon.className = initialTheme === 'dark' ? 'bi bi-moon-stars' : 'bi bi-sun';

  themeButton.addEventListener('click', function() {
    const isDark = document.body.classList.toggle('dark-theme');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    if (window.location.pathname === '/') {
      updateFAQSection();
      updateSection2Section();
    }
    icon.className = isDark ? 'bi bi-moon-stars' : 'bi bi-sun';
    icon.style.animation = 'iconSpin 0.5s ease';
    setTimeout(() => icon.style.animation = '', 500);
  });
});

  /**
   * Hide mobile nav on same-page/hash links
   */
  document.querySelectorAll('#navmenu a').forEach(navmenu => {
    navmenu.addEventListener('click', () => {
      if (document.querySelector('.mobile-nav-active')) {
        mobileNavToogle();
      }
    });

  });

  /**
   * Toggle mobile nav dropdowns
   */
  document.querySelectorAll('.navmenu .toggle-dropdown').forEach(navmenu => {
    navmenu.addEventListener('click', function(e) {
      e.preventDefault();
      this.parentNode.classList.toggle('active');
      this.parentNode.nextElementSibling.classList.toggle('dropdown-active');
      e.stopImmediatePropagation();
    });
  });

  /**
   * Scroll top button
   */
  let scrollTop = document.querySelector('.scroll-top');

  function toggleScrollTop() {
    if (scrollTop) {
      window.scrollY > 100 ? scrollTop.classList.add('active') : scrollTop.classList.remove('active');
    }
  }
  scrollTop.addEventListener('click', (e) => {
    e.preventDefault();
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  });

  window.addEventListener('load', toggleScrollTop);
  document.addEventListener('scroll', toggleScrollTop);

  /**
   * Animation on scroll function and init
   */
  function aosInit() {
    AOS.init({
      duration: 600,
      easing: 'ease-in-out',
      once: true,
      mirror: false
    });
  }
  window.addEventListener('load', aosInit);

  /**
   * Frequently Asked Questions Toggle
   */
  document.querySelectorAll('.faq-item h3, .faq-item .faq-toggle').forEach((faqItem) => {
    faqItem.addEventListener('click', () => {
      faqItem.parentNode.classList.toggle('faq-active');
    });
  });

  /**
   * Correct scrolling position upon page load for URLs containing hash links.
   */
  window.addEventListener('load', function(e) {
    if (window.location.hash) {
      if (document.querySelector(window.location.hash)) {
        setTimeout(() => {
          let section = document.querySelector(window.location.hash);
          let scrollMarginTop = getComputedStyle(section).scrollMarginTop;
          window.scrollTo({
            top: section.offsetTop - parseInt(scrollMarginTop),
            behavior: 'smooth'
          });
        }, 100);
      }
    }
  });
})();

/**
 * Handle translation of the page
 */
document.addEventListener('DOMContentLoaded', () => {
    fetch('/static/json/language.json')
        .then(response => response.json())
        .then(data => {
            translations = data;
            initLanguageSystem();
        })
        .catch(error => {
            console.error('Error loading translations:', error);
            translations = {};
        });

    function initLanguageSystem() {
        const browserLang = navigator.language.slice(0,2).toLowerCase();
        const savedLang = localStorage.getItem('language');
        const defaultLang = translations[savedLang] ? savedLang :
                          translations[browserLang] ? browserLang : 'es';

        updateLanguage(defaultLang);
        setupLanguageEvents();
    }

    function updateLanguage(lang) {
        if (!translations[lang]) return;

        document.querySelectorAll('[data-translate]').forEach(el => {
            if (el.tagName.toLowerCase() !== 'title') {
                const key = el.dataset.translate;
                el.innerHTML = DOMPurify.sanitize(translations[lang][key]);
            }
        });

        if(translations[lang].mainTitle) {
            document.title = DOMPurify.sanitize(translations[lang].mainTitle);
        }

        const linkInput = document.querySelector('#urlValidator');
        if (linkInput) linkInput.placeholder = translations[lang].urlPlaceholder;

        const analyzeButton = document.querySelector('button[type="submit"]');
        if (analyzeButton) analyzeButton.textContent = translations[lang].analyzeButton;

        const activeErrors = document.querySelectorAll('.is-invalid');
        if (activeErrors.length > 0) {
            const urlInput = document.getElementById('urlValidator');
            const currentValue = urlInput.value;

            validateAmazonUrl(currentValue).then(validationResult => {
                showValidationError(urlInput, validationResult.errorType);
            });
        }

        const flagElement = document.getElementById('currentFlag');
        const codeElement = document.getElementById('currentLang');
        if (flagElement && codeElement) {
            flagElement.className = `fi fi-${translations[lang].flag}`;
            codeElement.textContent = translations[lang].code.toUpperCase();
        }
    }

    function setupLanguageEvents() {
        document.querySelectorAll('.language-option').forEach(option => {
            option.addEventListener('click', async (e) => {
                e.preventDefault();
                const lang = e.currentTarget.dataset.lang;

                if (translations[lang]) {
                    clearExistingErrors();

                    localStorage.setItem('language', lang);
                    updateLanguage(lang);
                    const urlInput = document.getElementById('urlValidator');
                    if (urlInput.value){
                        const validationResult = await validateAmazonUrl(urlInput.value);
                        if (!validationResult.isValid) {
                            showValidationError(urlInput, validationResult.errorType);
                        }
                    }
                }
            });
        });
    }
});

/**
 * FAQ Section -Change to dark background when dark mode is active
 */
function updateFAQSection() {
    const faqSection = document.getElementById('faq');
    const actualTheme = localStorage.getItem('theme');
    if (faqSection && actualTheme === 'dark') {
        faqSection.classList.remove('light-background');
        faqSection.classList.add('dark-background');
    } else if (faqSection && actualTheme === 'light') {
        faqSection.classList.remove('dark-background');
        faqSection.classList.add('light-background');
    }
}

function updateSection2Section(){
    const section2Section = document.getElementById('section2');
    const actualTheme = localStorage.getItem('theme');
    if (section2Section && actualTheme === 'dark') {
        section2Section.classList.remove('light-background');
        section2Section.classList.add('dark-background');
    } else if (section2Section && actualTheme === 'light') {
        section2Section.classList.remove('dark-background');
        section2Section.classList.add('light-background');
    }
}

/**
 * Validate URL input
 */
document.addEventListener('DOMContentLoaded', function() {
    // Configuración principal de validación
    (function initValidation() {
        'use strict';
        const forms = document.querySelectorAll('.needs-validation');

        Array.from(forms).forEach(form => {
            form.addEventListener('submit', async (event) => {
                event.preventDefault();
                event.stopPropagation();

                const urlInput = document.getElementById('urlValidator');
                const validationResult = await validateAmazonUrl(urlInput.value);

                if (validationResult.isValid && form.checkValidity()) {
                    updateAnalyzeModalSection()
                    const modal = new bootstrap.Modal('#analysisModal', {
                        backdrop: 'static',
                        keyboard: false
                    });
                    modal.show();

                    setTimeout(() => {
                        AOS.refreshHard();
                        }, 100);

                    const result = await startAnalysisProcess(urlInput.value);
                } else {
                    showValidationError(urlInput, validationResult.errorType);
                }

                form.classList.add('was-validated');
            }, false);
        });
    })();

    // Validar URL de Amazon
    async function validateAmazonUrl(url) {
        const strictDomainRegex = /^(https?:\/\/)?(www\.)?(amazon\.com|amazon\.co\.uk)(\/(.)+)?$/i;
        const productPathRegex = /\/dp\//i;

        // Paso 1: Validar campo requerido
        if (!url) {
            return { isValid: false, errorType: 'required' };
        }

        // Paso 2: Validar dominio
        if (!strictDomainRegex.test(url)) {
            return { isValid: false, errorType: 'domain' };
        }

        // Paso 3: Validar estructura de producto
        if (!productPathRegex.test(url)) {
            return { isValid: false, errorType: 'product' };
        }

        // Paso 4: Verificar existencia de la URL
        try {
            const endpointURL = window.location.protocol + '//' + window.location.host + '/api/validate-url';
            const response = await fetch(endpointURL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url })
            });

            const result = await response.json();
            return {
                isValid: result.isValid,
                errorType: result.isValid ? null : 'invalid'
            }

        } catch (error) {
            return { isValid: false, errorType: 'connection_error' };
        }
    }

    // Mostrar errores correctamente
    function showValidationError(input, errorType) {
        const lang = localStorage.getItem('language') || 'es';
        const messages = {
            required: translations[lang].required,
            domain: translations[lang].domain,
            product: translations[lang].product,
            invalid: translations[lang].invalid,
            connection_error: translations[lang].connection_error
        };

        const feedback = input.closest('.input-group').querySelector('.invalid-feedback');
        input.classList.add('is-invalid');
        feedback.textContent = messages[errorType] || messages.invalid
    }

    // Resetear validación al escribir
    const urlInput = document.getElementById('urlValidator');
    if (urlInput) {
        urlInput.addEventListener('input', function(e) {
            this.setCustomValidity('');
            this.classList.remove('is-invalid');
            this.closest('.input-group').querySelector('.invalid-feedback').textContent = '';
        });
    }
});

function clearExistingErrors() {
    document.querySelectorAll('.is-invalid').forEach(el => {
        el.classList.remove('is-invalid');
        el.closest('.input-group').querySelector('.invalid-feedback').textContent = '';
    });
}

function updateAnalyzeModalSection() {
    const analyzeModal = document.getElementById('analysisModal');
    const actualTheme = localStorage.getItem('theme');
    if (analyzeModal && actualTheme === 'dark') {
        analyzeModal.classList.remove('light-background');
        analyzeModal.classList.add('dark-background');
    } else if (analyzeModal && actualTheme === 'light') {
        analyzeModal.classList.remove('dark-background');
        analyzeModal.classList.add('light-background');
    }
}

async function startAnalysisProcess(url) {
    let responseStep1;
    let lang = localStorage.getItem('language') || 'es';
    try {
        updateStepUI(1, 'start', null, translations[lang].step1Description);
        responseStep1 = await simulateApiCall('/api/fetch-reviews', { url })
        updateStepUI(1, 'end', null, translations[lang].step1Description_completed);

    } catch (error) {
        const step = error.step || 1;
        updateStepUI(step, 'error', translations[lang].errorTitle_step1, translations[lang].errorDescription_step1);
        throw error;
    }

    try {
        const { product_id, reviews } = responseStep1;
        updateStepUI(2, 'start', null, translations[lang].step2Description);
        const responseStep2 = await simulateApiCall('/api/ml-model-analysis', { product_id, reviews });
        updateStepUI(2, 'end', null, translations[lang].step2Description_completed);

        window.location.href = `/result/${encodeURIComponent(product_id)}`;
        return responseStep2;
    } catch (error) {
        const step = error.step || 2;
        updateStepUI(step, 'error', translations[lang].errorTitle_step2, translations[lang].errorDescription_step2);
        throw error;
    }
}

function updateStepUI(stepNumber, status, title, message) {
    const step = document.querySelector(`[data-step="${stepNumber}"]`);
    const spinner = step.querySelector('.spinner-border');
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
            } else {
                stepTitle.classList.add('text-success');
                stepMessage.classList.add('text-success');
             }
            step.style.opacity = '0.8';
            break;

        case 'error':
            stepTitle.textContent = title;
            if (actualTheme === 'dark') {
                 stepTitle.classList.add('text-danger-dark');
                stepMessage.classList.add('text-danger-dark');
            } else {
                stepTitle.classList.add('text-danger');
                stepMessage.classList.add('text-danger');
             }
            step.style.opacity = '0.8';
            break;
    }

    // Scroll handling
    const container = document.querySelector('#analysisModal .modal-body');
    container.scrollTop = step.offsetTop - container.offsetTop - 20;
}

async function simulateApiCall(endpoint, payload) {
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

                if (!response.ok) {
                    const error = new Error("API error");
                    error.step = endpoint === '/api/fetch-product' ? 1 : 2;
                    throw error;
                }
                const result = await response.json();
                resolve(result);
            } catch (error) {
                reject({
                    message: 'Failed to complete operation',
                    step: endpoint === '/api/fetch-product' ? 1 : 2
                });
            }
        }, 2000); // Simulate API delay
    });
}

function updateModalSection() {
    const modal = document.getElementById('analysisModal');
    if (!modal) return;

    const isDark = document.body.classList.contains('dark-theme');
    modal.classList.toggle('dark-background', isDark);
    modal.classList.toggle('light-background', !isDark);

    if (modal.classList.contains('show')) {
        modal.style.display = 'none';
        setTimeout(() => modal.style.display = 'block', 10);
    }
}