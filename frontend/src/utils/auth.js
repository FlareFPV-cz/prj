import { writable } from "svelte/store";

export const isAuthenticated = writable(false);

export async function checkAuth(redirect = true) {
    try {
        const response = await fetch("http://localhost:8000/validate-token", {
            method: "POST",
            credentials: "include",  // 🔥 Ensures cookies are sent
        });

        if (!response.ok) {
            throw new Error("Unauthorized");
        }

        isAuthenticated.set(true);
        return true;
    } catch (error) {
        isAuthenticated.set(false);
        if (redirect) {
            setTimeout(() => window.location.href = "/login", 2000); // Redirect
        }
        return false;
    }
}

export async function logout() {
    try {
        await fetch("http://localhost:8000/logout", {
            method: "POST",
            credentials: "include",
        });

        isAuthenticated.set(false);
        window.location.href = "/login";  // Redirect to login page
    } catch (error) {
        console.error("Logout failed:", error);
    }
}
