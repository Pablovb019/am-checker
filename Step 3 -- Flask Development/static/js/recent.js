import {TranslationSystem} from '/static/js/main.js';

const Recent = (() => {
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

    /* ======== INITIALIZATION ======== */
    const init = async () => {
        ProgressCircles.init();
    };

    return { init };

})();

// Start application
document.addEventListener('DOMContentLoaded', Recent.init);