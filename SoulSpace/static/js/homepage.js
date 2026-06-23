document.addEventListener('DOMContentLoaded', function() {
    const emojis = document.querySelectorAll('.emoji');
    const moodChartCanvas = document.getElementById('moodChart');
    const backgroundMusic = document.getElementById('background-music');

    // Maps moods to a numerical scale for the graph
    const moodMap = {
        'sad': 1,
        'tired': 2,
        'neutral': 3,
        'stressed': 4,
        'happy': 5
    };

    // Load or initialize mood data with comprehensive error handling
    let storedData = [];
    try {
        const storedDataString = localStorage.getItem('moods');
        if (storedDataString) {
            const parsed = JSON.parse(storedDataString);
            // Validate that parsed data is an array
            if (Array.isArray(parsed)) {
                storedData = parsed;
            } else {
                console.warn('Stored mood data is not an array, resetting...');
                localStorage.removeItem('moods');
                localStorage.removeItem('lastSelectionDate');
            }
        }
    } catch (error) {
        console.warn('Error loading mood data from localStorage:', error);
        // Clear corrupted data
        localStorage.removeItem('moods');
        localStorage.removeItem('lastSelectionDate');
    }

    // Validate and sanitize mood data with strict checks
    const validStoredData = storedData.filter(function(item) {
        return item &&
            typeof item === 'object' &&
            typeof item.label === 'string' &&
            item.label.trim() !== '' &&
            typeof item.mood === 'number' &&
            !isNaN(item.mood) &&
            isFinite(item.mood) &&
            item.mood >= 1 && item.mood <= 5;
    });

    // Ensure we have at least some data to work with
    let chartData = {
        labels: validStoredData.length > 0 ? validStoredData.map(item => item.label) : ['Start Tracking'],
        data: validStoredData.length > 0 ? validStoredData.map(item => item.mood) : [3]
    };

    // Additional validation to ensure chart data is never empty
    if (chartData.labels.length === 0 || chartData.data.length === 0) {
        chartData = {
            labels: ['Start Tracking'],
            data: [3]
        };
    }

    // Ensure labels and data arrays have the same length
    if (chartData.labels.length !== chartData.data.length) {
        console.warn('Labels and data arrays have different lengths, fixing...');
        const minLength = Math.min(chartData.labels.length, chartData.data.length);
        chartData.labels = chartData.labels.slice(0, minLength);
        chartData.data = chartData.data.slice(0, minLength);
    }

    // Check if a mood was already selected today
    const checkDailySelection = () => {
        const today = new Date().toISOString().slice(0, 10);
        return localStorage.getItem('lastSelectionDate') === today;
    };

    // Function to update local storage with new data
    const updateLocalStorage = () => {
        localStorage.setItem('lastSelectionDate', new Date().toISOString().slice(0, 10));
        localStorage.setItem('moods', JSON.stringify(chartData.labels.map((label, index) => ({
            label: label,
            mood: chartData.data[index]
        }))));
    };

    // Initialize the Chart.js graph with error handling
    let moodChart;
    try {
        // Validate chart data before initialization
        if (!chartData.labels || !chartData.data ||
            chartData.labels.length === 0 || chartData.data.length === 0 ||
            chartData.labels.length !== chartData.data.length) {
            throw new Error('Invalid chart data: labels and data arrays must be non-empty and have the same length');
        }

        const ctx = moodChartCanvas.getContext('2d');
        moodChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: 'Mood Tracker',
                    data: chartData.data,
                    borderColor: '#17bf6d',
                    borderWidth: 3,
                    tension: 0.4,
                    fill: false,
                    pointBackgroundColor: '#17bf6d',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.2)'
                        },
                        ticks: {
                            color: 'rgba(255, 255, 255, 0.8)',
                            autoSkip: false
                        }
                    },
                    y: {
                        display: true,
                        min: 1,
                        max: 5,
                        ticks: {
                            color: 'rgba(255, 255, 255, 0.8)',
                            stepSize: 1,
                            callback: function(value, index, values) {
                                const moodName = Object.keys(moodMap).find(key => moodMap[key] === value);
                                return moodName ? moodName.charAt(0).toUpperCase() + moodName.slice(1) : '';
                            }
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.2)'
                        }
                    }
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            title: tooltipItem => tooltipItem[0].label,
                            label: tooltipItem => {
                                const mood = tooltipItem.raw;
                                const moodName = Object.keys(moodMap).find(key => moodMap[key] === mood);
                                return `Mood: ${moodName ? moodName.charAt(0).toUpperCase() + moodName.slice(1) : 'Unknown'}`;
                            }
                        }
                    }
                }
            }
        });
        console.log('Mood chart initialized successfully');
    } catch (error) {
        console.error('Error initializing mood chart:', error);
        // Create a fallback display
        moodChartCanvas.style.display = 'none';
        const errorMsg = document.createElement('div');
        errorMsg.style.color = 'red';
        errorMsg.style.textAlign = 'center';
        errorMsg.style.padding = '20px';
        errorMsg.textContent = 'Unable to load mood chart. Please refresh the page.';
        moodChartCanvas.parentNode.appendChild(errorMsg);
    }

    // Event listener for emoji clicks
    emojis.forEach(emoji => {
        emoji.addEventListener('click', () => {
            if (checkDailySelection()) {
                alert("You have already selected your mood for today. Come back tomorrow!");
                return;
            }

            emojis.forEach(e => e.classList.remove('selected'));
            emoji.classList.add('selected');

            const moodValue = moodMap[emoji.dataset.mood];
            const newLabel = new Date().toLocaleDateString('en-US', { weekday: 'short' });

            chartData.labels.push(newLabel);
            chartData.data.push(moodValue);

            // Safely update the chart
            try {
                moodChart.update();
                updateLocalStorage();
                console.log('Mood chart updated successfully');
            } catch (error) {
                console.error('Error updating mood chart:', error);
                // Try to reinitialize the chart if update fails
                try {
                    moodChart.destroy();
                    const ctx = moodChartCanvas.getContext('2d');
                    moodChart = new Chart(ctx, {
                        type: 'line',
                        data: {
                            labels: chartData.labels,
                            datasets: [{
                                label: 'Mood Tracker',
                                data: chartData.data,
                                borderColor: '#17bf6d',
                                borderWidth: 3,
                                tension: 0.4,
                                fill: false,
                                pointBackgroundColor: '#17bf6d',
                                pointBorderColor: '#fff',
                                pointBorderWidth: 2,
                                pointRadius: 6,
                                pointHoverRadius: 8
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            scales: {
                                x: {
                                    grid: { color: 'rgba(255, 255, 255, 0.2)' },
                                    ticks: { color: 'rgba(255, 255, 255, 0.8)', autoSkip: false }
                                },
                                y: {
                                    display: true,
                                    min: 1,
                                    max: 5,
                                    ticks: {
                                        color: 'rgba(255, 255, 255, 0.8)',
                                        stepSize: 1,
                                        callback: function(value) {
                                            const moodName = Object.keys(moodMap).find(key => moodMap[key] === value);
                                            return moodName ? moodName.charAt(0).toUpperCase() + moodName.slice(1) : '';
                                        }
                                    },
                                    grid: { color: 'rgba(255, 255, 255, 0.2)' }
                                }
                            },
                            plugins: {
                                legend: { display: false },
                                tooltip: {
                                    callbacks: {
                                        title: tooltipItem => tooltipItem[0].label,
                                        label: tooltipItem => {
                                            const mood = tooltipItem.raw;
                                            const moodName = Object.keys(moodMap).find(key => moodMap[key] === mood);
                                            return `Mood: ${moodName ? moodName.charAt(0).toUpperCase() + moodName.slice(1) : 'Unknown'}`;
                                        }
                                    }
                                }
                            }
                        }
                    });
                } catch (reinitError) {
                    console.error('Error reinitializing mood chart:', reinitError);
                }
            }
        });
    });

    // Play background music on first user interaction to comply with browser autoplay policies
    const playBackgroundMusic = () => {
        if (backgroundMusic.paused) {
            backgroundMusic.play().catch(error => {
                console.warn('Background music playback was prevented:', error);
            });
        }
        // Remove the event listeners after first play attempt
        window.removeEventListener('click', playBackgroundMusic);
        window.removeEventListener('keydown', playBackgroundMusic);
    };

    window.addEventListener('click', playBackgroundMusic);
    window.addEventListener('keydown', playBackgroundMusic);

    // Check on page load if a mood has already been selected today
    if (checkDailySelection()) {
        const lastMood = storedData[storedData.length - 1];
        if (lastMood) {
            const emojiToSelect = document.querySelector(`.emoji[data-mood="${Object.keys(moodMap).find(key => moodMap[key] === lastMood.mood)}"]`);
            if (emojiToSelect) {
                emojiToSelect.classList.add('selected');
            }
        }
    }
});