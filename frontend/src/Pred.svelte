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
      condition = '';
      recommendation = '';
      confidence = 0;
      soilData = {};
      try {
          const response = await fetch(`http://localhost:8000/predict?lon=${lon}&lat=${lat}`, {credentials: "include"});
          if (!response.ok) {
              throw new Error('Failed to fetch prediction');
          }
          const data = await response.json();
          condition = data.condition;
          recommendation = data.recommendation;
          confidence = data.confidence;
          soilData = data.soil_data;
      } catch (err) {
          error = err.message;
      } finally {
          loading = false;
      }
  }

  onMount(async () => {
      const auth = await checkAuth();
      if (!auth) return; // Stop execution if not authenticated
  });
</script>

<head>
  <link rel="stylesheet" href="../css/pred.css">
</head>

<main style="display: flex;">
  <div class="card">
      <h1 class="text-xl font-bold text-center">Soil Condition Prediction</h1>

      <div class="input-group">
          <label class="text-sm font-medium">Latitude</label>
          <input
              type="number"
              step="any"
              bind:value={lat}
              placeholder="Enter latitude"
          />
      </div>

      <div class="input-group">
          <label class="text-sm font-medium">Longitude</label>
          <input
              type="number"
              step="any"
              bind:value={lon}
              placeholder="Enter longitude"
          />
      </div>

      <button
          on:click={fetchPrediction}
          disabled={loading || !lat || !lon}
      >
          {loading ? 'Loading...' : 'Get Prediction'}
          {#if loading}
              <span class="spinner"></span>
          {/if}
      </button>

      {#if error}
          <p class="error">{error}</p>
      {/if}

      {#if condition}
          <div class="results">
              <p class="text-lg font-semibold">Condition: <span class="text-blue-400">{condition}</span></p>
              <p class="text-lg font-semibold">Confidence: <span class="text-blue-400">{(confidence * 100).toFixed(2)}%</span></p>
              <p>Recommendation: {recommendation}</p>
          </div>

          <details>
              <summary>View Soil Data</summary>
              <pre>{JSON.stringify(soilData, null, 2)}</pre>
          </details>
      {/if}
  </div>
</main>
