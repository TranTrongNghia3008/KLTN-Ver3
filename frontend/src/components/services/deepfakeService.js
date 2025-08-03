import apiClient from "./apiClient";

export async function checkDeepfake(videoFile) {
  const formData = new FormData();
  formData.append("video", videoFile);

  return await apiClient("/deepfake/", {
    method: "POST",
    body: formData,
  });
}
