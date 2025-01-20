<script>
    import { writable } from "svelte/store";

    export let token = writable("");

    let username = "";
    let password = "";
    let email = "";
    let full_name = "";
    let error = "";
    let isSignup = false;

    async function login() {
        error = "";
        try {
            const response = await fetch("http://127.0.0.1:8000/login", {
                method: "POST",
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
                body: new URLSearchParams({ username, password }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                error = errorData.detail || "Login failed";
                return;
            }

            const data = await response.json();
            token.set(data.access_token);
            localStorage.setItem("access_token", data.access_token);
            window.location.href = "#/";
            location.reload();
        } catch (e) {
            error = "An error occurred. Please try again.";
        }
    }

    async function signup() {
        error = "";
        try {
            const response = await fetch("http://127.0.0.1:8000/signup", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password, email, full_name }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                error = errorData.detail || "Signup failed";
                return;
            }

            username = password = email = full_name = "";
            error = "Signup successful! You can now log in.";
            isSignup = false;
        } catch (e) {
            error = "An error occurred. Please try again.";
        }
    }

    function toggleForm() {
        error = "";
        isSignup = !isSignup;
    }
</script>

<head>
    <link rel="stylesheet" href="../css/login.css">
  </head>

<form on:submit|preventDefault={isSignup ? signup : login}>
    <h2>{isSignup ? "Sign Up" : "Login"}</h2>

    <input type="text" placeholder="Username" bind:value={username} required />
    <input type="password" placeholder="Password" bind:value={password} required />

    {#if isSignup}
        <input type="email" placeholder="Email" bind:value={email} required />
        <input type="text" placeholder="Full Name" bind:value={full_name} required />
    {/if}

    <button type="submit">{isSignup ? "Sign Up" : "Login"}</button>

    {#if error}
        <p class="error">{error}</p>
    {/if}

    <p class="toggle" on:click={toggleForm}>
        {isSignup ? "Already have an account? Login here." : "Don't have an account? Sign up here."}
    </p>
</form>
