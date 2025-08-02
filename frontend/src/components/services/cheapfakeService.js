import apiClient from "./apiClient";

export async function checkCheapfake(image, caption) {
  const formData = new FormData();
  formData.append("image", image);
  formData.append("caption", caption);

  return await apiClient("/cheapfake/", {
    method: "POST",
    body: formData,
  });
}
