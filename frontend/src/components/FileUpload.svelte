<script lang="ts">
  import { onMount } from 'svelte';
  import { checkAuth } from "../utils/auth";

  let file: HTMLInputElement;
  let analysisMethod = "ndvi"; // Default method
  let resultImagePath = ""; // To hold the returned image path
  let insights = null;

  onMount(async () => {
    const auth = await checkAuth();
    if (!auth) return; // Stop execution if not authenticated
  });

  async function handleUpload() {
    if (!file || !file.files[0]) {
      alert("Please select a file to upload.");
      return;
    }
    
    const formData = new FormData();
    formData.append('file', file.files[0]);

    const response = await fetch(`http://localhost:8000/analyze/${analysisMethod}/`, {
      method: 'POST',
      body: formData,
      credentials: "include"
    });

    if (!response.ok) {
      alert("An error occurred during the analysis. Please try again.");
      return;
    }

    const result = await response.json();
    console.log(result);

    if (result.file_path) {
      resultImagePath = `http://localhost:8000/${result.file_path}`;
      insights = result.insights;
      alert(`Analysis complete. File saved at ${result.file_path}`);
    } else {
      alert("Unexpected response from the server.");
    }
    console.log(insights);
  }
</script>


<div class="file-upload-container">
  <div class="analysis-method-selector">
    <label for="analysis-method">Choose Analysis Method:</label>
    <select id="analysis-method" on:change={(e: Event) => analysisMethod = (e.target as HTMLSelectElement).value}>
      <option value="ndvi">NDVI (Normalized Difference Vegetation Index)</option>
      <option value="evi">EVI (Enhanced Vegetation Index)</option>
      <option value="savi">SAVI (Soil Adjusted Vegetation Index)</option>
      <option value="arvi">ARVI (Atmospherically Resistant Vegetation Index)</option>
      <option value="gndvi">GNDVI (Green Normalized Difference Vegetation Index)</option>
      <option value="msavi">MSAVI (Modified Soil-Adjusted Vegetation Index)</option>
    </select>
  </div>

  <div class="file-input-container">
    <input type="file" bind:this={file} />
    <button on:click={handleUpload}>Upload and Analyze</button>
  </div>

  {#if insights}
    <div class="insights-container">
      <h3>Analysis Insights:</h3>
      <table>
        <thead>
          <tr>
            <th>Metric</th>
            <th>Value</th>
          </tr>
        </thead>
        <tbody>
          {#each Object.entries(insights) as [key, value]}
            <tr>
              <td>{key}</td>
              <td>{value.toFixed(2)}%</td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}
</div>

<style>
  .file-upload-container {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .analysis-method-selector,
  .file-input-container {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  select {
    padding: 0.5rem;
    border-radius: 4px;
    border: 1px solid #ccc;
  }

  button {
    padding: 0.5rem 1rem;
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.3s;
  }

  button:hover {
    background-color: #2980b9;
  }

  .insights-container {
    margin-top: 1rem;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 0.5rem;
  }

  th, td {
    padding: 0.5rem;
    border: 1px solid #ddd;
    text-align: left;
  }

  th {
    background-color: #2f2f2f;
  }
</style>