<!-- <script>
  import FileUpload from './components/FileUpload.svelte';

  // Check authentication on mount

</script>

<main>
  <h1>Analysis</h1>
  <FileUpload/>
</main>

<body>
</body> -->

<script>
  // import { fetchIndexValue, validateToken } from './utils/api.js';
  import FileUpload from './components/FileUpload.svelte';
  import IndexValue from './components/IndexValue.svelte';
  import Map from './components/Map.svelte';
  if (!localStorage.getItem("access_token")) {
    alert("You are not authenticated. Redirecting to login.");
    window.location.href = "#/login"; // Redirect to login page
  }
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
