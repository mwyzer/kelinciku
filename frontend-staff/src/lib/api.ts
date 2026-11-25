export const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";

export async function fetchWithAuth(endpoint: string, userEmail: string = "muhammad.wyzer@gmail.com", options: RequestInit = {}) {
  const headers = {
    "Content-Type": "application/json",
    "X-User-Email": userEmail,
    ...(options.headers || {})
  };

  const res = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers
  });

  if (!res.ok) {
    throw new Error(`API Error: ${res.status} ${res.statusText}`);
  }
  return res.json();
}
