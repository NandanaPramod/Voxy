export const USE_MOCK = false;

export const BACKEND_URL = "http://127.0.0.1:8000/analyze";

export async function analyzeAudio(file) {

  if (!file) {
    throw new Error("No audio file provided.");
  }

  const formData = new FormData();

  formData.append("file", file);

  console.log("Sending file to backend:", file.name);

  const response = await fetch(BACKEND_URL, {
    method: "POST",
    body: formData,
  });

  console.log("Backend response status:", response.status);

  if (!response.ok) {
    const errorText = await response.text();

    throw new Error(
      "Backend error: " +
      response.status +
      " - " +
      errorText
    );
  }

  return response.json();
}