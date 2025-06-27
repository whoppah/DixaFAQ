// src/lib/axios.js
import axios from "axios";
import Cookies from "js-cookie";

const instance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "",
  withCredentials: false,
});

instance.interceptors.request.use((config) => {
  const csrfToken = Cookies.get("csrftoken");

  const safeMethods = ["post", "put", "patch", "delete"];
  if (csrfToken && safeMethods.includes(config.method?.toLowerCase())) {
    config.headers["X-CSRFToken"] = csrfToken;
  }

  return config;
});

export default instance;

