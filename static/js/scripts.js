// Custom JavaScript for Shopwise e-commerce platform
// Add your custom JavaScript here

(function($) {
    'use strict';
    
    // Document ready
    $(document).ready(function() {
        
        // Product card hover effect
        $('.product_wrap').hover(
            function() {
                $(this).find('.product_action_box').css('opacity', '1');
            },
            function() {
                $(this).find('.product_action_box').css('opacity', '0');
            }
        );
        
        // Smooth scroll for anchor links
        $('a[href^="#"]').on('click', function(event) {
            var target = $(this.getAttribute('href'));
            if( target.length ) {
                event.preventDefault();
                $('html, body').stop().animate({
                    scrollTop: target.offset().top - 100
                }, 1000);
            }
        });
        
        // Form validation
        $('form').on('submit', function(e) {
            var form = $(this);
            var required = form.find('[required]');
            var valid = true;
            
            required.each(function() {
                if ($(this).val() === '') {
                    valid = false;
                    $(this).addClass('is-invalid');
                } else {
                    $(this).removeClass('is-invalid');
                }
            });
            
            if (!valid) {
                e.preventDefault();
                alert('Please fill in all required fields');
            }
        });
        
        // Auto-hide flash messages
        setTimeout(function() {
            $('.alert').fadeOut('slow');
        }, 5000);
        
        // Initialize tooltips if Bootstrap is available
        if (typeof bootstrap !== 'undefined') {
            var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
        }
    });
    
})(jQuery);

