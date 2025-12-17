const ctx = document.getElementById('accuracyChart');
new Chart(ctx, {
    type: 'bar',
    data: {
        labels: ['Rule-Based', 'LogReg', 'SVM', 'Random Forest'],
        datasets: [{
            label: 'Accuracy (%)',
            data: [78, 90, 93, 96],
        }]
    }
});
