<script>
  import { onMount } from "svelte";
  import { checkAuth } from "../utils/auth";

  let x = 0;
  let y = 0;
  let indexType = "ndvi";
  let result = null;
  let error = null;

  async function fetchIndexValue() {
    error = null;
    result = null;

    const auth = await checkAuth();
    if (!auth) return;


    try {
      const response = await fetch("http://localhost:8000/get-index-value/", {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ x, y, index_type: indexType }),
      });

      console.log(x, y, indexType);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to fetch index value.");
      }

      result = await response.json();
    } catch (err) {
      error = err.message;
    }
  }
</script>

<style>
  .error {
    color: red;
  }
  .result {
    color: green;
  }
</style>

<main>
  <form
    on:submit|preventDefault={() => {
      fetchIndexValue();
    }}
  >
    <label for="x">X Coordinate:</label>
    <input id="x" type="number" bind:value={x} />

    <label for="y">Y Coordinate:</label>
    <input id="y" type="number" bind:value={y} />

    <label for="indexType">Index Type:</label>
    <select id="indexType" bind:value={indexType}>
      <option value="ndvi">NDVI</option>
      <option value="evi">EVI</option>
      <option value="savi">SAVI</option>
      <option value="arvi">ARVI</option>
      <option value="gndvi">GNDVI</option>
      <option value="msavi">MSAVI</option>
    </select>

    <button type="submit">Get Index Value</button>
  </form>

  {#if error}
    <p class="error">Error: {error}</p>
  {/if}

  {#if result}
    <div class="result">
      <h2>Result:</h2>
      <p>X: {result.x}</p>
      <p>Y: {result.y}</p>
      <p>Index Type: {result.index_type}</p>
      <p>Index Value: {result.index_value}</p>
    </div>
  {/if}
</main>
