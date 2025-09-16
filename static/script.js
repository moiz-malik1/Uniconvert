const dropArea = document.getElementById("drop-area");
const fileInput = document.getElementById("fileElem");
const filePreview = document.getElementById("file-preview");
const formatSelect = document.getElementById("format");
const progressContainer = document.getElementById("progress-container");
const progressBar = document.getElementById("progress-bar");
const progressText = document.getElementById("progress-text");
const downloadLink = document.getElementById("download-link");

// ---- Drag & Drop ----
dropArea.addEventListener("dragover", (e) => {
  e.preventDefault();
  dropArea.classList.add("highlight");
});

dropArea.addEventListener("dragleave", () => {
  dropArea.classList.remove("highlight");
});

dropArea.addEventListener("drop", (e) => {
  e.preventDefault();
  dropArea.classList.remove("highlight");
  fileInput.files = e.dataTransfer.files;
  showFilePreview(fileInput.files[0]);
  uploadFile(fileInput.files[0]);
});

// ---- File Input ----
fileInput.addEventListener("change", () => {
  if (fileInput.files.length > 0) {
    showFilePreview(fileInput.files[0]);
    uploadFile(fileInput.files[0]);
  }
});

// ---- Show File Preview ----
function showFilePreview(file) {
  if (!file) return;
  const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
  filePreview.innerHTML = `📄 <b>${file.name}</b> (${sizeMB} MB)`;
  filePreview.classList.remove("hidden");
}

// ---- Upload + Convert ----
function uploadFile(file) {
  if (!file) return;

  const formData = new FormData();
  formData.append("file", file);
  formData.append("format", formatSelect.value);

  progressContainer.classList.remove("hidden");
  progressBar.style.width = "0%";
  progressText.textContent = "Uploading...";

  fetch("/", {
    method: "POST",
    body: formData,
  })
    .then((res) => {
      if (!res.ok) throw new Error("Conversion failed");
      return res.blob();
    })
    .then((blob) => {
      const url = window.URL.createObjectURL(blob);
      downloadLink.href = url;
      downloadLink.download = file.name.replace(/\.[^/.]+$/, "") + "." + formatSelect.value;
      downloadLink.classList.remove("hidden");

      progressBar.style.width = "100%";
      progressText.textContent = "Done!";
    })
    .catch((err) => {
      progressText.textContent = "Error: " + err.message;
    });
}