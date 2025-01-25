<script>
    import { writable } from "svelte/store";

    let username = "";
    let password = "";
    let email = "";
    let full_name = "";
    let error = "";
    let isSignup = false;

    let isAuthenticated = writable(false);

    const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

    async function login() {
        error = "";
        try {
            const response = await fetch(`${API_URL}/login`, {
                method: "POST",
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
                credentials: "include", //Required for secure cookies
                body: new URLSearchParams({ username, password }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                error = escapeHTML(errorData.detail) || "Login failed";
                return;
            }

            console.log("Login successful! Checking auth...");
            await checkAuth();
            
            window.location.href = "#/";
            location.reload();
        } catch (e) {
            error = "An error occurred. Please try again.";
        }
    }

    async function checkAuth() {
        try {
            const response = await fetch(`${API_URL}/validate-token`, {
                method: "POST",
                credentials: "include", 
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


    async function signup() {
        error = "";

        if (password.length < 8 || !/\d/.test(password)) {
            error = "Password must be at least 8 characters long and include a number.";
            return;
        }

        try {
            const response = await fetch(`${API_URL}/signup`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ 
                    username, 
                    password, 
                    email, 
                    full_name 
                }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                error = escapeHTML(errorData.detail) || "Signup failed";
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

    function escapeHTML(str) {
        return str.replace(/[&<>"']/g, match => ({
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#039;"
        }[match]));
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
