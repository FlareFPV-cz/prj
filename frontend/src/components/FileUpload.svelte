<!-- <script>
  let file;
  let analysisMethod = "ndvi"; // Default method
  let resultImagePath = ""; // To hold the returned image path

  async function handleUpload() {
    if (!file || !file.files[0]) {
      alert("Please select a file to upload.");
      return;
    }

    const formData = new FormData();
    formData.append('file', file.files[0]);

    const response = await fetch(`http://localhost:8000/${analysisMethod}/`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      alert("An error occurred during the analysis. Please try again.");
      return;
    }

    const result = await response.json();
    console.log(result);

    if (result.file_path) {
      resultImagePath = `http://localhost:8000/${result.file_path}`;
      alert(`Analysis complete. File saved at ${result.file_path}`);
    } else {
      alert("Unexpected response from the server.");
    }
  }
</script>

<div>
  <label for="analysis-method">Choose Analysis Method:</label>
  <select id="analysis-method" on:change={(e) => analysisMethod = e.target.value}>
    <option value="ndvi">NDVI (Normalized Difference Vegetation Index)</option>
    <option value="evi">EVI (Enhanced Vegetation Index)</option>
  </select>
</div>

<div>
  <input type="file" bind:this={file} />
  <button on:click={handleUpload}>Upload and Analyze</button>
</div>

<div>
  <h3>Analysis Result:</h3>
  {#if resultImagePath}
    <img src={resultImagePath} alt="Analysis Result" style="max-width: 50%; border: 1px solid #ccc; margin-top: 10px;" />
  {/if}
</div> -->

<!-- <script>
  import { onMount } from 'svelte';
  import Chart from 'chart.js/auto';

  let file;
  let analysisMethod = "ndvi"; // Default method
  let resultImagePath = ""; // To hold the returned image path
  let insights = null;

  async function handleUpload() {
    if (!file || !file.files[0]) {
      alert("Please select a file to upload.");
      return;
    }

    const formData = new FormData();
    formData.append('file', file.files[0]);

    const response = await fetch(`http://localhost:8000/${analysisMethod}/`, {
      method: 'POST',
      body: formData,
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
    // console.log(insights);
  }
</script>

<div>
  <label for="analysis-method">Choose Analysis Method:</label>
  <select id="analysis-method" on:change={(e) => analysisMethod = e.target.value}>
    <option value="ndvi">NDVI (Normalized Difference Vegetation Index)</option>
    <option value="evi">EVI (Enhanced Vegetation Index)</option>
    <option value="savi">SAVI(Soil Adjusted Vegetation Index)</option>
  </select>
</div>

<div>
  <input type="file" bind:this={file} />
  <button on:click={handleUpload}>Upload and Analyze</button>
</div>

<div>
  {#if resultImagePath}
  <h3>Analysis Result:</h3>
    <img src={resultImagePath} alt="Analysis Result" style="max-width: 50%; border: 1px solid #ccc; margin-top: 10px;" />
  {/if}
</div>

<div style="text-align: center;">
  {#if insights}
    <h3>Insights:</h3>
    <table border="1" style="width: 50%; margin: 10px auto;">
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
  {/if}
</div> -->

<script>
  import { onMount } from 'svelte';
  import L from "leaflet";

  let file;
  let analysisMethod = "ndvi"; // Default method
  let resultImagePath = ""; // To hold the returned image path
  let insights = null;

  let map, imageLayer;

  // Function to fetch index value
  async function fetchIndexValue(x, y, indexType) {
      const response = await fetch("/get-index-value/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ x, y, index_type: indexType }),
      });
      if (response.ok) {
          const data = await response.json();
          alert(`Coordinates: (${data.x}, ${data.y})\n${data.index_type}: ${data.index_value}`);
      } else {
          alert("Error retrieving index value.");
      }
  }

  onMount(() => {
      // Initialize map
      map = L.map("map", {
          crs: L.CRS.Simple,
          minZoom: -1,
          maxZoom: 4,
      });

      const bounds = [[0, 0], [1024, 1024]]; // Adjust based on your image dimensions
      imageLayer = L.imageOverlay("", bounds).addTo(map);
      map.fitBounds(bounds);

      // Add click event listener
      map.on("click", (e) => {
          const { x, y } = map.latLngToContainerPoint(e.latlng); // Get pixel coordinates
          fetchIndexValue(Math.round(x), Math.round(y), "ndvi");
      });
  });


  async function handleUpload() {
    if (!file || !file.files[0]) {
      alert("Please select a file to upload.");
      return;
    }

    const formData = new FormData();
    formData.append('file', file.files[0]);

    const response = await fetch(`http://localhost:8000/${analysisMethod}/`, {
      method: 'POST',
      body: formData,
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

<div>
  <label for="analysis-method">Choose Analysis Method:</label>
  <select id="analysis-method" on:change={(e) => analysisMethod = e.target.value}>
    <option value="ndvi">NDVI (Normalized Difference Vegetation Index)</option>
    <option value="evi">EVI (Enhanced Vegetation Index)</option>
    <option value="savi">SAVI(Soil Adjusted Vegetation Index)</option>
  </select>
</div>

<div>
  <input type="file" bind:this={file} />
  <button on:click={handleUpload}>Upload and Analyze</button>
</div>

<div>
  {#if resultImagePath}
  <h3>Analysis Result:</h3>
    <img src={resultImagePath} alt="Analysis Result" style="max-width: 50%; border: 1px solid #ccc; margin-top: 10px;" />
  {/if}
</div>

<div style="text-align: center;">
  {#if insights}
    <h3>Insights:</h3>
    <table border="1" style="width: 50%; margin: 10px auto;">
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
  {/if}
</div>