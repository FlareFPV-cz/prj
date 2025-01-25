<script>
    import { writable } from "svelte/store";
    import JSEncrypt from "jsencrypt";

    let publicKey = null; // Store public key
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

    async function fetchPublicKey() {
        try {
            const response = await fetch(`${API_URL}/public-key`);
            const data = await response.json();
            publicKey = data.public_key;
        } catch (e) {
            console.error("Failed to fetch public key:", e);
        }
    }

    async function signup() {
        if (!publicKey) {
            await fetchPublicKey();
        }

        const encrypt = new JSEncrypt();
        encrypt.setPublicKey(publicKey);
        const encryptedPassword = encrypt.encrypt(password);

        const response = await fetch(`${API_URL}/signup`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password: encryptedPassword, email, full_name }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            error = errorData.detail || "Signup failed";
            return;
        }

        console.log("Signup successful!");
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

    <button class="toggle" on:click={toggleForm} type="button">
        {isSignup ? "Already have an account? Login here." : "Don't have an account? Sign up here."}
    </button>
</form>
