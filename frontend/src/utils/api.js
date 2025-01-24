export const fetchIndexValue = async ({ x, y, indexType }) => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      throw new Error("You are not authenticated. Please log in.");
    }
  
    const response = await fetch("http://localhost:8000/get-index-value/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ x, y, index_type: indexType }),
    });
  
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Failed to fetch index value.");
    }
  
    return response.json();
  };
  
  export const validateToken = () => {
    if (!localStorage.getItem("access_token")) {
      alert("You are not authenticated. Redirecting to login.");
      window.location.href = "/login";
    }
  };  