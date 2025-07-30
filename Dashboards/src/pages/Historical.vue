<template>
  <div class="historical-page">
    <!-- Header Section -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">Historical Data & Forecast Analysis</h1>
        <p class="page-subtitle">
          Comprehensive analysis of compost monitoring data with predictive insights
        </p>
        <div class="header-stats">
          <div class="stat-badge">
            <span class="stat-label">Data Period</span>
            <span class="stat-value">10 Months</span>
          </div>
          <div class="stat-badge">
            <span class="stat-label">Forecast Period</span>
            <span class="stat-value">3 Months</span>
          </div>
          <div class="stat-badge">
            <span class="stat-label">Weather Integration</span>
            <span class="stat-value">✓ Active</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Navigation Tabs -->
    <div class="nav-tabs">
      <button 
        v-for="tab in tabs" 
        :key="tab.id"
        :class="['tab-button', { active: activeTab === tab.id }]"
        @click="activeTab = tab.id"
      >
        <span class="tab-icon">{{ tab.icon }}</span>
        {{ tab.label }}
      </button>
    </div>

    <!-- Tab Content -->
    <div class="tab-content">
      <!-- Overview Tab -->
      <div v-if="activeTab === 'overview'" class="tab-panel" key="overview">
        <div class="overview-grid">
          <div class="overview-card">
            <h3>📊 Data Summary</h3>
            <div class="card-content">
              <div class="summary-item">
                <span class="label">Total Records:</span>
                <span class="value">133,793 readings</span>
              </div>
              <div class="summary-item">
                <span class="label">Date Range:</span>
                <span class="value">Nov 2024 - Jun 2025</span>
              </div>
              <div class="summary-item">
                <span class="label">Sensors:</span>
                <span class="value">Multi-parameter monitoring</span>
              </div>
              <div class="summary-item">
                <span class="label">Update Frequency:</span>
                <span class="value">Continuous logging</span>
              </div>
            </div>
          </div>

          <div class="overview-card">
            <h3>🎯 Key Insights</h3>
            <div class="card-content">
              <div class="insight-item">
                <span class="insight-icon">📈</span>
                <div class="insight-text">
                  <strong>Moisture Trends:</strong>
                  <p>Recent decline in moisture levels requiring attention</p>
                </div>
              </div>
              <div class="insight-item">
                <span class="insight-icon">🌡️</span>
                <div class="insight-text">
                  <strong>Temperature Correlation:</strong>
                  <p>Strong relationship between air temp and moisture loss</p>
                </div>
              </div>
              <div class="insight-item">
                <span class="insight-icon">⚠️</span>
                <div class="insight-text">
                  <strong>Management Alert:</strong>
                  <p>Current moisture below optimal range (40-60%)</p>
                </div>
              </div>
            </div>
          </div>

          <div class="overview-card">
            <h3>🔮 Forecast Model</h3>
            <div class="card-content">
              <div class="model-feature">
                <span class="feature-icon">🌤️</span>
                <div class="feature-text">
                  <strong>Weather Integration</strong>
                  <p>Singapore climate data for evaporation modeling</p>
                </div>
              </div>
              <div class="model-feature">
                <span class="feature-icon">📊</span>
                <div class="feature-text">
                  <strong>Trend Analysis</strong>
                  <p>Statistical modeling of historical patterns</p>
                </div>
              </div>
              <div class="model-feature">
                <span class="feature-icon">🔄</span>
                <div class="feature-text">
                  <strong>Seasonal Patterns</strong>
                  <p>Monthly variation analysis and prediction</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Forecast Tab -->
      <div v-if="activeTab === 'forecast'" class="tab-panel" key="forecast">
        <CompostForecast />
      </div>

      <!-- Historical Tab -->
      <div v-if="activeTab === 'historical'" class="tab-panel" key="historical">
        <div class="historical-section">
          <h2>📈 Historical Data Analysis</h2>
          
          <div class="analysis-grid">
            <div class="analysis-card">
              <h3>Moisture Level Distribution</h3>
              <div class="chart-placeholder">
                <p>Historical moisture levels over time</p>
                <div class="placeholder-chart">
                  <div class="chart-bar" style="height: 60%"></div>
                  <div class="chart-bar" style="height: 80%"></div>
                  <div class="chart-bar" style="height: 45%"></div>
                  <div class="chart-bar" style="height: 70%"></div>
                  <div class="chart-bar" style="height: 55%"></div>
                  <div class="chart-bar" style="height: 90%"></div>
                  <div class="chart-bar" style="height: 30%"></div>
                  <div class="chart-bar" style="height: 40%"></div>
                </div>
              </div>
            </div>

            <div class="analysis-card">
              <h3>Temperature Correlation</h3>
              <div class="correlation-stats">
                <div class="stat-row">
                  <span class="stat-name">Air Temperature Range:</span>
                  <span class="stat-result">24°C - 35°C</span>
                </div>
                <div class="stat-row">
                  <span class="stat-name">Soil Temperature Range:</span>
                  <span class="stat-result">22°C - 38°C</span>
                </div>
                <div class="stat-row">
                  <span class="stat-name">Correlation Coefficient:</span>
                  <span class="stat-result">0.74 (Strong)</span>
                </div>
                <div class="stat-row">
                  <span class="stat-name">Optimal Range:</span>
                  <span class="stat-result">35°C - 55°C</span>
                </div>
              </div>
            </div>

            <div class="analysis-card">
              <h3>Nutrient Profile Trends</h3>
              <div class="nutrient-grid">
                <div class="nutrient-item">
                  <span class="nutrient-name">Nitrogen (N)</span>
                  <div class="nutrient-bar">
                    <div class="nutrient-fill" style="width: 20%"></div>
                  </div>
                  <span class="nutrient-value">Low</span>
                </div>
                <div class="nutrient-item">
                  <span class="nutrient-name">Phosphorus (P)</span>
                  <div class="nutrient-bar">
                    <div class="nutrient-fill" style="width: 75%"></div>
                  </div>
                  <span class="nutrient-value">High</span>
                </div>
                <div class="nutrient-item">
                  <span class="nutrient-name">Potassium (K)</span>
                  <div class="nutrient-bar">
                    <div class="nutrient-fill" style="width: 60%"></div>
                  </div>
                  <span class="nutrient-value">Good</span>
                </div>
                <div class="nutrient-item">
                  <span class="nutrient-name">pH Level</span>
                  <div class="nutrient-bar">
                    <div class="nutrient-fill" style="width: 45%"></div>
                  </div>
                  <span class="nutrient-value">5.6-5.7</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Reports Tab -->
      <div v-if="activeTab === 'reports'" class="tab-panel" key="reports">
        <div class="reports-section">
          <h2>📋 Analysis Reports</h2>
          
          <div class="reports-grid">
            <div class="report-card">
              <div class="report-header">
                <h3>Monthly Summary Report</h3>
                <span class="report-date">June 2025</span>
              </div>
              <div class="report-content">
                <div class="report-metric">
                  <span class="metric-label">Average Moisture:</span>
                  <span class="metric-value">18.2%</span>
                  <span class="metric-trend down">↓ 15%</span>
                </div>
                <div class="report-metric">
                  <span class="metric-label">Temperature Range:</span>
                  <span class="metric-value">26.2°C - 26.9°C</span>
                  <span class="metric-trend stable">→</span>
                </div>
                <div class="report-metric">
                  <span class="metric-label">Turning Frequency:</span>
                  <span class="metric-value">3 times/week</span>
                  <span class="metric-trend up">↑ 20%</span>
                </div>
              </div>
              <button class="report-button">Download Report</button>
            </div>

            <div class="report-card">
              <div class="report-header">
                <h3>Forecast Accuracy Report</h3>
                <span class="report-date">Q2 2025</span>
              </div>
              <div class="report-content">
                <div class="accuracy-metric">
                  <div class="accuracy-circle">
                    <div class="accuracy-fill" style="--percentage: 87"></div>
                    <span class="accuracy-text">87%</span>
                  </div>
                  <p class="accuracy-label">Prediction Accuracy</p>
                </div>
                <div class="improvement-note">
                  <p><strong>Model Performance:</strong> Weather integration improved accuracy by 23% compared to statistical-only predictions.</p>
                </div>
              </div>
              <button class="report-button">View Details</button>
            </div>

            <div class="report-card">
              <div class="report-header">
                <h3>Management Recommendations</h3>
                <span class="report-date">Updated Daily</span>
              </div>
              <div class="report-content">
                <div class="recommendation-list">
                  <div class="recommendation-item priority-high">
                    <span class="priority-badge">High</span>
                    <p>Increase watering frequency - moisture below optimal</p>
                  </div>
                  <div class="recommendation-item priority-medium">
                    <span class="priority-badge">Medium</span>
                    <p>Monitor temperature during hot weather periods</p>
                  </div>
                  <div class="recommendation-item priority-low">
                    <span class="priority-badge">Low</span>
                    <p>Consider pH adjustment for better decomposition</p>
                  </div>
                </div>
              </div>
              <button class="report-button">Export Actions</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import CompostForecast from '@/components/CompostForecast.vue'

export default {
  name: 'Historical',
  components: {
    CompostForecast
  },
  data() {
    return {
      activeTab: 'overview',
      tabs: [
        { id: 'overview', label: 'Overview', icon: '📊' },
        { id: 'forecast', label: 'Forecast', icon: '🔮' },
        { id: 'historical', label: 'Historical', icon: '📈' },
        { id: 'reports', label: 'Reports', icon: '📋' }
      ]
    }
  },
  methods: {
    downloadReport(reportType) {
      // Implement report download logic
      console.log(`Downloading ${reportType} report...`)
    },
    
    exportActions() {
      // Implement action export logic
      console.log('Exporting management actions...')
    }
  }
}
</script>

<style scoped>
.historical-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.page-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2rem 0;
  margin-bottom: 0;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
  text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.page-subtitle {
  font-size: 1.2rem;
  opacity: 0.9;
  margin: 0 0 2rem 0;
}

.header-stats {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.stat-badge {
  background: rgba(255,255,255,0.2);
  backdrop-filter: blur(10px);
  padding: 0.75rem 1rem;
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.3);
}

.stat-label {
  display: block;
  font-size: 0.8rem;
  opacity: 0.8;
  margin-bottom: 0.25rem;
}

.stat-value {
  display: block;
  font-weight: 600;
  font-size: 1rem;
}

.nav-tabs {
  background: white;
  border-bottom: 1px solid #e0e7ff;
  padding: 0 2rem;
  display: flex;
  gap: 0;
  max-width: 1200px;
  margin: 0 auto;
}

.tab-button {
  background: none;
  border: none;
  padding: 1rem 1.5rem;
  cursor: pointer;
  border-bottom: 3px solid transparent;
  transition: all 0.3s ease;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.tab-button:hover {
  background: #f8fafc;
  color: #667eea;
}

.tab-button.active {
  color: #667eea;
  border-bottom-color: #667eea;
  background: #f8fafc;
}

.tab-icon {
  font-size: 1.2rem;
}

.tab-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.tab-panel {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Overview Tab Styles */
.overview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
}

.overview-card {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
  border: 1px solid #e0e7ff;
}

.overview-card h3 {
  margin: 0 0 1.5rem 0;
  color: #374151;
  font-size: 1.3rem;
}

.card-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0;
  border-bottom: 1px solid #f3f4f6;
}

.summary-item:last-child {
  border-bottom: none;
}

.label {
  color: #6b7280;
  font-weight: 500;
}

.value {
  color: #374151;
  font-weight: 600;
}

.insight-item, .model-feature {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem 0;
  border-bottom: 1px solid #f3f4f6;
}

.insight-item:last-child, .model-feature:last-child {
  border-bottom: none;
}

.insight-icon, .feature-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.insight-text, .feature-text {
  flex: 1;
}

.insight-text strong, .feature-text strong {
  color: #374151;
  display: block;
  margin-bottom: 0.25rem;
}

.insight-text p, .feature-text p {
  color: #6b7280;
  margin: 0;
  font-size: 0.9rem;
}

/* Historical Tab Styles */
.historical-section h2 {
  color: #374151;
  margin: 0 0 2rem 0;
  font-size: 1.8rem;
}

.analysis-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.analysis-card {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}

.analysis-card h3 {
  margin: 0 0 1.5rem 0;
  color: #374151;
}

.chart-placeholder {
  text-align: center;
  padding: 2rem;
  background: #f8fafc;
  border-radius: 8px;
}

.placeholder-chart {
  display: flex;
  align-items: end;
  justify-content: center;
  gap: 0.5rem;
  height: 100px;
  margin-top: 1rem;
}

.chart-bar {
  background: linear-gradient(to top, #667eea, #764ba2);
  width: 20px;
  border-radius: 2px;
  transition: all 0.3s ease;
}

.chart-bar:hover {
  transform: scale(1.1);
}

.correlation-stats {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: #f8fafc;
  border-radius: 8px;
}

.stat-name {
  color: #6b7280;
  font-weight: 500;
}

.stat-result {
  color: #374151;
  font-weight: 600;
}

.nutrient-grid {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.nutrient-item {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.nutrient-name {
  min-width: 120px;
  font-weight: 500;
  color: #374151;
}

.nutrient-bar {
  flex: 1;
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
}

.nutrient-fill {
  height: 100%;
  background: linear-gradient(to right, #10b981, #34d399);
  transition: width 0.5s ease;
}

.nutrient-value {
  min-width: 60px;
  font-weight: 600;
  color: #059669;
}

/* Reports Tab Styles */
.reports-section h2 {
  color: #374151;
  margin: 0 0 2rem 0;
  font-size: 1.8rem;
}

.reports-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
}

.report-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
  border: 1px solid #e0e7ff;
}

.report-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.report-header h3 {
  margin: 0;
  font-size: 1.2rem;
}

.report-date {
  font-size: 0.9rem;
  opacity: 0.8;
}

.report-content {
  padding: 2rem;
}

.report-metric {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0;
  border-bottom: 1px solid #f3f4f6;
}

.report-metric:last-child {
  border-bottom: none;
}

.metric-label {
  color: #6b7280;
  font-weight: 500;
}

.metric-value {
  color: #374151;
  font-weight: 600;
}

.metric-trend {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 600;
}

.metric-trend.up {
  background: #dcfce7;
  color: #166534;
}

.metric-trend.down {
  background: #fee2e2;
  color: #991b1b;
}

.metric-trend.stable {
  background: #e0e7ff;
  color: #3730a3;
}

.accuracy-metric {
  text-align: center;
  margin-bottom: 1.5rem;
}

.accuracy-circle {
  position: relative;
  width: 120px;
  height: 120px;
  margin: 0 auto 1rem;
  border-radius: 50%;
  background: conic-gradient(from 0deg, #667eea calc(var(--percentage) * 1%), #e5e7eb 0%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.accuracy-circle::before {
  content: '';
  position: absolute;
  width: 80px;
  height: 80px;
  background: white;
  border-radius: 50%;
}

.accuracy-text {
  position: relative;
  z-index: 1;
  font-size: 1.5rem;
  font-weight: 700;
  color: #374151;
}

.accuracy-label {
  color: #6b7280;
  font-weight: 500;
  margin: 0;
}

.improvement-note p {
  color: #6b7280;
  font-size: 0.9rem;
  line-height: 1.5;
  margin: 0;
}

.recommendation-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.recommendation-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-radius: 8px;
  border-left: 4px solid;
}

.recommendation-item.priority-high {
  background: #fef2f2;
  border-left-color: #ef4444;
}

.recommendation-item.priority-medium {
  background: #fefbf2;
  border-left-color: #f59e0b;
}

.recommendation-item.priority-low {
  background: #f0fdf4;
  border-left-color: #10b981;
}

.priority-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  color: white;
  min-width: 60px;
  text-align: center;
}

.priority-high .priority-badge {
  background: #ef4444;
}

.priority-medium .priority-badge {
  background: #f59e0b;
}

.priority-low .priority-badge {
  background: #10b981;
}

.recommendation-item p {
  margin: 0;
  color: #374151;
  font-weight: 500;
}

.report-button {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  width: 100%;
  margin-top: 1rem;
}

.report-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 12px rgba(102, 126, 234, 0.3);
}

/* Responsive Design */
@media (max-width: 768px) {
  .header-content {
    padding: 0 1rem;
  }

  .page-title {
    font-size: 2rem;
  }

  .nav-tabs {
    padding: 0 1rem;
    overflow-x: auto;
  }

  .tab-content {
    padding: 1rem;
  }

  .overview-grid,
  .analysis-grid,
  .reports-grid {
    grid-template-columns: 1fr;
  }

  .header-stats {
    justify-content: center;
  }

  .tab-button {
    white-space: nowrap;
  }
}
</style>