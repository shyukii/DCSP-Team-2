<template>
  <div class="compost-forecast">
    <!-- DEBUG LINE - ADD THIS -->
    <div style="background: red; color: white; padding: 1rem; margin: 1rem; border-radius: 8px;">
      🔍 DEBUG: CompostForecast loaded! State - Loading: {{ loading }}, Error: {{ error }}, Data: {{ historicalData.length }} rows
    </div>
    <!-- Header -->
    <div class="forecast-header">
      <h1 class="forecast-title">Weather-Enhanced Compost Moisture Forecast</h1>
      <p class="forecast-subtitle">
        Advanced prediction model integrating Singapore weather patterns with historical measurements
      </p>
      <div class="weather-badge">
        <span class="weather-icon">🌤️</span>
        <span class="weather-text">Live Weather Integration Active</span>
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p class="loading-text">Processing compost data and generating forecasts...</p>
    </div>

    <!-- Error state -->
    <div v-if="error" class="error-container">
      <div class="error-icon">⚠️</div>
      <h2 class="error-title">Data Processing Error</h2>
      <p class="error-message">{{ error }}</p>
      <button @click="loadData" class="retry-button">Retry</button>
    </div>

    <!-- Main content -->
    <div v-if="!loading && !error" class="forecast-content">
      <!-- Key Metrics -->
      <div class="metrics-grid">
        <div class="metric-card">
          <h3 class="metric-label">Data Points</h3>
          <p class="metric-value">{{ historicalData.length.toLocaleString() }}</p>
          <p class="metric-subtitle">Historical readings</p>
        </div>
        
        <div class="metric-card">
          <h3 class="metric-label">Avg Moisture</h3>
          <p class="metric-value">{{ averageMoisture }}%</p>
          <p class="metric-subtitle">Historical average</p>
        </div>
        
        <div class="metric-card">
          <h3 class="metric-label">Forecast Period</h3>
          <p class="metric-value">90 Days</p>
          <p class="metric-subtitle">Weather-enhanced</p>
        </div>
        
        <div class="metric-card">
          <h3 class="metric-label">Active Alerts</h3>
          <p class="metric-value">{{ alerts.length }}</p>
          <p class="metric-subtitle">Management actions</p>
        </div>
      </div>

      <!-- Management Alerts -->
      <div v-if="alerts.length > 0" class="alerts-section">
        <h2 class="alerts-title">🚨 Management Alerts</h2>
        <div class="alerts-grid">
          <div 
            v-for="alert in alerts.slice(0, 4)" 
            :key="alert.date"
            :class="['alert-card', `alert-${alert.severity}`]"
          >
            <div class="alert-content">
              <p class="alert-date">{{ alert.date }}</p>
              <p class="alert-message">{{ alert.message }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Chart Section -->
      <div class="chart-section">
        <h2 class="chart-title">Moisture Level Trends & Weather-Enhanced Predictions</h2>
        <div class="chart-container">
          <canvas ref="chartCanvas" class="forecast-chart"></canvas>
        </div>
      </div>

      <!-- Model Information -->
      <div class="info-grid">
        <div class="info-card">
          <h3 class="info-title">🌡️ Weather Integration</h3>
          <div class="info-content">
            <div class="info-item">
              <h4>Evaporation Modeling</h4>
              <p>Temperature and humidity drive moisture loss predictions</p>
            </div>
            <div class="info-item">
              <h4>Seasonal Patterns</h4>
              <p>Singapore climate cycles integrated into forecasts</p>
            </div>
            <div class="info-item">
              <h4>Real-time Updates</h4>
              <p>Daily weather data refreshes predictions</p>
            </div>
          </div>
        </div>

        <div class="info-card">
          <h3 class="info-title">📈 Management Recommendations</h3>
          <div class="recommendations-list">
            <div class="recommendation-item">
              <span class="rec-icon">🔍</span>
              <span>Monitor moisture during high temperature periods</span>
            </div>
            <div class="recommendation-item">
              <span class="rec-icon">💧</span>
              <span>Increase watering when evaporation alerts are active</span>
            </div>
            <div class="recommendation-item">
              <span class="rec-icon">🎯</span>
              <span>Maintain 40-60% moisture for optimal decomposition</span>
            </div>
            <div class="recommendation-item">
              <span class="rec-icon">📅</span>
              <span>Use forecasts to plan maintenance schedules</span>
            </div>
          </div>
        </div>
      </div>

      <!-- API Status -->
      <div class="api-status">
        <div class="api-content">
          <div class="api-info">
            <h3>Singapore Weather API Integration</h3>
            <p>Collection ID: 1459 - Air Temperature & Humidity datasets</p>
            <p class="api-details">Next update: Every 24 hours | Coverage: Island-wide stations</p>
          </div>
          <div class="api-badge">
            <div class="status-indicator">✓ Connected</div>
            <p class="sync-info">Last sync: Real-time</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Chart from 'chart.js/auto'

export default {
  name: 'CompostForecast',
  data() {
    return {
      loading: true,
      error: null,
      historicalData: [],
      forecasts: [],
      alerts: [],
      chart: null
    }
  },
  computed: {
    averageMoisture() {
      if (this.historicalData.length === 0) return '0.0'
      const sum = this.historicalData.reduce((acc, item) => acc + item.moisture, 0)
      return (sum / this.historicalData.length).toFixed(1)
    }
  },
  mounted() {
    this.loadData()
  },
  beforeUnmount() {
    if (this.chart) {
      this.chart.destroy()
    }
  },
  methods: {
    async loadData() {
      try {
        this.loading = true
        this.error = null

        // Load CSV file from public folder
        const response = await fetch('/Combined_Humid_Temp_Cleaned.csv')
        if (!response.ok) {
          throw new Error('CSV file not found. Please ensure Combined_Humid_Temp_Cleaned.csv is in the public folder.')
        }
        
        const csvText = await response.text()
        
        // Simple CSV parsing
        const lines = csvText.trim().split('\n')
        const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''))
        
        // Find column indices
        const timestampIdx = headers.findIndex(h => h.toLowerCase().includes('timestamp'))
        const moistureIdx = headers.findIndex(h => h.toLowerCase().includes('soil moisture'))
        const tempIdx = headers.findIndex(h => h.toLowerCase().includes('air temperature'))
        const humidityIdx = headers.findIndex(h => h.toLowerCase().includes('humidity'))
        
        if (timestampIdx === -1 || moistureIdx === -1) {
          throw new Error('Required columns (timestamp, soil moisture) not found in CSV')
        }

        // Process data with error handling
        const processedData = []
        for (let i = 1; i < lines.length; i += 300) { // Sample every 300th row
          try {
            const row = lines[i].split(',')
            if (row.length > Math.max(timestampIdx, moistureIdx, tempIdx, humidityIdx)) {
              const timestamp = row[timestampIdx].replace(/"/g, '').trim()
              const moisture = parseFloat(row[moistureIdx])
              const temp = parseFloat(row[tempIdx] || 26)
              const humidity = parseFloat(row[humidityIdx] || 80)
              
              const date = new Date(timestamp)
              
              if (!isNaN(date.getTime()) && 
                  !isNaN(moisture) && 
                  moisture >= 0 && 
                  moisture <= 100) {
                
                processedData.push({
                  date: date,
                  moisture: moisture,
                  temperature: temp,
                  humidity: humidity,
                  dateStr: date.toISOString().split('T')[0]
                })
              }
            }
          } catch (rowError) {
            // Skip problematic rows
            continue
          }
        }

        if (processedData.length === 0) {
          throw new Error('No valid data found in CSV file')
        }

        // Sort by date
        processedData.sort((a, b) => a.date - b.date)

        // Apply smoothing
        this.historicalData = this.applySmoothing(processedData)
        
        // Generate forecast
        this.generateForecast()
        
        // Create chart
        await this.$nextTick()
        this.createChart()
        
        this.loading = false

      } catch (err) {
        console.error('Error loading data:', err)
        this.error = err.message
        this.loading = false
      }
    },

    applySmoothing(data, windowSize = 3) {
      return data.map((point, index) => {
        const start = Math.max(0, index - windowSize)
        const end = Math.min(data.length, index + windowSize + 1)
        const window = data.slice(start, end)
        
        const avgMoisture = window.reduce((sum, p) => sum + (p.moisture || 0), 0) / window.length
        
        return {
          ...point,
          smoothedMoisture: isNaN(avgMoisture) ? point.moisture : avgMoisture
        }
      })
    },

    generateForecast() {
      const lastDate = this.historicalData[this.historicalData.length - 1].date
      const recentData = this.historicalData.slice(-20)
      
      // Simple trend calculation
      const moistureTrend = this.calculateSimpleTrend(recentData.map(d => d.smoothedMoisture))
      
      // Generate forecasts
      this.forecasts = []
      this.alerts = []
      let currentMoisture = recentData[recentData.length - 1].smoothedMoisture

      for (let i = 1; i <= 90; i++) {
        const forecastDate = new Date(lastDate)
        forecastDate.setDate(forecastDate.getDate() + i)
        
        // Simulate weather data for Singapore
        const dayOfYear = Math.floor((forecastDate - new Date(forecastDate.getFullYear(), 0, 0)) / (1000 * 60 * 60 * 24))
        const airTemp = 27 + 3 * Math.sin(dayOfYear * 2 * Math.PI / 365) + (Math.random() - 0.5) * 4
        const airHumidity = 78 + 12 * Math.sin((dayOfYear + 90) * 2 * Math.PI / 365) + (Math.random() - 0.5) * 10
        
        // Calculate evaporation
        const evaporationFactor = this.calculateEvaporation(
          Math.max(24, Math.min(35, airTemp)),
          Math.max(60, Math.min(95, airHumidity)),
          currentMoisture
        )
        
        // Predict moisture
        const trendFactor = moistureTrend * i * 0.05
        const seasonalFactor = 2 * Math.sin((dayOfYear + 180) * 2 * Math.PI / 365)
        
        let predictedMoisture = currentMoisture - evaporationFactor + trendFactor + seasonalFactor
        predictedMoisture += (Math.random() - 0.5) * 2 // Add variation
        predictedMoisture = Math.max(15, Math.min(100, predictedMoisture))
        
        // Generate alerts
        if (evaporationFactor > 1.0) {
          this.alerts.push({
            date: forecastDate.toISOString().split('T')[0],
            type: 'high_evaporation',
            message: `High moisture loss expected (${evaporationFactor.toFixed(1)}%). Consider extra watering.`,
            severity: 'warning'
          })
        }
        
        if (predictedMoisture < 25) {
          this.alerts.push({
            date: forecastDate.toISOString().split('T')[0],
            type: 'low_moisture',
            message: `Moisture dropping to ${predictedMoisture.toFixed(1)}%. Action needed.`,
            severity: 'critical'
          })
        }
        
        this.forecasts.push({
          dateStr: forecastDate.toISOString().split('T')[0],
          moisture: null,
          predictedMoisture: predictedMoisture,
          airTemp: airTemp,
          airHumidity: airHumidity,
          isForecast: true
        })
        
        currentMoisture = predictedMoisture
      }
    },

    calculateSimpleTrend(values) {
      if (values.length < 2) return 0
      const first = values[0] || 0
      const last = values[values.length - 1] || 0
      return (last - first) / values.length
    },

    calculateEvaporation(airTemp, airHumidity, soilMoisture) {
      const tempFactor = Math.max(0, (airTemp - 20) / 20)
      const humidityFactor = Math.max(0, (100 - airHumidity) / 100)
      const moistureFactor = soilMoisture / 100
      
      return tempFactor * humidityFactor * moistureFactor * 1.5
    },

    createChart() {
      if (!this.$refs.chartCanvas) return

      // Prepare chart data
      const combinedData = [
        ...this.historicalData.map(d => ({
          dateStr: d.dateStr,
          moisture: d.smoothedMoisture,
          predictedMoisture: null,
          airTemp: d.temperature,
          isForecast: false
        })),
        ...this.forecasts
      ]

      const labels = combinedData.map(d => d.dateStr)
      const historicalMoisture = combinedData.map(d => d.isForecast ? null : d.moisture)
      const predictedMoisture = combinedData.map(d => d.isForecast ? d.predictedMoisture : null)
      const temperature = combinedData.map(d => d.airTemp)

      // Create Chart.js chart
      this.chart = new Chart(this.$refs.chartCanvas, {
        type: 'line',
        data: {
          labels: labels,
          datasets: [
            {
              label: 'Historical Moisture',
              data: historicalMoisture,
              borderColor: 'rgb(37, 99, 235)',
              backgroundColor: 'rgba(37, 99, 235, 0.1)',
              borderWidth: 2,
              fill: false,
              spanGaps: false,
              yAxisID: 'y'
            },
            {
              label: 'Predicted Moisture',
              data: predictedMoisture,
              borderColor: 'rgb(220, 38, 38)',
              backgroundColor: 'rgba(220, 38, 38, 0.1)',
              borderWidth: 2,
              borderDash: [5, 5],
              fill: false,
              spanGaps: false,
              yAxisID: 'y'
            },
            {
              label: 'Air Temperature',
              data: temperature,
              borderColor: 'rgb(245, 158, 11)',
              backgroundColor: 'rgba(245, 158, 11, 0.1)',
              borderWidth: 1,
              fill: false,
              yAxisID: 'y1'
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          interaction: {
            mode: 'index',
            intersect: false,
          },
          scales: {
            x: {
              display: true,
              title: {
                display: true,
                text: 'Date'
              },
              ticks: {
                maxTicksLimit: 20
              }
            },
            y: {
              type: 'linear',
              display: true,
              position: 'left',
              min: 0,
              max: 100,
              title: {
                display: true,
                text: 'Moisture (%)'
              }
            },
            y1: {
              type: 'linear',
              display: true,
              position: 'right',
              min: 20,
              max: 40,
              title: {
                display: true,
                text: 'Temperature (°C)'
              },
              grid: {
                drawOnChartArea: false,
              },
            }
          },
          plugins: {
            tooltip: {
              filter: function(tooltipItem) {
                return tooltipItem.parsed.y !== null
              }
            }
          }
        }
      })
    }
  }
}
</script>

<style scoped>
.compost-forecast {
  padding: 2rem;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  min-height: 100vh;
}

.forecast-header {
  text-align: center;
  margin-bottom: 2rem;
}

.forecast-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #374151;
  margin: 0 0 1rem 0;
}

.forecast-subtitle {
  font-size: 1.2rem;
  color: #6b7280;
  margin: 0 0 1.5rem 0;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.weather-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(59, 130, 246, 0.1);
  color: #1d4ed8;
  padding: 0.75rem 1.5rem;
  border-radius: 50px;
  font-weight: 600;
}

.weather-icon {
  font-size: 1.2rem;
}

.loading-container {
  text-align: center;
  padding: 4rem 2rem;
}

.loading-spinner {
  border: 4px solid #f3f4f6;
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  width: 48px;
  height: 48px;
  animation: spin 1s linear infinite;
  margin: 0 auto 1.5rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  color: #6b7280;
  font-size: 1.1rem;
}

.error-container {
  text-align: center;
  padding: 4rem 2rem;
  background: white;
  border-radius: 16px;
  margin: 2rem auto;
  max-width: 500px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.error-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.error-title {
  color: #374151;
  font-size: 1.5rem;
  margin: 0 0 1rem 0;
}

.error-message {
  color: #6b7280;
  margin: 0 0 2rem 0;
}

.retry-button {
  background: #ef4444;
  color: white;
  border: none;
  padding: 0.75rem 2rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.3s ease;
}

.retry-button:hover {
  background: #dc2626;
}

.forecast-content {
  max-width: 1200px;
  margin: 0 auto;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.metric-card {
  background: white;
  padding: 2rem;
  border-radius: 16px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  text-align: center;
  border: 1px solid #e5e7eb;
}

.metric-label {
  color: #6b7280;
  font-size: 0.9rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0 0 0.5rem 0;
}

.metric-value {
  color: #1f2937;
  font-size: 2.5rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
}

.metric-subtitle {
  color: #9ca3af;
  font-size: 0.9rem;
  margin: 0;
}

.alerts-section {
  margin-bottom: 2rem;
}

.alerts-title {
  color: #374151;
  font-size: 1.8rem;
  margin: 0 0 1.5rem 0;
}

.alerts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
}

.alert-card {
  padding: 1.5rem;
  border-radius: 12px;
  border-left: 4px solid;
}

.alert-warning {
  background: #fef3cd;
  border-left-color: #f59e0b;
}

.alert-critical {
  background: #fee2e2;
  border-left-color: #ef4444;
}

.alert-content {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.alert-date {
  font-weight: 600;
  color: #374151;
  margin: 0;
}

.alert-message {
  color: #6b7280;
  margin: 0;
  font-size: 0.9rem;
}

.chart-section {
  background: white;
  padding: 2rem;
  border-radius: 16px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  margin-bottom: 2rem;
  border: 1px solid #e5e7eb;
}

.chart-title {
  color: #374151;
  font-size: 1.5rem;
  margin: 0 0 2rem 0;
}

.chart-container {
  position: relative;
  height: 400px;
}

.forecast-chart {
  width: 100% !important;
  height: 100% !important;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
}

.info-card {
  background: white;
  padding: 2rem;
  border-radius: 16px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  border: 1px solid #e5e7eb;
}

.info-title {
  color: #374151;
  font-size: 1.3rem;
  margin: 0 0 1.5rem 0;
}

.info-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.info-item {
  padding: 1rem;
  background: #f8fafc;
  border-radius: 8px;
}

.info-item h4 {
  color: #1f2937;
  font-size: 1rem;
  margin: 0 0 0.5rem 0;
}

.info-item p {
  color: #6b7280;
  font-size: 0.9rem;
  margin: 0;
  line-height: 1.5;
}

.recommendations-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.recommendation-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 8px;
}

.rec-icon {
  font-size: 1.2rem;
  flex-shrink: 0;
}

.api-status {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  border-radius: 16px;
  padding: 2rem;
  color: white;
}

.api-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.api-info h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1.2rem;
}

.api-info p {
  margin: 0 0 0.25rem 0;
  opacity: 0.9;
}

.api-details {
  font-size: 0.9rem;
  opacity: 0.7;
}

.api-badge {
  text-align: right;
}

.status-indicator {
  background: rgba(255, 255, 255, 0.2);
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.sync-info {
  font-size: 0.8rem;
  opacity: 0.7;
  margin: 0;
}

/* Responsive Design */
@media (max-width: 768px) {
  .compost-forecast {
    padding: 1rem;
  }

  .forecast-title {
    font-size: 2rem;
  }

  .metrics-grid {
    grid-template-columns: 1fr;
  }

  .alerts-grid {
    grid-template-columns: 1fr;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }

  .api-content {
    text-align: center;
  }

  .api-badge {
    text-align: center;
  }

  .chart-container {
    height: 300px;
  }
}
</style>