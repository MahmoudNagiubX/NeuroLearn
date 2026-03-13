import { API_BASE_URL } from "../constants/config";

function buildUrl(path, query) {
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  const url = new URL(`${API_BASE_URL}${normalizedPath}`);

  if (query) {
    Object.entries(query).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== "") {
        url.searchParams.set(key, String(value));
      }
    });
  }

  return url.toString();
}

export async function apiRequest(path, { method = "GET", token, body, query } = {}) {
  const url = buildUrl(path, query);
  let response;
  try {
    response = await fetch(url, {
      method,
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
  } catch (error) {
    throw new Error(`Could not reach backend API at ${API_BASE_URL}. Check that backend is running and VITE_API_BASE_URL is correct.`);
  }

  const contentType = response.headers.get("content-type") || "";
  const isJson = contentType.includes("application/json");
  const payload = isJson ? await response.json() : null;
  const textPayload = !isJson ? await response.text() : "";

  if (!response.ok) {
    const detail = payload?.detail;
    let message = `Request failed with status ${response.status}`;

    if (typeof detail === "string") {
      message = detail;
    } else if (Array.isArray(detail)) {
      message = detail
        .map((issue) => issue?.msg || "Validation error")
        .filter(Boolean)
        .join("; ");
    } else if (detail && typeof detail === "object") {
      message = detail.message || JSON.stringify(detail);
    } else if (typeof textPayload === "string" && textPayload.trim()) {
      message = textPayload.trim();
    }

    throw new Error(message);
  }

  return payload;
}
