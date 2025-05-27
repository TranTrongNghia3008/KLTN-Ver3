// src/services/apiClient.js
const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function apiClient(path, { method = "GET", body, headers = {}, raw = false, ...customConfig } = {}) {
  const token = localStorage.getItem("token");
  const isFormData = body instanceof FormData;

  const config = {
    method,
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(isFormData ? {} : { "Content-Type": "application/json" }),
      ...headers,
    },
    ...customConfig,
  };

  if (body && method !== "GET" && method !== "HEAD") {
    config.body = isFormData ? body : JSON.stringify(body);
  }

  try {
    const response = await fetch(`${BASE_URL}${path}`, config);

    if (!response.ok) {
      if (raw) {
        throw new Error(`Failed to fetch file (${response.status})`);
      } else {
        const errorBody = await response.json();
        console.error("API error:", errorBody);
        throw new Error(errorBody.detail || "API error");
      }
    }

    if (response.status === 204) return null;

    // ✅ Nếu raw = true, trả về blob (file)
    return raw ? await response.blob() : await response.json();
  } catch (error) {
    console.error("API call error:", error);
    throw error;
  }
}

export default apiClient;
