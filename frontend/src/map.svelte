<script>
    import { onMount } from "svelte";
    import L from "leaflet";
  
    let map;
    let indexValue = null;
    let bounds = null;
    let selectedIndexType = "ndvi"; // Default index type
  
    const fetchIndexValue = async (x, y) => {
      try {
        const response = await fetch("http://localhost:8000/get-index-value/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
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
  
    const loadMapOverlay = () => {
      const ndviMapUrl = `http://localhost:8000/get-map/?index_type=${selectedIndexType}`;
      L.imageOverlay(ndviMapUrl, bounds).addTo(map);
    };
  
    const updateMap = () => {
      if (map) {
        map.eachLayer((layer) => map.removeLayer(layer)); // Remove existing layers
        loadMapOverlay(); // Load new map overlay based on the selected index type
      }
    };
  
    onMount(() => {
      const img = new Image();
      img.src = `http://localhost:8000/get-map/?index_type=${selectedIndexType}`;
      img.onload = () => {
        const { naturalWidth, naturalHeight } = img;
        initializeMap(naturalWidth, naturalHeight);
      };
    });
  </script>
  
  <style>
    #map {
      height: 300px;
      width: 300px;
      margin: 0 auto;
      padding: 0;
      border: 2px solid #333;
    }
  
    .info-box {
      position: fixed;
      bottom: 20px;
      left: 50%;
      transform: translateX(-50%);
      background: rgba(0, 0, 0, 0.7);
      color: #fff;
      padding: 10px;
      border-radius: 5px;
      z-index: 1000;
      text-align: center;
    }
  
    .controls {
      margin: 20px auto;
      text-align: center;
    }
  
    select {
      padding: 5px;
      font-size: 14px;
    }
  </style>
  
  <div class="controls">
    <label for="index-type">Select Index Type:</label>
    <select id="index-type" bind:value={selectedIndexType} on:change={updateMap}>
      <option value="ndvi">NDVI</option>
      <option value="evi">EVI</option>
      <option value="savi">SAVI</option>
    </select>
  </div>
  
  <div id="map"></div>
  <div class="info-box">
    <h3>{selectedIndexType.toUpperCase()} Map</h3>
    {#if indexValue !== null}
      <p>Index Value: {indexValue}</p>
    {/if}
  </div>
  