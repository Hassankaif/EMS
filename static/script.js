document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded and parsed');

    const forecastForm = document.getElementById('forecast-form');
    const forecastResult = document.getElementById('forecast-result');
    const visualizeBtn = document.getElementById('visualize-btn');
    const visualizationResults = document.getElementById('visualization-results');

    let forecastChart;
    let floorWiseChart;

    forecastForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        
        fetch('/forecast', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            
            const img = new Image();
            img.src = data.plot_url;
            img.alt = 'Forecast Plot';
            
            forecastResult.innerHTML = '';
            forecastResult.appendChild(img);
            forecastResult.classList.remove('hidden');
        })
        .catch(error => {
            console.error('Error:', error);
            forecastResult.textContent = `An error occurred while fetching the forecast: ${error.message}. Please try again.`;
            forecastResult.classList.remove('hidden');
        });
    });

    function createForecastChart(data) {
        const ctx = document.getElementById('forecast-chart').getContext('2d');
        
        if (forecastChart) {
            forecastChart.destroy();
        }

        forecastChart = new Chart(ctx, {
            type: 'line',
            data: {
                datasets: [{
                    label: 'Actual',
                    data: Object.entries(data.actual_data).map(([date, value]) => ({x: date, y: value})),
                    borderColor: 'blue',
                    fill: false
                }, {
                    label: 'Predicted',
                    data: Object.entries(data.predicted_data).map(([date, value]) => ({x: date, y: value})),
                    borderColor: 'red',
                    fill: false
                }]
            },
            options: {
                responsive: true,
                title: {
                    display: true,
                    text: 'Energy Consumption Forecast'
                },
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'day'
                        },
                        title: {
                            display: true,
                            text: 'Date'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Energy Consumption (kWh)'
                        }
                    }
                }
            }
        });
    }

    visualizeBtn.addEventListener('click', function() {
        console.log('Visualize button clicked');
        fetch('/visualize')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            console.log('Data received:', data);
            visualizationResults.classList.remove('hidden');
            createFloorWiseChart(data);
        })
        .catch(error => {
            console.error('Error:', error);
            visualizationResults.textContent = `An error occurred while visualizing the data: ${error.message}. Please try again.`;
            visualizationResults.classList.remove('hidden');
        });
    });

    function createFloorWiseChart(data) {
        console.log('Creating floor-wise chart');
        const canvas = document.getElementById('floor-wise-chart');
        if (!canvas) {
            console.error('Floor-wise chart canvas not found');
            visualizationResults.textContent = 'Error: Floor-wise chart canvas not found';
            return;
        }

        const ctx = canvas.getContext('2d');
        if (!ctx) {
            console.error('Could not get 2D context from canvas');
            visualizationResults.textContent = 'Error: Could not create chart context';
            return;
        }
        
        if (floorWiseChart) {
            floorWiseChart.destroy();
        }

        try {
            floorWiseChart = new Chart(ctx, {
                type: 'line',
                data: {
                    datasets: Object.entries(data).map(([floor, values]) => ({
                        label: `Floor ${floor}`,
                        data: values.map(([date, consumption]) => ({ x: date, y: consumption })),
                        borderColor: getRandomColor(),
                        fill: false,
                        tension: 0.1
                    }))
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Floor-wise Energy Consumption'
                        }
                    },
                    scales: {
                        x: {
                            type: 'time',
                            time: {
                                unit: 'day'
                            },
                            title: {
                                display: true,
                                text: 'Date'
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: 'Energy Consumption (kWh)'
                            }
                        }
                    }
                }
            });
            console.log('Floor-wise chart created successfully');
        } catch (error) {
            console.error('Error creating chart:', error);
            visualizationResults.textContent = `Error creating chart: ${error.message}`;
        }
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
                plugins: {
                    title: {
                        display: true,
                        text: 'Appliance-wise Energy Consumption'
                    }
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
                plugins: {
                    title: {
                        display: true,
                        text: 'Floor and Appliance-wise Energy Consumption'
                    }
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
                plugins: {
                    title: {
                        display: true,
                        text: 'Average Hourly Energy Consumption'
                    }
                }
            }
        });
    }

    function getRandomColor() {
        return '#' + Math.floor(Math.random()*16777215).toString(16);
    }

    console.log('Script loaded successfully');
});
