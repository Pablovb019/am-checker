import {TranslationSystem} from '/static/js/main.js';

const Analysis = (() => {
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
            return `${(value * 100).toFixed(2)} %`;
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

    /* ======== CHART SYSTEM ======== */
    const ChartSystem = {
        statsData: null,
        currentCharts: {},
        currentActivePill: null,
        hasData: false,

        init() {
            const dataAuthenticity = document.getElementById('authDistributionData');
            if (dataAuthenticity) {
                this.hasData = true;
                this.initAuthenticityDistributionChart();
            } else {
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
            }
        },

        validateStats(stats) {
            return stats.map(stat => ({
                ...stat,
                total_products: Number(stat.total_products),
                total_reviews: Number(stat.total_reviews),
                total_users: Number(stat.total_users),
                percent_authentic_products: Number(stat.percent_authentic_products),
                percent_robotized_products: Number(stat.percent_robotized_products),
            }));
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

        initAuthenticityDistributionChart() {
            const dataContainer = document.getElementById('authDistributionData');
            if (!dataContainer) return;

            if (this.currentCharts.authenticityDist) {
                this.currentCharts.authenticityDist.destroy();
            }

            const labels = JSON.parse(dataContainer.dataset.labels);
            const values = JSON.parse(dataContainer.dataset.values);

            const lang = localStorage.getItem('language') || 'es';
            const ctx = document.getElementById('authenticityDistributionChart');
            const translations = TranslationSystem.translations[lang] || {};

            this.currentCharts.authenticityDist = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: translations.authenticityDistributionText,
                        data: values,
                        backgroundColor: this.getBarColors(),
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: this.getTooltipStyle()
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: this.getTickStyle()
                        },
                        x: {
                            ticks: this.getTickStyle()
                        }
                    }
                }
            });
        },

        getBarColors() {
            return [
                'rgba(255, 99, 132, 0.7)',  // 0-20
                'rgba(255, 159, 64, 0.7)',  // 20-40
                'rgba(255, 205, 86, 0.7)',  // 40-60
                'rgba(75, 192, 192, 0.7)',  // 60-80
                'rgba(54, 162, 235, 0.7)'   // 80-100
            ];
        },

        getTooltipStyle() {
            const lang = localStorage.getItem('language') || 'es';
            const translations = TranslationSystem.translations[lang] || {};

            return {
                backgroundColor: getComputedStyle(document.documentElement).getPropertyValue('--surface-color'),
                titleColor: getComputedStyle(document.documentElement).getPropertyValue('--heading-color'),
                bodyColor: getComputedStyle(document.documentElement).getPropertyValue('--default-color'),
                borderColor: getComputedStyle(document.documentElement).getPropertyValue('--accent-color'),
                borderWidth: 1,
                callbacks: {
                    label: (context) => {
                        const label = translations.authenticityReviewsLabel;
                        const value = context.parsed.y || context.parsed;
                        return `${label}: ${value}`;
                    }
                }
            };
        },

        getTickStyle() {
            const rootStyles = getComputedStyle(document.documentElement);
            return {
                color: rootStyles.getPropertyValue('--chart-text-color'),
                font: {
                    family: rootStyles.getPropertyValue('--default-font'),
                    size: 12
                }
            };
        },

        updateCharts(selectedData) {
            if (!this.hasData || !selectedData) return;

            this.animateValue('totalProducts', this.safeNumber(selectedData.total_products));
            this.animateValue('totalReviews', this.safeNumber(selectedData.total_reviews));
            this.animateValue('activeUsers', this.safeNumber(selectedData.total_users));
            this.animateValue('avgAuthenticity', this.safeNumber(selectedData.percent_authentic_products), true);
            this.animateValue('authenticPercent', this.safeNumber(selectedData.percent_authentic_products), true);
            this.animateValue('robotizedPercent', this.safeNumber(selectedData.percent_robotized_products), true);

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
                            selectedData.percent_robotized_products
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
                { key: 'best_category_authentic_reviews', type: 'text' },
                { key: 'worst_category_robotized_products', type: 'text' },
                { key: 'worst_category_robotized_reviews', type: 'text' },
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
        },

        refreshCharts() {
            if (!this.hasData) return;

            Object.keys(this.currentCharts).forEach(key => {
                if (this.currentCharts[key]) {
                    this.currentCharts[key].destroy();
                    delete this.currentCharts[key];
                }
            });

            const authDataExists = document.getElementById('authDistributionData');
            const trendDataExists = document.getElementById('trendChart');

            if (authDataExists) {
                this.initAuthenticityDistributionChart();
            } else if (trendDataExists) {
                this.initTrendChart();
                this.updateCharts(this.validatedStats[this.currentActivePill.dataset.index]);
            }
        }
    };

    /* ======== PAGINATION SYSTEM ======== */
    const PaginationSystem = {
        mainState: {
            currentPage: 1,
            reviewsPerPage: 10,
            currentSort: null,
            allReviews: []
        },

        modalState: {
            currentPage: 1,
            reviewsPerPage: 10,
            currentSort: null,
            allReviews: [],
            defaultReviews: [],
            rawTemplates: []
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
                const templates = document.querySelectorAll('#reviewTemplates .review-template');
                if (this.modalState.rawTemplates.length === 0) {
                    this.modalState.rawTemplates = [...templates];
                }

                this.modalState.defaultReviews = this.modalState.rawTemplates.map(template => {
                    const clone = template.cloneNode(true);
                    return {
                        element: clone,
                        accuracy: parseFloat(clone.querySelector('.circle-progress').dataset.value)
                    };
                });

                this.modalState.allReviews = [...this.modalState.defaultReviews];
                this.modalState.currentSort = null;
                this.modalState.currentPage = 1;
                this.modalState.reviewsPerPage = 10;
                this.updatePaginationDisplay(true);
            });
        },

        applySorting(order){
            this.modalState.currentSort = order;
            this.modalState.allReviews = [...this.modalState.defaultReviews].sort((a, b) =>
                order === 'desc' ? b.accuracy - a.accuracy : a.accuracy - b.accuracy
            );
            this.modalState.currentPage = 1;
            this.updatePaginationDisplay(true);
        },

        init() {
            if (!document.getElementById('reviewsContainer')) return;
            this.setupPaginationControls();
            this.setupModalPagination();

            document.getElementById('clearSort')?.addEventListener('click', () => {
                this.modalState.currentSort = null;
                this.modalState.allReviews = [...this.modalState.defaultReviews];
                this.modalState.currentPage = 1;

                document.querySelectorAll('.btn-sort').forEach(b => {
                    b.classList.remove('active');
                    b.disabled = false;
                });

                this.updatePaginationDisplay(true);
            });

            window.addEventListener('resize', () => this.checkTextOverflow());

            document.querySelectorAll('.btn-sort').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const clickedButton = e.currentTarget;
                    if (clickedButton.disabled) return;
                    const sortOrder = e.currentTarget.dataset.sort;
                    this.applySorting(sortOrder);

                    document.querySelectorAll('.btn-sort').forEach(b => {
                        b.classList.remove('active');
                        b.disabled = false;
                    });

                    clickedButton.classList.add('active');
                    clickedButton.disabled = true;

                    const clearSortBtn = document.getElementById('clearSort');
                    if (clearSortBtn) {
                        clearSortBtn.style.display = 'inline-block';
                    }
                });
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

            const start = (state.currentPage - 1) * state.reviewsPerPage;
            const end = start + state.reviewsPerPage;
            const reviewsToShow = state.allReviews.slice(start, end).map(r => r.element);

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

            prevButton.disabled = state.currentPage === 1;
            nextButton.disabled = end >= totalReviews;
            paginationInfo.textContent = `${translations.showing || 'Mostrando'} ${start + 1}-${Math.min(end, totalReviews)} ${translations.of || 'de'} ${totalReviews} ${translations.reviews || 'reseñas'}`;

            if (isModal) {
                const clearSortBtn = document.getElementById('clearSort');
                if (clearSortBtn) {
                    clearSortBtn.style.display = state.currentSort ? 'inline-block' : 'none';
                }
                container.scrollTo({ top: 0, behavior: 'smooth' });
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

    /* ======== INITIALIZATION ======== */
    const init = async () => {
        ProgressCircles.init();
        ChartSystem.init();
        PaginationSystem.init();
        ExpandToggleHandler.init();
        ModalManager.init();
    };

    return { init };

})();

// Start application
document.addEventListener('DOMContentLoaded', Analysis.init);