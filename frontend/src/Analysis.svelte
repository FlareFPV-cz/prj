<script>
  import { onMount } from "svelte";
  import FileUpload from './components/FileUpload.svelte';
  import IndexValue from './components/IndexValue.svelte';
  import Map from './components/Map.svelte';
  import { checkAuth } from "./utils/auth";

  onMount(async () => {
      const auth = await checkAuth();
      if (!auth) return; // Stop execution if not authenticated
  });
</script>

<main>
  <h1>Analysis Dashboard</h1>

  <!-- File Upload Section -->
  <section>
    <FileUpload />
  </section>

  <hr>
  
  <section>
    <IndexValue />
  </section>

  <hr>

  <section>
    <Map />
  </section>
</main>
