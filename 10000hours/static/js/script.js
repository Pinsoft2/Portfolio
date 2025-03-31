// script.js for 10000 Hours app with user management
let activeTimerId = null;

$(document).ready(function() {
    // Set today's date as default for manual entry
    if (document.getElementById('manual-date')) {
        document.getElementById('manual-date').valueAsDate = new Date();
    }

    // Check if there's an active timer for the current user
    function checkActiveTimer() {
        $.get('/check_active_timer', function(response) {
            if (response.active_timer) {
                activeTimerId = response.entry_id;
                $('#toggleTimer').text('Stop Timer').addClass('btn-danger').removeClass('btn-primary');
                $('#timerForm').addClass('timer-active');
                
                // Set form values and disable inputs
                if (response.category_id) {
                    $('#timer-category').val(response.category_id);
                    $('#timer-category').prop('disabled', true);
                }
                
                if (response.description) {
                    $('#timer-description').val(response.description);
                    $('#timer-description').prop('disabled', true);
                }
            }
        });
    }
    
    // Call on page load if timer form exists
    if ($('#timerForm').length > 0) {
        checkActiveTimer();
    }

    // Timer toggle handler
    $('#toggleTimer').click(function() {
        if (!activeTimerId) {
            // Start timer
            const categoryId = $('#timer-category').val();
            const description = $('#timer-description').val();
            
            if (!categoryId) {
                alert('Please select a category');
                return;
            }

            $.post('/start_timer', {
                category_id: categoryId,
                description: description
            }, function(response) {
                activeTimerId = response.entry_id;
                $('#toggleTimer').text('Stop Timer').addClass('btn-danger').removeClass('btn-primary');
                $('#timerForm').addClass('timer-active');
                $('#timer-category').prop('disabled', true);
                $('#timer-description').prop('disabled', true);
            });
        } else {
            // Stop timer
            $.post(`/stop_timer/${activeTimerId}`, function() {
                location.reload();
            });
        }
    });
    
    // Password confirmation validation for registration form
    $('#confirm_password').on('input', function() {
        const password = $('#password').val();
        const confirmPassword = $(this).val();
        
        if (password !== confirmPassword) {
            $(this).addClass('is-invalid');
        } else {
            $(this).removeClass('is-invalid');
        }
    });
    
    // Same for profile page password change
    if ($('#new_password').length > 0) {
        $('#confirm_password').on('input', function() {
            const newPassword = $('#new_password').val();
            const confirmPassword = $(this).val();
            
            if (newPassword !== confirmPassword) {
                $(this).addClass('is-invalid');
            } else {
                $(this).removeClass('is-invalid');
            }
        });
    }
});