<script>
  import Router from "svelte-spa-router";
  import routes from "./routes";
  import { onMount } from 'svelte';
  let isAuthenticated = false;

  function checkAuth() {
    const token = localStorage.getItem('access_token');
    isAuthenticated = !!token; // Check if token exists
  }

  function logout() {
    localStorage.removeItem('access_token');
    isAuthenticated = false;
    window.location.href = "#/"; 
  }

  onMount(() => {
    checkAuth(); // Check authentication on load
  });
</script>


<style>
  /* Navbar Styling */
  nav {
    background-color: #333;
    color: white;
    display: flex;
    justify-content: space-between; /* Separates left and right parts */
    align-items: center;
    width: 100%; /* Stretch to full width */
    padding: 1em 2em;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1); /* Optional shadow for better appearance */
    position: sticky; /* Makes the navbar sticky at the top */
    top: 0;
    z-index: 1000; /* Ensures it stays above other content */
  }

  .brand {
    font-size: 1.5em;
    font-weight: bold;
    flex-shrink: 0; /* Prevents the brand from shrinking */
  }

  .nav-links {
    display: flex;
    gap: 1em;
  }

  nav a {
    color: white;
    text-decoration: none;
    font-weight: bold;
    padding: 0.5em 1em;
    border-radius: 5px;
    transition: background-color 0.3s ease;
  }

  nav a:hover {
    background-color: #555;
  }

  /* Main Content Styling */
  main {
    padding: 2em;
    font-family: Arial, sans-serif;
    text-align: center;
  }

  h1 {
    font-size: 3em;
    color: #333;
    margin-bottom: 0.5em;
  }

  p {
    font-size: 1.2em;
    color: #555;
    line-height: 1.6;
  }

  footer {
    text-align: center;
    padding: 1rem;
    color: #b0b0b0;
  }

  footer a {
    color: #f0b429;
    text-decoration: none;
  }
    
</style>

<nav>
  <div class="brand">FLARE PRJ</div>
  <div class="nav-links">
    {#if isAuthenticated}
      <a href="/">Home</a>
      <a href="#/analysis">Analysis</a>
      <a href="#/soil">Soil Map</a>
      <button on:click={logout}>Logout</button>
    {:else}
      <a href="#/login">Login</a>
      <!-- <a href="#/signup">Signup</a> -->
    {/if}
  </div>
</nav>

<main>
  <Router {routes} />
</main>

<footer>
  <p>&copy; 2025 FLARE PRJ. Built with ❤️ by the Flare FPV team. <a href="https://github.com/Jankozeluh/prj">GitHub</a></p>
</footer>
