<script>
  import { onMount } from "svelte";
  import L from "leaflet";
  import { checkAuth } from "../utils/auth";

  let map;
  let indexValue = null;
  let bounds = null;
  let selectedIndexType = "ndvi";
  let coordinates = { x: 0, y: 0 };

  const fetchIndexValue = async (x, y) => {
    try {
      coordinates = { x, y };
      const response = await fetch("http://localhost:8000/get-index-value/", {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ x, y, index_type: selectedIndexType }),
      });
      if (!response.ok) throw new Error("Failed to fetch index value.");
      const data = await response.json();
      indexValue = data.index_value;
    } catch (error) {
      console.error(error);
      indexValue = "Error fetching data";
    }
  };

  const initializeMap = (imageWidth, imageHeight) => {
    const southWest = [0, 0];
    const northEast = [imageHeight, imageWidth];
    bounds = [southWest, northEast];

    map = L.map("map", {
      crs: L.CRS.Simple,
      zoomControl: true,
      zoom: 0,
      minZoom: -2,
    });

    loadMapOverlay();
    map.fitBounds(bounds);

    map.on("click", (e) => {
      const { lat, lng } = e.latlng;
      const x = Math.floor(lng);
      const y = Math.floor(lat);
      if (x >= 0 && y >= 0 && x < imageWidth && y < imageHeight) {
        fetchIndexValue(x, y);
      } else {
        indexValue = "Clicked outside image bounds";
      }
    });
  };

  const loadMapOverlay = async () => {
    const ndviMapUrl = `http://localhost:8000/get-map/?index_type=${selectedIndexType}`;
    const response = await fetch(ndviMapUrl, {
      credentials: "include"
    });
    const blob = await response.blob();
    const imageUrl = URL.createObjectURL(blob);
    L.imageOverlay(imageUrl, bounds).addTo(map);
  };

  const updateMap = () => {
    if (map) {
      map.eachLayer((layer) => map.removeLayer(layer));
      loadMapOverlay();
      // Reset index value when changing index type
      indexValue = null;
    }
  };

  onMount(async () => {
    const auth = await checkAuth();
    if (!auth) return;
    const img = new Image();
    img.src = `http://localhost:8000/get-map/?index_type=${selectedIndexType}`;
    img.onload = () => {
      const { naturalWidth, naturalHeight } = img;
      initializeMap(naturalWidth, naturalHeight);
    };
  });
</script>

<head>
  <link rel="stylesheet" href="../css/map.css">
</head>

<div class="map-container">
  <div class="controls">
    <label for="index-type">Select Index Type:</label>
    <select id="index-type" bind:value={selectedIndexType} on:change={updateMap}>
      <option value="ndvi">NDVI</option>
      <option value="evi">EVI</option>
      <option value="savi">SAVI</option>
      <option value="arvi">ARVI</option>
      <option value="gndvi">GNDVI</option>
      <option value="msavi">MSAVI</option>
    </select>
  </div>

  <div id="map"></div>

  <div class="info-box">
    <h3>{selectedIndexType.toUpperCase()} Map Information</h3>
    {#if indexValue !== null}
      <div class="index-details">
        <p>Coordinates: ({coordinates.x}, {coordinates.y})</p>
        <p>Index Value: {indexValue}</p>
      </div>
    {/if}
  </div>
</div>

<style>
  .map-container {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    height: 100%;
  }

  .controls {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    background: #222222;
    border-radius: 8px;
  }

  select {
    padding: 0.5rem;
    border-radius: 4px;
    border: 1px solid #222222;
  }

  #map {
    height: 500px;
    border-radius: 8px;
    overflow: hidden;
  }

  .info-box {
    padding: 1rem;
    border-radius: 8px;
  }

  .index-details {
    margin-top: 0.5rem;
  }

  h3 {
    margin: 0;
    color: #ffffff;
  }
</style>
