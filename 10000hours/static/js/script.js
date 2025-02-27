let activeTimerId = null;

$(document).ready(function() {
    $('#toggleTimer').click(function() {
        if (!activeTimerId) {
            // Start timer
            const categoryId = $('#timer-category').val();
            const description = $('#timer-description').val();

            $.post('/start_timer', {
                category_id: categoryId,
                description: description
            }, function(response) {
                activeTimerId = response.entry_id;
                $('#toggleTimer').text('Stop Timer').addClass('btn-danger').removeClass('btn-primary');
                $('#timerForm').addClass('timer-active');
            });
        } else {
            // Stop timer
            $.post(`/stop_timer/${activeTimerId}`, function() {
                location.reload();
            });
        }
    });

    // Set today's date as default for manual entry
    document.getElementById('manual-date').valueAsDate = new Date();
});