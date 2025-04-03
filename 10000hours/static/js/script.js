// Complete fixed JavaScript for star animation

$(document).ready(function() {
    // Theme toggle functionality
    setupThemeToggle();
    
    // Star animation functionality
    setupStarAnimation();
    
        // More robust theme toggle function
    function setupThemeToggle() {
        console.log("Setting up theme toggle...");
        
        // Check if user has a theme preference stored
        const currentTheme = localStorage.getItem('theme') || 'cyber';
        console.log("Current theme from localStorage:", currentTheme);
        
        setTheme(currentTheme);
        
        // Use event delegation for better compatibility with dynamically loaded content
        $(document).on('click', '#theme-toggle', function() {
            console.log("Theme toggle clicked!");
            const currentTheme = $('body').hasClass('theme-cyber') ? 'cyber' : 'retro';
            console.log("Current theme detected:", currentTheme);
            
            const newTheme = currentTheme === 'cyber' ? 'retro' : 'cyber';
            console.log("Switching to:", newTheme);
            
            setTheme(newTheme);
            localStorage.setItem('theme', newTheme);
        });
    }
        
    function setTheme(theme) {
        if (theme === 'cyber') {
            $('body').removeClass('theme-retro').addClass('theme-cyber');
            $('#theme-toggle-icon').removeClass('fa-microchip').addClass('fa-computer');
            $('#theme-toggle-text').text('Switch to Retro');
        } else {
            $('body').removeClass('theme-cyber').addClass('theme-retro');
            $('#theme-toggle-icon').removeClass('fa-computer').addClass('fa-microchip');
            $('#theme-toggle-text').text('Switch to Cyber');
        }
    }
    
    function setupStarAnimation() {
        // Only run star animation if we're on a page with the progress tracker
        if ($('.total-hours').length === 0) return;
        
        // Get the raw value of total_hours directly from the span
        const totalHoursText = $('.total-hours').text().trim();
        const totalHours = parseFloat(totalHoursText.split('/')[0].trim());
        
        console.log('Total hours text:', totalHoursText);
        console.log('Extracted total hours:', totalHours);
        
        // Calculate stars (1 star per 500 hours)
        const starsCount = Math.floor(totalHours / 500);
        
        // Make sure we don't exceed 20 stars
        const maxStars = Math.min(starsCount, 20);
        
        console.log('Stars earned:', maxStars);
        
        // Clear any existing stars
        $('.star-container').empty();
        
        // Update the stars counter text
        $('.stars-collected span').text(maxStars + ' / 20 Stars');
        
        // Need to ensure star container and vase have proper positioning and style
        ensureProperStarContainerSetup();
        
        // Add stars with proper falling animation
        if (maxStars > 0) {
            for (let i = 0; i < maxStars; i++) {
                // Delay each star slightly for better visual effect
                setTimeout(function() {
                    addFallingStarWithoutOverlap(i, maxStars);
                }, i * 500);
            }
        }
        
        // Check if vase is complete (100%)
        if (totalHours >= 10000) {
            $('.vase-body').addClass('complete');
            celebrateCompletion();
        }
    }
    
    function ensureProperStarContainerSetup() {
        // Make sure the container structure allows stars to appear above the vase
        $('.vase').css({
            'position': 'relative',
            'overflow': 'visible'
        });
        
        $('.star-container').css({
            'position': 'absolute',
            'width': '100%',
            'height': '100%',
            'top': '0',
            'left': '0',
            'overflow': 'visible'
        });
        
        // Make parent containers allow overflow
        $('.bottle-sidebar, #bottle-container').css('overflow', 'visible');
        
        // Add a parent container for perspective if needed
        if ($('.star-perspective-container').length === 0) {
            $('.star-container').wrap('<div class="star-perspective-container"></div>');
            $('.star-perspective-container').css({
                'position': 'absolute',
                'width': '100%',
                'height': '200%', // Extra height above the vase
                'top': '-100%', // Start above the vase
                'left': '0',
                'overflow': 'visible',
                'pointer-events': 'none' // Don't block interactions
            });
        }
    }
    
    function addFallingStarWithoutOverlap(index, totalStars) {
        // Get vase dimensions
        const vaseHeight = $('.vase-body').height();
        const vaseTop = $('.vase-body').offset().top;
        const vaseWidth = $('.vase-body').width();
        
        // Create the star
        const star = $('<div></div>')
            .addClass('star')
            .text('★')
            .css({
                'opacity': '0',
                'position': 'absolute',
                'font-size': '3.5rem',
                'color': '#FFFF00',
                'text-shadow': '0 0 15px rgba(255, 255, 0, 0.8)',
                'animation': 'onlyTwinkle 3s infinite alternate',
                'z-index': '5'
            });
        
        // Add to DOM
        $('.star-container').append(star);
        
        // Calculate random starting position ABOVE the vase
        const startAngle = -30 + Math.random() * 60; // Random angle
        const startX = 10 + Math.random() * 80; // Random X position
        
        // Set starting position above the vase
        star.css({
            'top': '-200px', // Start well above the container
            'left': startX + '%',
            'transform': 'rotate(' + startAngle + 'deg)',
            'transition': 'none'
        });
        
        // Calculate non-overlapping final position
        const finalPosition = calculateNonOverlappingPosition(index, totalStars);
        
        // Show star at starting position
        setTimeout(function() {
            star.css('opacity', '1');
            
            // Then start falling animation after a tiny delay
            setTimeout(function() {
                star.css({
                    'top': finalPosition.y + '%',
                    'left': finalPosition.x + '%',
                    'transition': 'top 2s ease-in, left 2s ease-in-out'
                });
            }, 30);
        }, 10);
    }
    
    function calculateNonOverlappingPosition(index, totalStars) {
        // Create a grid system to prevent overlapping
        let starsPerRow;
        
        if (totalStars <= 5) {
            starsPerRow = 2; // 2 stars per row for 1-5 stars
        } else if (totalStars <= 10) {
            starsPerRow = 3; // 3 stars per row for 6-10 stars
        } else if (totalStars <= 15) {
            starsPerRow = 4; // 4 stars per row for 11-15 stars
        } else {
            starsPerRow = 5; // 5 stars per row for 16-20 stars
        }
        
        // Calculate row and column for this star
        const row = Math.floor(index / starsPerRow);
        const col = index % starsPerRow;
        
        // Calculate cell size as percentage
        const cellWidth = 100 / starsPerRow;
        const cellHeight = 100 / Math.ceil(totalStars / starsPerRow);
        
        // Add some randomness within the cell, but keep away from edges
        const randomX = (Math.random() * 0.3) * cellWidth;
        const randomY = (Math.random() * 0.3) * cellHeight;
        
        // Calculate final position with padding
        const landX = (col * cellWidth) + (cellWidth * 0.35) + randomX;
        const landY = (row * cellHeight) + (cellHeight * 0.35) + randomY;
        
        // Ensure stars stay within container bounds
        return {
            x: Math.min(Math.max(landX, 10), 90),
            y: Math.min(Math.max(landY, 10), 90)
        };
    }
    
    function celebrateCompletion() {
        // Add celebration effects when all 20 stars are collected
        $('.star').css('animation-duration', '2s');
        
        // Add a subtle pulsing glow to the entire vase
        setInterval(function() {
            $('.vase-body').toggleClass('complete-pulse');
        }, 1500);
    }
    
    // Add CSS for star twinkling if it doesn't exist
    if (!$('#star-animation-style').length) {
        $('head').append(
            '<style id="star-animation-style">' +
            '@keyframes onlyTwinkle {' +
            '  0% { opacity: 0.7; text-shadow: 0 0 5px rgba(255, 255, 0, 0.5); }' +
            '  50% { opacity: 1; text-shadow: 0 0 15px rgba(255, 255, 0, 0.9), 0 0 20px rgba(255, 255, 0, 0.5); }' +
            '  100% { opacity: 0.7; text-shadow: 0 0 5px rgba(255, 255, 0, 0.5); }' +
            '}' +
            '</style>'
        );
    }
});