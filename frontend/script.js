// CoastalGuard AI Frontend JavaScript
class CoastalGuardApp {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8000';
        this.tideApiUrl = 'http://localhost:5000';
        this.currentTab = 'dashboard';
        this.stats = {
            totalScans: 0,
            activeAlerts: 0,
            detectionAccuracy: 98.5,
            responseTime: 2.3
        };
        this.activities = [];
        this.alerts = [];
        this.uploadedFiles = [];
        this.init();
    }

    async init() {
        this.setupEventListeners();
        await this.loadDashboardData();
        this.startRealTimeUpdates();
        this.showToast('CoastalGuard AI System initialized successfully', 'success');
    }

    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                this.switchTab(e.target.closest('.nav-link').dataset.tab);
            });
        });

        // Media upload
        const uploadArea = document.getElementById('upload-area');
        const mediaInput = document.getElementById('media-input');

        uploadArea.addEventListener('click', () => mediaInput.click());
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            this.handleMediaUpload(files);
        });

        mediaInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleMediaUpload(e.target.files);
            }
        });

        // Hazard cards
        document.querySelectorAll('.hazard-card').forEach(card => {
            card.addEventListener('click', () => {
                this.switchTab('reporting');
                document.getElementById('hazard-type').value = card.dataset.hazard;
            });
        });

        // Form submission
        const reportForm = document.getElementById('hazard-report-form');
        if (reportForm) {
            reportForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.submitHazardReport();
            });
        }
    }

    switchTab(tabName) {
        // Update navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // Update content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(tabName).classList.add('active');

        this.currentTab = tabName;

        // Load tab-specific data
        switch (tabName) {
            case 'dashboard':
                this.loadDashboardData();
                break;
            case 'alerts':
                this.loadAlertsData();
                break;
            case 'tides':
                this.loadTidesData();
                break;
        }
    }

    async loadDashboardData() {
        try {
            // Load system health
            const healthResponse = await fetch(`${this.apiBaseUrl}/health`);
            const healthData = await healthResponse.json();
            
            if (healthData.status === 'healthy') {
                this.updateStats();
                this.loadRecentActivities();
                this.checkEmergencyAlerts();
            } else {
                this.showToast('System experiencing issues', 'warning');
            }
        } catch (error) {
            console.error('Error loading dashboard data:', error);
            this.showToast('Unable to load dashboard data', 'error');
        }
    }

    updateStats() {
        document.getElementById('total-scans').textContent = this.stats.totalScans;
        document.getElementById('active-alerts').textContent = this.stats.activeAlerts;
        document.getElementById('detection-accuracy').textContent = this.stats.detectionAccuracy + '%';
        document.getElementById('response-time').textContent = this.stats.responseTime + 's';
    }

    loadRecentActivities() {
        const activityList = document.getElementById('activity-list');
        if (!activityList) return;

        // Simulate recent activities
        const recentActivities = [
            {
                icon: 'fas fa-flag',
                title: 'Oil Spill Report',
                description: 'Citizen reported potential oil spill near Golden Gate Bridge',
                time: '2 minutes ago'
            },
            {
                icon: 'fas fa-leaf',
                title: 'Algal Bloom Detection',
                description: 'AI detected harmful algal bloom in Monterey Bay',
                time: '15 minutes ago'
            },
            {
                icon: 'fas fa-mountain',
                title: 'Erosion Alert',
                description: 'Coastal erosion detected at Point Reyes',
                time: '1 hour ago'
            }
        ];

        activityList.innerHTML = recentActivities.map(activity => `
            <div class="activity-item">
                <div class="activity-icon">
                    <i class="${activity.icon}"></i>
                </div>
                <div class="activity-content">
                    <h4>${activity.title}</h4>
                    <p>${activity.description}</p>
                </div>
                <div class="activity-time">${activity.time}</div>
            </div>
        `).join('');
    }

    checkEmergencyAlerts() {
        // Check for high-priority alerts
        const emergencyBanner = document.getElementById('emergency-banner');
        if (this.stats.activeAlerts > 2) {
            emergencyBanner.style.display = 'block';
            document.getElementById('emergency-message').textContent = 
                `${this.stats.activeAlerts} active alerts require immediate attention`;
        } else {
            emergencyBanner.style.display = 'none';
        }
    }

    // Quick Report Functions
    quickReport(hazardType) {
        this.switchTab('reporting');
        document.getElementById('hazard-type').value = hazardType;
        
        // Pre-fill severity based on hazard type
        const severitySelect = document.getElementById('hazard-severity');
        if (hazardType === 'oil_spill') {
            severitySelect.value = 'high';
        } else if (hazardType === 'algal_bloom') {
            severitySelect.value = 'medium';
        } else {
            severitySelect.value = 'low';
        }
        
        this.showToast(`Quick report started for ${hazardType.replace('_', ' ')}`, 'info');
    }

    // Location Services
    async getCurrentLocation() {
        if (!navigator.geolocation) {
            this.showToast('Geolocation not supported by your browser', 'error');
            return;
        }

        this.showLoading(true);
        
        try {
            const position = await new Promise((resolve, reject) => {
                navigator.geolocation.getCurrentPosition(resolve, reject, {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 60000
                });
            });

            const { latitude, longitude } = position.coords;
            document.getElementById('latitude').value = latitude.toFixed(6);
            document.getElementById('longitude').value = longitude.toFixed(6);
            
            this.showToast('Location captured successfully', 'success');
        } catch (error) {
            console.error('Error getting location:', error);
            this.showToast('Unable to get your location', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    // Media Upload Functions
    handleMediaUpload(files) {
        const mediaPreview = document.getElementById('media-preview');
        const previewGrid = document.getElementById('preview-grid');
        
        Array.from(files).forEach(file => {
            if (file.type.startsWith('image/') || file.type.startsWith('video/')) {
                this.uploadedFiles.push(file);
                this.createMediaPreview(file, previewGrid);
            }
        });

        if (this.uploadedFiles.length > 0) {
            mediaPreview.style.display = 'block';
            this.showToast(`${this.uploadedFiles.length} file(s) uploaded`, 'success');
        }
    }

    createMediaPreview(file, previewGrid) {
        const previewItem = document.createElement('div');
        previewItem.className = 'preview-item';
        
        const reader = new FileReader();
        reader.onload = (e) => {
            if (file.type.startsWith('image/')) {
                previewItem.innerHTML = `
                    <img src="${e.target.result}" alt="Preview">
                    <button class="remove-btn" onclick="this.parentElement.remove()">
                        <i class="fas fa-times"></i>
                    </button>
                `;
            } else if (file.type.startsWith('video/')) {
                previewItem.innerHTML = `
                    <video src="${e.target.result}" controls></video>
                    <button class="remove-btn" onclick="this.parentElement.remove()">
                        <i class="fas fa-times"></i>
                    </button>
                `;
            }
        };
        reader.readAsDataURL(file);
        
        previewGrid.appendChild(previewItem);
    }

    // Form Management
    clearForm() {
        const form = document.getElementById('hazard-report-form');
        if (form) {
            form.reset();
            this.uploadedFiles = [];
            document.getElementById('media-preview').style.display = 'none';
            document.getElementById('preview-grid').innerHTML = '';
            this.showToast('Form cleared', 'info');
        }
    }

    async submitHazardReport() {
        const form = document.getElementById('hazard-report-form');
        if (!form.checkValidity()) {
            form.reportValidity();
            this.showToast('Please fill in all required fields', 'error');
            return;
        }

        this.showLoading(true);

        try {
            const formData = new FormData();
            
            // Add form fields
            formData.append('hazard_type', document.getElementById('hazard-type').value);
            formData.append('severity', document.getElementById('hazard-severity').value);
            formData.append('description', document.getElementById('hazard-description').value);
            formData.append('latitude', document.getElementById('latitude').value);
            formData.append('longitude', document.getElementById('longitude').value);
            formData.append('location_description', document.getElementById('location-description').value);
            formData.append('water_temp', document.getElementById('water-temp').value);
            formData.append('salinity', document.getElementById('salinity').value);
            formData.append('wind_speed', document.getElementById('wind-speed').value);
            formData.append('weather_conditions', document.getElementById('weather-conditions').value);
            formData.append('reporter_name', document.getElementById('reporter-name').value);
            formData.append('reporter_email', document.getElementById('reporter-email').value);
            formData.append('reporter_phone', document.getElementById('reporter-phone').value);
            formData.append('contact_preference', document.getElementById('contact-preference').value);

            // Add media files
            this.uploadedFiles.forEach((file, index) => {
                formData.append(`media_${index}`, file);
            });

            // Submit to API
            const response = await fetch(`${this.apiBaseUrl}/upload`, {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            
            if (result.success) {
                this.displayReportStatus(result);
                this.stats.totalScans++;
                this.updateStats();
                this.addActivity({
                    icon: 'fas fa-flag',
                    title: `${result.hazard_details.type.replace('_', ' ')} Report`,
                    description: `Alert level: ${result.hazard_details.alert_level}`,
                    time: 'Just now'
                });
                this.showToast('Hazard report submitted successfully', 'success');
            } else {
                throw new Error(result.error || 'Submission failed');
            }
            
        } catch (error) {
            console.error('Error submitting report:', error);
            this.showToast('Error submitting report: ' + error.message, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    displayReportStatus(result) {
        const reportStatus = document.getElementById('report-status');
        const statusContent = document.getElementById('status-content');
        
        const alertLevels = {
            'GREEN': { class: 'success', icon: 'fas fa-check-circle' },
            'YELLOW': { class: 'warning', icon: 'fas fa-exclamation-triangle' },
            'ORANGE': { class: 'warning', icon: 'fas fa-exclamation-triangle' },
            'RED': { class: 'error', icon: 'fas fa-times-circle' }
        };

        const level = alertLevels[result.hazard_details.alert_level] || alertLevels['GREEN'];

        statusContent.innerHTML = `
            <div class="result-card ${level.class}">
                <i class="${level.icon}"></i>
                <h4>Report Submitted Successfully</h4>
                <p><strong>Hazard Type:</strong> ${result.hazard_details.type.replace('_', ' ')}</p>
                <p><strong>Alert Level:</strong> ${result.hazard_details.alert_level}</p>
                <p><strong>Location:</strong> ${result.hazard_details.location}</p>
                <p><strong>Confidence:</strong> ${(result.hazard_details.confidence * 100).toFixed(1)}%</p>
                <p><strong>Report ID:</strong> ${result.alert.id}</p>
                <p><strong>Timestamp:</strong> ${new Date(result.alert.timestamp).toLocaleString()}</p>
            </div>
        `;

        reportStatus.style.display = 'block';
        reportStatus.scrollIntoView({ behavior: 'smooth' });
    }

    async loadAlertsData() {
        try {
            // Simulate loading alerts
            this.alerts = [
                {
                    id: 1,
                    level: 'red',
                    type: 'Oil Spill',
                    location: 'San Francisco Bay',
                    description: 'Large oil slick detected near Golden Gate Bridge. Emergency response team dispatched.',
                    time: '2 hours ago',
                    status: 'active'
                },
                {
                    id: 2,
                    level: 'orange',
                    type: 'Algal Bloom',
                    location: 'Monterey Bay',
                    description: 'Harmful algal bloom spreading rapidly. Water quality monitoring increased.',
                    time: '4 hours ago',
                    status: 'active'
                },
                {
                    id: 3,
                    level: 'yellow',
                    type: 'Coastal Erosion',
                    location: 'Point Reyes',
                    description: 'Moderate coastal erosion observed. Monitoring continues.',
                    time: '6 hours ago',
                    status: 'active'
                }
            ];

            this.displayAlerts();
        } catch (error) {
            console.error('Error loading alerts:', error);
            this.showToast('Error loading alerts', 'error');
        }
    }

    displayAlerts() {
        const alertsList = document.getElementById('alerts-list');
        if (!alertsList) return;

        alertsList.innerHTML = this.alerts.map(alert => `
            <div class="alert-item ${alert.level}">
                <div class="alert-header">
                    <span class="alert-type">${alert.type}</span>
                    <span class="alert-time">${alert.time}</span>
                </div>
                <div class="alert-location">${alert.location}</div>
                <div class="alert-description">${alert.description}</div>
            </div>
        `).join('');

        this.stats.activeAlerts = this.alerts.length;
        this.updateStats();
    }

    async loadTidesData() {
        try {
            // Simulate tide data
            const tideData = {
                current_level: 1.2,
                phase: 'Rising',
                location: 'San Francisco Bay',
                forecast: [
                    { time: '00:00', level: 0.8 },
                    { time: '06:00', level: 1.8 },
                    { time: '12:00', level: 0.5 },
                    { time: '18:00', level: 1.5 }
                ]
            };

            this.displayTideData(tideData);
        } catch (error) {
            console.error('Error loading tide data:', error);
            this.showToast('Error loading tide data', 'error');
        }
    }

    displayTideData(data) {
        document.getElementById('current-level').textContent = data.current_level.toFixed(1);
        document.getElementById('tide-phase').textContent = data.phase;
        document.getElementById('tide-location').textContent = data.location;
    }

    addActivity(activity) {
        this.activities.unshift(activity);
        if (this.activities.length > 10) {
            this.activities.pop();
        }
        
        if (this.currentTab === 'dashboard') {
            this.loadRecentActivities();
        }
    }

    startRealTimeUpdates() {
        // Simulate real-time updates
        setInterval(() => {
            this.stats.responseTime = (Math.random() * 2 + 1).toFixed(1);
            this.updateStats();
        }, 30000);
    }

    showLoading(show) {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.style.display = show ? 'flex' : 'none';
        }
    }

    showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-times-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };

        toast.innerHTML = `
            <i class="${icons[type]}"></i>
            <div class="toast-content">
                <div class="toast-title">${type.charAt(0).toUpperCase() + type.slice(1)}</div>
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;

        container.appendChild(toast);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, 5000);
    }
}

// Global functions for HTML onclick handlers
function quickReport(hazardType) {
    if (window.coastalGuardApp) {
        window.coastalGuardApp.quickReport(hazardType);
    }
}

function getCurrentLocation() {
    if (window.coastalGuardApp) {
        window.coastalGuardApp.getCurrentLocation();
    }
}

function clearForm() {
    if (window.coastalGuardApp) {
        window.coastalGuardApp.clearForm();
    }
}

function viewEmergencyDetails() {
    if (window.coastalGuardApp) {
        window.coastalGuardApp.switchTab('alerts');
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.coastalGuardApp = new CoastalGuardApp();
});
