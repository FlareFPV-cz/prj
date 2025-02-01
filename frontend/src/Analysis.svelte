<script>
  import { onMount } from "svelte";
  import FileUpload from './components/FileUpload.svelte';
  import Map from './components/Map.svelte';
  import { checkAuth } from "./utils/auth";

  onMount(async () => {
      const auth = await checkAuth();
      if (!auth) return; // Stop execution if not authenticated
  });
</script>

<main class="analysis-dashboard">
  <h1>Soil Health Analysis Dashboard</h1>

  <div class="analysis-grid">
    <!-- File Upload Section -->
    <section class="analysis-section file-upload-section">
      <FileUpload />
    </section>

    <!-- Map Section with Integrated Index Values -->
    <section class="analysis-section map-section">
      <Map />
    </section>
  </div>
</main>

<style>
  .map-section {
    grid-column: span 2;
  }
</style>
