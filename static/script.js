document.addEventListener('DOMContentLoaded', function() {
    const forecastForm = document.getElementById('forecast-form');
    const forecastResult = document.getElementById('forecast-result');
    const forecastPlot = document.getElementById('forecast-plot');
    const visualizeBtn = document.getElementById('visualize-btn');
    const visualizationResults = document.getElementById('visualization-results');

    forecastForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(forecastForm);
        
        fetch('/forecast', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            forecastPlot.src = 'data:image/png;base64,' + data.plot_url;
            forecastResult.classList.remove('hidden');
        })
        .catch(error => console.error('Error:', error));
    });

    visualizeBtn.addEventListener('click', function() {
        fetch('/visualize')
        .then(response => response.json())
        .then(data => {
            createFloorWiseChart(data.floor_wise_consumption);
            createApplianceWiseChart(data.appliance_wise_consumption);
            createFloorApplianceChart(data.floor_appliance_consumption);
            createHourlyConsumptionChart(data.hourly_consumption);
            visualizationResults.classList.remove('hidden');
        })
        .catch(error => console.error('Error:', error));
    });

    function createFloorWiseChart(data) {
        const ctx = document.getElementById('floor-wise-chart').getContext('2d');
        new Chart(ctx, {
            
            type: 'line',
            data: {
                labels: Object.keys(data),
                datasets: Object.entries(data).map(([floor, values]) => ({
                    label: floor,
                    data: Object.values(values),
                    borderColor: getRandomColor(),
                    fill: false
                }))
            },
            options: {
                responsive: true,
                title: {
                    display: true,
                    text: 'Floor-wise Energy Consumption'
                }
            }
        });
    }

    function createApplianceWiseChart(data) {
        const ctx = document.getElementById('appliance-wise-chart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: Object.keys(data),
                datasets: [{
                    label: 'Energy Consumption',
                    data: Object.values(data),
                    backgroundColor: getRandomColor()
                }]
            },
            options: {
                responsive: true,
                title: {
                    display: true,
                    text: 'Appliance-wise Energy Consumption'
                }
            }
        });
    }

    function createFloorApplianceChart(data) {
        const ctx = document.getElementById('floor-appliance-chart').getContext('2d');
        const floors = Object.keys(data);
        const appliances = Object.keys(data[floors[0]]);
        
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: floors,
                datasets: appliances.map(appliance => ({
                    label: appliance,
                    data: floors.map(floor => data[floor][appliance]),
                    backgroundColor: getRandomColor()
                }))
            },
            options: {
                responsive: true,
                title: {
                    display: true,
                    text: 'Floor and Appliance-wise Energy Consumption'
                },
                scales: {
                    x: {
                        stacked: true,
                    },
                    y: {
                        stacked: true
                    }
                }
            }
        });
    }

    function createHourlyConsumptionChart(data) {
        const ctx = document.getElementById('hourly-consumption-chart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: Object.keys(data),
                datasets: [{
                    label: 'Average Energy Consumption',
                    data: Object.values(data),
                    borderColor: getRandomColor(),
                    fill: false
                }]
            },
            options: {
                responsive: true,
                title: {
                    display: true,
                    text: 'Average Hourly Energy Consumption'
                }
            }
        });
    }

    function getRandomColor() {
        return '#' + Math.floor(Math.random()*16777215).toString(16);
    }
});