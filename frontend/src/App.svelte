<script>
  import { onMount } from 'svelte';
  import { writable } from 'svelte/store';
  import Router from "svelte-spa-router";
  import routes from "./routes";

  let isAuthenticated = writable(false);

  async function checkAuth() {
        try {
            const response = await fetch(`http://localhost:8000/validate-token`, {
                method: "POST",
                credentials: "include",  // cookies
            });

            if (!response.ok) {
                console.error("User is not authenticated.");
                return false;
            }

            const data = await response.json();
            console.log("User is authenticated:", data);
            return true;
        } catch (e) {
            console.error("Error checking authentication:", e);
            return false;
        }
    }


  async function logout() {
    try {
        await fetch("http://localhost:8000/logout", {
            method: "POST",
            credentials: "include", // cookies
        });

        isAuthenticated.set(false);
        window.location.href = "#/";
    } catch (error) {
        console.error("Logout failed:", error);
    }
  }


  onMount(async () => {
    isAuthenticated.set(await checkAuth()); // ✅ Wait for checkAuth() to complete
  });
</script>

<style>
  /* Navbar Styling */
  nav {
    background-color: #333;
    color: white;
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
    padding: 1em 2em;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    position: sticky;
    top: 0;
    z-index: 1000;
    border-radius: 5px;
  }

  .brand {
    font-size: 1.5em;
    font-weight: bold;
    flex-shrink: 0;
  }

  .nav-links {
    display: flex;
    gap: 1em;
  }

  nav a, nav button {
    color: white;
    text-decoration: none;
    font-weight: bold;
    padding: 0.5em 1em;
    border-radius: 5px;
    transition: background-color 0.3s ease;
    background: none;
    border: none;
    cursor: pointer;
  }

  nav a:hover, nav button:hover {
    background-color: #555;
  }

  /* Main Content Styling */
  main {
    padding: 2em;
    font-family: Arial, sans-serif;
    text-align: center;
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
    {#if $isAuthenticated}
      <a href="/">Home</a>
      <a href="#/analysis">Analysis</a>
      <a href="#/soil">Soil Map</a>
      <a href="#/pred">Pred</a>
      <button on:click={logout}>Logout</button>
    {:else}
      <a href="#/login">Login</a>
    {/if}
  </div>
</nav>

<main style="display: flex; flex-direction: column;">
  <Router {routes} />
</main>

<footer>
  <p>&copy; 2025 FLARE PRJ. Built with ❤️ by the Flare FPV team. <a href="https://github.com/Jankozeluh/prj">GitHub</a></p>
</footer>
