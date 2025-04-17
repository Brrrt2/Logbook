// Existing functions for menu and modal toggling
function toggleMenu() {
  const drawer = document.getElementById("menuDrawer");
  const overlay = document.getElementById("overlay");
  drawer.classList.toggle("open");
  overlay.classList.toggle("d-none");
}

function toggleRecordModal() {
  const modal = document.getElementById("recordModal");
  const camera = document.getElementById("camera");
  const cover = document.getElementById("cameraCover");
  const captureBtn = document.getElementById("captureBtn");
  const snapshotResult = document.getElementById("snapshotResult");

  modal.classList.toggle("d-none");
  modal.classList.toggle("show");

  // Reset the camera and form when closing the modal
  if (!modal.classList.contains("show")) {
    let stream = camera.srcObject;
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
    }
    camera.srcObject = null;
    cover.style.display = "flex"; // reset cover for next time
    captureBtn.classList.add("d-none");
    snapshotResult.innerHTML = "";
  }
}

// Start the camera when the modal is shown
function startCamera() {
  const camera = document.getElementById("camera");
  const cover = document.getElementById("cameraCover");
  const captureBtn = document.getElementById("captureBtn");

  navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
      camera.srcObject = stream;
      cover.style.display = "none";
      captureBtn.classList.remove("d-none");
    })
    .catch(err => {
      console.error("Camera access denied:", err);
    });
}

// Capture Image Function (Existing)
function captureImage() {
  const camera = document.getElementById("camera");
  const previewImage = document.getElementById("previewImage");

  // Create a temporary canvas to capture the image from the camera
  const canvas = document.createElement("canvas");
  canvas.width = camera.videoWidth;
  canvas.height = camera.videoHeight;

  // Get the 2d context and draw the image from the camera onto the canvas
  const ctx = canvas.getContext("2d");
  ctx.drawImage(camera, 0, 0, canvas.width, canvas.height);

  // Convert canvas to data URL and set it as the source of the preview image
  const imageUrl = canvas.toDataURL("image/png");
  previewImage.src = imageUrl;

  // Toggle the image preview modal to show it above the camera modal
  toggleImagePreviewModal();
}

// Toggle Image Preview Modal (Show/Hide it)
function toggleImagePreviewModal() {
  const imagePreviewModal = document.getElementById("imagePreviewModal");
  imagePreviewModal.classList.toggle("d-none"); // Toggles visibility
  imagePreviewModal.classList.toggle("show"); // Toggles the 'show' class
}

// Function to save OCR data and insert it into the table
function saveOcrData() {
  // Get the input values from the OCR form
  const date = document.getElementById("ocrDate").value;
  const description = document.getElementById("ocrDescription").value;
  const amount = document.getElementById("ocrAmount").value;
  const invoice = document.getElementById("ocrInvoice").value;
  const vatCompany = document.getElementById("ocrVatCompany").value;
  const inputTax = document.getElementById("ocrInputTax").value;
  const vatTin = document.getElementById("ocrTin").value;
  const category = document.getElementById("ocrCategory").value;

  // Check if any field is empty
  if (!date || !description || !amount || !invoice || !vatCompany || !inputTax || !vatTin || !category) {
    alert("Please fill in all fields before saving.");
    return; // Prevent saving if any field is empty
  }

  // Get the table body element by class or ID
  const tableBody = document.querySelector(".table-layout tbody");

  // Create a new row in the table
  const newRow = tableBody.insertRow();

  // Insert new cells with the OCR data
  newRow.innerHTML = `
      <td>${date}</td>
      <td>${description}</td>
      <td>${amount}</td>
      <td>${invoice}</td>
      <td>${vatCompany}</td>
      <td>${inputTax}</td>
      <td>${vatTin}</td>
      <td>${category}</td>
      <td>
          <button class="btn btn-warning btn-sm" onclick="editRow(this)">Edit</button>
          <button class="btn btn-danger btn-sm" onclick="deleteRow(this)">Delete</button>
      </td>
  `;

  // Clear the form fields after saving the data for the next entry
  document.getElementById("ocrDate").value = "";
  document.getElementById("ocrDescription").value = "";
  document.getElementById("ocrAmount").value = "";
  document.getElementById("ocrInvoice").value = "";
  document.getElementById("ocrVatCompany").value = "";
  document.getElementById("ocrInputTax").value = "";
  document.getElementById("ocrTin").value = "";
  document.getElementById("ocrCategory").value = "";

  // Close both modals after saving the data
  toggleRecordModal();
  toggleImagePreviewModal(); // <- This is the added line to close image modal too
}

// Function to edit a row
function editRow(button) {
  const row = button.closest("tr");
  const cells = row.getElementsByTagName("td");

  // Fill the modal fields with the current row data
  document.getElementById("ocrDate").value = cells[0].innerText;
  document.getElementById("ocrDescription").value = cells[1].innerText;
  document.getElementById("ocrAmount").value = cells[2].innerText;
  document.getElementById("ocrInvoice").value = cells[3].innerText;
  document.getElementById("ocrVatCompany").value = cells[4].innerText;
  document.getElementById("ocrInputTax").value = cells[5].innerText;
  document.getElementById("ocrTin").value = cells[6].innerText;
  document.getElementById("ocrCategory").value = cells[7].innerText;

  // Remove the row to allow saving updated data
  row.remove();
}

// Function to delete a row
function deleteRow(button) {
  const row = button.closest("tr");
  row.remove();
}


// Add event listener to the save button in the modal
document.querySelector(".btn-primary").addEventListener("click", saveOcrData);

let currentEditingRow = null;

// Called when Edit button is clicked
function editRow(button) {
  const row = button.closest("tr");
  const cells = row.getElementsByTagName("td");

  // Store reference for saving later
  currentEditingRow = row;

  // Fill the edit modal with current row values
  document.getElementById("editDate").value = cells[0].innerText;
  document.getElementById("editDescription").value = cells[1].innerText;
  document.getElementById("editAmount").value = cells[2].innerText;
  document.getElementById("editInvoice").value = cells[3].innerText;
  document.getElementById("editVatCompany").value = cells[4].innerText;
  document.getElementById("editInputTax").value = cells[5].innerText;
  document.getElementById("editTin").value = cells[6].innerText;
  document.getElementById("editCategory").value = cells[7].innerText;

  // Show edit modal
  document.getElementById("editRecordModal").classList.remove("d-none");
  document.getElementById("editRecordModal").classList.add("show");
}

// Save button inside Edit Modal
function saveEditedRecord(closeAfterSave = false) {
  if (!currentEditingRow) return;

  const cells = currentEditingRow.getElementsByTagName("td");

  // Update cell values
  cells[0].innerText = document.getElementById("editDate").value;
  cells[1].innerText = document.getElementById("editDescription").value;
  cells[2].innerText = document.getElementById("editAmount").value;
  cells[3].innerText = document.getElementById("editInvoice").value;
  cells[4].innerText = document.getElementById("editVatCompany").value;
  cells[5].innerText = document.getElementById("editInputTax").value;
  cells[6].innerText = document.getElementById("editTin").value;
  cells[7].innerText = document.getElementById("editCategory").value;

  if (closeAfterSave) {
    hideEditModal();
    hideConfirmClose();
  } else {
    hideEditModal();
  }

  currentEditingRow = null;
}

// Close edit modal
function hideEditModal() {
  document.getElementById("editRecordModal").classList.add("d-none");
  document.getElementById("editRecordModal").classList.remove("show");
}

// Show confirm close dialog
function showCloseConfirm() {
  document.getElementById("confirmCloseModal").classList.remove("d-none");
  document.getElementById("confirmCloseModal").classList.add("show");
}

// Hide confirm close
function hideConfirmClose() {
  document.getElementById("confirmCloseModal").classList.add("d-none");
  document.getElementById("confirmCloseModal").classList.remove("show");
}

// Close without saving
function closeWithoutSaving() {
  hideConfirmClose();
  hideEditModal();
  currentEditingRow = null;
}

// Function to preview the uploaded image
function previewImage(event) {
  const file = event.target.files[0];
  const reader = new FileReader();

  reader.onload = function(e) {
    const previewImage = document.getElementById('previewImage');
    previewImage.src = e.target.result;

    // Show the modal once the image is selected
    toggleImagePreviewModal();
  };

  if (file) {
    reader.readAsDataURL(file);
  }
}

// Function to toggle the modal visibility
function toggleImagePreviewModal() {
  const modal = document.getElementById('imagePreviewModal');
  modal.classList.toggle('d-none');
  
}

