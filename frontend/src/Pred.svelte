<script>
    import { onMount } from "svelte";
    import { checkAuth } from "./utils/auth";
    
    let lat = '';
    let lon = '';
    let condition = '';
    let recommendation = '';
    let confidence = 0;
    let soilData = {};
    let loading = false;
    let error = '';
  
    async function fetchPrediction() {
      loading = true;
      error = '';
      try {
        const response = await fetch(`http://localhost:8000/predict?lon=${lon}&lat=${lat}`, {
          credentials: "include"
        });
        
        if (!response.ok) throw new Error('Failed to fetch prediction');
        
        const data = await response.json();
        condition = data.condition;
        recommendation = data.recommendation;
        confidence = data.confidence;
        soilData = data.soil_data || {};
      } catch (err) {
        error = err.message;
      } finally {
        loading = false;
      }
    }
  
    onMount(async () => {
      const auth = await checkAuth();
      if (!auth) return;
    });
  </script>
  
  <svelte:head>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" />
  </svelte:head>
  
  <main style="display: flex;">
    <div class="card">
      <h1 class="header">
        <i class="fas fa-seedling"></i> Soil Health Analysis
      </h1>
  
      <div class="input-group">
        <label>Latitude</label>
        <input
          type="number"
          step="any"
          bind:value={lat}
          placeholder="e.g. 37.7749"
          class="input-field"
        />
      </div>
  
      <div class="input-group">
        <label>Longitude</label>
        <input
          type="number"
          step="any"
          bind:value={lon}
          placeholder="e.g. -122.4194"
          class="input-field"
        />
      </div>
  
      <button
        on:click={fetchPrediction}
        disabled={loading || !lat || !lon}
        class="submit-btn"
      >
        {#if loading}
          <i class="fas fa-spinner fa-spin"></i> Analyzing...
        {:else}
          <i class="fas fa-chart-line"></i> Analyze Soil
        {/if}
      </button>
  
      {#if error}
        <div class="error-message">
          <i class="fas fa-exclamation-triangle"></i> {error}
        </div>
      {/if}
  
      {#if condition}
      <div style="; box-shadow: 10px 14px 6px -1px rgba(0, 0, 0, 0.1); padding: 20px 20px 10px 10px;">
        <div class="status-card {condition.toLowerCase()}">
          <div class="status-header">
            <i class="fas {condition === 'Good' ? 'fa-check-circle' : 'fa-exclamation-triangle'}"></i>
            <h2>Soil Condition: {condition}</h2>
          </div>
          <div class="confidence-meter">
            <div class="meter-bar" style="width: {confidence * 100}%"></div>
          </div>
          <p>{(confidence * 100).toFixed(1)}% Confidence</p>
        </div>
  
        <div class="recommendation-card">
          <h3><i class="fas fa-lightbulb"></i> Recommendations</h3>
          <p>{recommendation}</p>
        </div>
  
        <div class="soil-details">
            <h3><i class="fas fa-microscope"></i> Soil Parameters</h3>
            {#if soilData.data && soilData.data.properties && soilData.data.properties.layers}
              <div class="soil-grid">
                {#each soilData.data.properties.layers as layer}
                  <div class="soil-parameter">
                    <span class="parameter-name">{layer.name}</span>
                    {#each layer.depths as depth}
                      <div class="depth-details">
                        <span class="depth-range">{depth.label}</span>
                        <span class="parameter-value">
                          Q0.5: {depth.values['Q0.5']} {layer.unit_measure.mapped_units}
                        </span>
                        <span class="parameter-value">
                          Mean: {depth.values.mean} {layer.unit_measure.mapped_units}
                        </span>
                      </div>
                    {/each}
                  </div>
                {/each}
              </div>
            {:else}
              <p>No soil data available.</p>
            {/if}
        </div>
        </div>
      {/if}
    </div>
  </main>
  
  <style>
    .card {
      border-radius: 10px;
      box-shadow: 1px 4px 6px -1px rgba(0, 0, 0, 0.1);
      padding: 2rem;
      display: flex;
      flex-direction: column;
      text-align: center;
    }
  
    .header {
      text-align: center;
      margin-bottom: 2rem;
      font-size: 1.5rem;
    }
  
    .input-group {
      margin-bottom: 1.5rem;
    }
  
    .input-group label {
      margin-bottom: 0.5rem;
      font-weight: 500;
    }
  
    .input-field {
      width: 90%;
      padding: 10px 0 10px 10px;
      border: 1px solid #cbd5e0;
      border-radius: 6px;
      font-size: 1rem;
    }
  
    .submit-btn {
      width: 100%;
      padding: 1rem;
      background: #2c7a7b;
      border: none;
      border-radius: 6px;
      font-size: 1rem;
      cursor: pointer;
      transition: background-color 0.3s ease;
    }
  
    .submit-btn:hover:not(:disabled) {
      background-color: #434343;
    }
  
    .submit-btn:disabled {
      opacity: 0.7;
      cursor: not-allowed;
    }
  
    .status-card {
      padding: 1.5rem;
      border-radius: 8px;
      margin: 1.5rem 0;
    }
  
    .status-card.good {
      border: 2px solid #48bb78;
    }
  
    .status-card.poor {
      border: 2px solid #f56565;
    }
  
    .status-header {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      margin-bottom: 1rem;
    }
  
    .confidence-meter {
      background: #595959;
      height: 24px;
      border-radius: 12px;
      position: relative;
      overflow: hidden;
    }
  
    .meter-bar {
      position: absolute;
      left: 0;
      top: 0;
      height: 100%;
      background: #cecece;
      transition: width 0.5s ease;
    }
  
    .soil-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 1rem;
      margin-top: 1rem;
    }
  
    .soil-parameter {
      background: #343434;
      padding: 1rem;
      border-radius: 6px;
      text-align: center;
    }
  
    .parameter-name {
      font-weight: 600;
      color: #5e5e5f;
      text-transform: capitalize;
    }
  
    .parameter-value {
      font-size: 1.25rem;
      color: #2c7a7b;
      margin-top: 0.5rem;
      display: block;
    }
  
    .error-message {
      background: #303030;
      color: #c53030;
      padding: 1rem;
      border-radius: 6px;
      margin: 1rem 0;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }
  
    .fa-spinner {
      animation: spin 1s linear infinite;
    }
  
    @keyframes spin {
      from { transform: rotate(0deg); }
      to { transform: rotate(360deg); }
    }
  </style>