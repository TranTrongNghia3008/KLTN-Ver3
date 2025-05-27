import apiClient from "./apiClient";

export async function registerUser(userData) {
  try {
    return await apiClient("/auth/register", {
    method: "POST",
    body: userData,
  });
  } catch (error) {
    console.error("Register error:", error);
    // Ném lại lỗi có chi tiết cụ thể để UI xử lý
    if (error.message) {
      throw new Error(error.message);
    }
    throw new Error("Register failed");
  }
}

export async function loginUser(credentials) {
  try {
    return await apiClient("/auth/login", {
      method: "POST",
      body: credentials,
    });
  } catch (error) {
    console.error("Login error:", error);
    // Ném lại lỗi có chi tiết cụ thể để UI xử lý
    if (error.message) {
      throw new Error(error.message);
    }
    throw new Error("Login failed");
  }
}
