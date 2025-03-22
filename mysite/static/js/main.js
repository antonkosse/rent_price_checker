// Main JavaScript for Rental Tracker

document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // URL validation for add listing form
    const listingForm = document.getElementById('add-listing-form');
    if (listingForm) {
        listingForm.addEventListener('submit', function(event) {
            const urlInput = document.getElementById('listing-url');
            const url = urlInput.value.trim();

            // Simple validation for supported sites
            const supportedSites = ['rieltor.ua', 'dom.ria.com'];
            let isValid = false;

            for (const site of supportedSites) {
                if (url.includes(site)) {
                    isValid = true;
                    break;
                }
            }

            if (!isValid) {
                event.preventDefault();
                alert('Please enter a valid URL from rieltor.ua or dom.ria.com');
                urlInput.focus();
            }
        });
    }

    // Toggle notification settings
    const notificationToggles = document.querySelectorAll('.notification-toggle');
    if (notificationToggles.length > 0) {
        notificationToggles.forEach(function(toggle) {
            toggle.addEventListener('change', function() {
                const listingId = this.dataset.listingId;
                const notificationType = this.dataset.notificationType;
                const isEnabled = this.checked;

                // Send AJAX request to update notification preferences
                fetch(`/update_notification_settings/${listingId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: JSON.stringify({
                        notification_type: notificationType,
                        enabled: isEnabled
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Show success message
                        const toastEl = document.getElementById('notification-toast');
                        const toast = new bootstrap.Toast(toastEl);
                        document.getElementById('toast-message').textContent =
                            `Notifications ${isEnabled ? 'enabled' : 'disabled'} for ${notificationType}`;
                        toast.show();
                    }
                })
                .catch(error => console.error('Error updating notification settings:', error));
            });
        });
    }

    // Price history chart (if Chart.js is included)
    const priceHistoryChart = document.getElementById('price-history-chart');
    if (priceHistoryChart && typeof Chart !== 'undefined') {
        // Get the data from the data attributes
        const dates = JSON.parse(priceHistoryChart.dataset.dates);
        const prices = JSON.parse(priceHistoryChart.dataset.prices);

        new Chart(priceHistoryChart, {
            type: 'line',
            data: {
                labels: dates,
                datasets: [{
                    label: 'Price History',
                    data: prices,
                    borderColor: '#007bff',
                    backgroundColor: 'rgba(0, 123, 255, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Price: ${context.raw} UAH`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        ticks: {
                            callback: function(value) {
                                return value + ' UAH';
                            }
                        }
                    }
                }
            }
        });
    }
});

// Copy verification link to clipboard
function copyToClipboard(elementId) {
    const el = document.getElementById(elementId);
    const text = el.textContent || el.innerText;

    navigator.clipboard.writeText(text).then(function() {
        // Show success message
        const copyBtn = document.getElementById('copy-btn');
        copyBtn.innerHTML = '<i class="fas fa-check"></i> Copied!';
        copyBtn.classList.remove('btn-primary');
        copyBtn.classList.add('btn-success');

        // Reset button after 2 seconds
        setTimeout(function() {
            copyBtn.innerHTML = '<i class="fas fa-copy"></i> Copy Link';
            copyBtn.classList.remove('btn-success');
            copyBtn.classList.add('btn-primary');
        }, 2000);
    }).catch(function(err) {
        console.error('Failed to copy text: ', err);
    });
}