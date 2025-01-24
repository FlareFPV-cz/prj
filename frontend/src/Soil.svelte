<script>
    import { onMount } from "svelte";
    import L from "leaflet";
    import "leaflet/dist/leaflet.css";

    let map;
    let lon = 15.5, lat = 49.75; // Default coordinates
    let soilData = null;
    let loading = true;
    let errorMessage = null;

    async function fetchSoilData() {
      loading = true;
      errorMessage = null;

      try {
        const response = await fetch(
          `http://localhost:8000/soil-data/?lon=${lon}&lat=${lat}`
        );
        if (response.ok) {
          const data = await response.json();
          soilData = data.data; // Update soil data
        } else {
          throw new Error("Failed to fetch soil data. Please check the server.");
        }
      } catch (error) {
        errorMessage = error.message;
      } finally {
        loading = false;
      }
    }

    function toggleContent(event) {
      const button = event.currentTarget;
      const content = button.nextElementSibling;

      button.classList.toggle("active");

      if (content.style.display === "block") {
        content.style.display = "none";
      } else {
        content.style.display = "block";
      }
    }

    onMount(() => {
      // Initialize Leaflet map
      map = L.map("map").setView([lat, lon], 8);

      // Add OpenStreetMap tiles
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: '© OpenStreetMap contributors',
      }).addTo(map);

      // Add marker
      const marker = L.marker([lat, lon]).addTo(map).bindPopup("Selected Location");

      // Handle map click
      map.on("click", async (e) => {
        lon = e.latlng.lng;
        lat = e.latlng.lat;
        marker.setLatLng([lat, lon]).openPopup();
        await fetchSoilData();
      });

      fetchSoilData();
    });
</script>

<head>
    <link rel="stylesheet" href="../css/soil.css">
</head>

<style>
    #map-container {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 20px;
      padding: 20px;
    }

    #map {
      height: 500px;
      width: 100%;
      min-width: 800px;
      max-width: 800px;
      border-radius: 12px;
      box-shadow: 0px 4px 20px rgba(0, 0, 0, 0.5);
    }
</style>

<div id="map-container">
  <div id="map"></div>

  {#if loading}
    <div class="info-panel">
      <p>Loading soil data...</p>
    </div>
  {:else if errorMessage}
    <div class="info-panel">
      <p class="error-message">{errorMessage}</p>
    </div>
  {:else if soilData}
    <div class="info-panel">
      <h2>Soil Data</h2>
      <p><strong>Type:</strong> {soilData.type}</p>
      <p><strong>Coordinates:</strong> [{soilData.geometry.coordinates.join(", ")}]
      </p>
      <h3>Layers:</h3>
      {#each soilData.properties.layers as layer}
        <button class="collapsible" on:click="{toggleContent}">{layer.name}</button>
        <div class="content">
          <p><strong>Units:</strong> {layer.unit_measure.mapped_units || "N/A"}</p>
          <table>
            <thead>
              <tr>
                <th>Depth Label</th>
                <th>Depth Range</th>
                <th>Q0.05</th>
                <th>Q0.5</th>
                <th>Q0.95</th>
                <th>Mean</th>
                <th>Uncertainty</th>
              </tr>
            </thead>
            <tbody>
              {#each layer.depths as depth}
                <tr>
                  <td>{depth.label}</td>
                  <td>{depth.range.top_depth}-{depth.range.bottom_depth} {depth.range.unit_depth}</td>
                  <td>{depth.values["Q0.05"] || "N/A"}</td>
                  <td>{depth.values["Q0.5"] || "N/A"}</td>
                  <td>{depth.values["Q0.95"] || "N/A"}</td>
                  <td>{depth.values.mean || "N/A"}</td>
                  <td>{depth.values.uncertainty || "N/A"}</td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      {/each}
    </div>
  {/if}
</div>
