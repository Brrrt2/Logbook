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

// last updated func returning last update system time/date
// function updateLastModified() {
//   const now = new Date();
//   const formatted = now.toLocaleString(); // Adjust for your preferred format
//   document.getElementById("lastUpdated").textContent = `Last updated: ${formatted}`;
// }

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

  // Draw the image from the camera onto the canvas
  const ctx = canvas.getContext("2d");
  ctx.drawImage(camera, 0, 0, canvas.width, canvas.height);

  // Convert canvas to base64 string and preview it
  const imageUrl = canvas.toDataURL("image/png");
  previewImage.src = imageUrl;

  // Show the preview modal
  toggleImagePreviewModal();

  // 🔁 Send the base64 image to the Flask backend for OCR
  fetch('/process_receipt', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ image: imageUrl })
  })
  .then(response => response.json())
  .then(data => {
    console.log("OCR Result:", data.ocr_result);
    console.log("Extracted Entities:", data.extracted_entities);

    // 🔧 Optional: Auto-fill form fields with extracted data
    // Example:
    // document.getElementById('dateField').value = data.extracted_entities.date || '';
    // document.getElementById('amountField').value = data.extracted_entities.amount || '';
  })
  .catch(error => {
    console.error("Error sending image to server:", error);
  });
}


// Toggle Image Preview Modal (Show/Hide it)
function toggleImagePreviewModal() {
  const imagePreviewModal = document.getElementById("imagePreviewModal");
  imagePreviewModal.classList.toggle("d-none"); // Toggles visibility
  imagePreviewModal.classList.toggle("show"); // Toggles the 'show' class
}

// Prevent e and other symbols in Amount
document.addEventListener("DOMContentLoaded", function (){
  // prevent other keys being pressed for amount
  const pesosInput = document.getElementById('ocrPesos');
  const centsInput = document.getElementById('ocrCents');
  const taxpesosInput = document.getElementById('ocrTaxPesos');
  // const taxcentsInput = document.getElementById('ocrTaxCents');
  const keyblock = ['e', 'E', '.', '+', '-'];
  
  function preventKeyPressed(event){
    if (keyblock.includes(event.key)) {
  
        event.preventDefault();
    }
  
  }
  
  pesosInput.addEventListener('keydown', preventKeyPressed);
  taxpesosInput.addEventListener('keydown', preventKeyPressed);
  centsInput.addEventListener('keydown', preventKeyPressed);
});

// Function to save OCR data and insert it into the table
function saveOcrData() {
  // Get the input values from the OCR form
  const date = document.getElementById("ocrDate").value;
  const description = document.getElementById("ocrDescription").value;
  const pesos = document.getElementById("ocrPesos").value;
  const cents = document.getElementById("ocrCents").value;
  const invoice = document.getElementById("ocrInvoice").value;
  const vatCompany = document.getElementById("ocrVatCompany").value;
  const taxpesos = document.getElementById("ocrTaxPesos").value;
  const taxcents = document.getElementById("ocrTaxCents").value;
  const vatTin = document.getElementById("ocrTin").value;
  const category = document.getElementById("ocrCategory").value;

  // amount

  if (!cents) {
    document.getElementById("ocrCents").value = "00";
  }
  if (!taxcents) {
    document.getElementById("ocrTaxCents").value = "00";
  }
  
  const amount = `${pesos}.${cents}`
  const inputTax = `${taxpesos}.${taxcents}`

  // Check if any field is empty
  if (!date || !description || !invoice || !pesos || !taxpesos || !vatCompany || !inputTax || !vatTin || !category) {
    alert("Please fill in all fields before saving.");
    return updateLastModified(); // Prevent saving if any field is empty
  }

  // Get the table body element by class or ID
  const tableBody = document.querySelector(".table-layout tbody");

  // Create a new row in the table
  const newRow = tableBody.insertRow();

  // Insert new cells with the OCR data
  newRow.innerHTML = `
      <td><input type="checkbox" id="selectRow1" name="selectRow" class="record-checkbox" /></td>
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
  // document.getElementById("ocrAmount").value = "";
  document.getElementById("ocrPesos").value = "";
  document.getElementById("ocrCents").value = "";
  document.getElementById("ocrInvoice").value = "";
  document.getElementById("ocrVatCompany").value = "";
  // document.getElementById("ocrInputTax").value = "";
  document.getElementById("ocrTaxPesos").value = "";
  document.getElementById("ocrTaxCents").value = "";
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
  document.getElementById("ocrDate").value = cells[1].innerText;
  document.getElementById("ocrDescription").value = cells[2].innerText;
  
  // split amount 
  const amount = cells[3].innerText;
  const [pesos, cents] = amount.split(".")
  document.getElementById("ocrPesos").value = pesos;
  document.getElementById("ocrCents").value = cents || "00";

  document.getElementById("ocrInvoice").value = cells[4].innerText;
  document.getElementById("ocrVatCompany").value = cells[5].innerText;

  // split amount
  const InputTax = cells[6].innerText.trim();
  const [taxpesos, taxcents] = InputTax.split(".")
  document.getElementById("ocrTaxPesos").value = taxpesos;
  document.getElementById("ocrTaxCents").value = taxcents || "00";

  document.getElementById("ocrTin").value = cells[7].innerText;
  document.getElementById("ocrCategory").value = cells[8].innerText;

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
  document.getElementById("editDate").value = cells[1].innerText;
  document.getElementById("editDescription").value = cells[2].innerText;

  // split amount 
  const amount = cells[3].innerText;
  const [pesos, cents] = amount.split(".")
  document.getElementById("editPesos").value = pesos;
  document.getElementById("editCents").value = cents || "00";

  document.getElementById("editInvoice").value = cells[4].innerText;
  document.getElementById("editVatCompany").value = cells[5].innerText;

  const InputTax = cells[6].innerText;
  const [taxpesos, taxcents] = InputTax.split(".")
  document.getElementById("editTaxPesos").value = taxpesos;
  document.getElementById("editTaxCents").value = taxcents || "00";
  
  document.getElementById("editTin").value = cells[7].innerText;
  document.getElementById("editCategory").value = cells[8].innerText;

  // Show edit modal
  document.getElementById("editRecordModal").classList.remove("d-none");
  document.getElementById("editRecordModal").classList.add("show");
}

// Save button inside Edit Modal
function saveEditedRecord(closeAfterSave = false) {
  if (!currentEditingRow) return;

  const cells = currentEditingRow.getElementsByTagName("td");

  // Update cell values
  cells[1].innerText = document.getElementById("editDate").value;
  cells[2].innerText = document.getElementById("editDescription").value;

  const updatedAmount = `${document.getElementById("editPesos").value}.${document.getElementById("editCents").value.padStart(2, '0')}`;
  cells[3].innerText = updatedAmount

  cells[4].innerText = document.getElementById("editInvoice").value;
  cells[5].innerText = document.getElementById("editVatCompany").value;

  const updatedTaxAmount = `${document.getElementById("editTaxPesos").value}.${document.getElementById("editTaxCents").value.padStart(2, '0')}`;
  cells[6].innerText = updatedTaxAmount

  cells[7].innerText = document.getElementById("editTin").value;
  cells[8].innerText = document.getElementById("editCategory").value;

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
    const imageUrl = e.target.result; // base64 string

    // Set image preview
    previewImage.src = imageUrl;

    // Show the modal
    toggleImagePreviewModal();

    // Send image to Flask backend for OCR
    fetch('/process_receipt', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ image: imageUrl })
    })
    .then(response => response.json())
    .then(data => {
      console.log("OCR Result:", data.ocr_result);
      console.log("Extracted Entities:", data.extracted_entities);

      // Optional: Fill form fields with extracted data
      // document.getElementById('dateField').value = data.extracted_entities.date || '';
      // document.getElementById('amountField').value = data.extracted_entities.amount || '';
    })
    .catch(error => {
      console.error("Error sending image to server:", error);
    });
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





// test for export button
function exportTableWithTitle(event) {
  if (event) event.preventDefault();

  // Get the editable title text
  let title = document.querySelector(".title-of-record").innerText.trim() || "Untitled_Record";

  // Sanitize the title to be file-safe
  title = title.replace(/[^a-z0-9_\-]/gi, "_");

  const table = document.querySelector(".table-layout");
  if (!table) {
    alert("No table found to export.");
    return;
  }

  let csvContent = "data:text/csv;charset=utf-8,";
  csvContent += `Title of Record:,"${title}"\r\n\r\n`;

  const rows = table.querySelectorAll("tr");
  rows.forEach((row, rowIndex) => {
    const cells = row.querySelectorAll("th, td");
    const rowData = [];

    // Skip the last column (assumed to be the Action column)
    const cellCount = cells.length > 1 ? cells.length - 1 : cells.length;

    for (let i = 0; i < cellCount; i++) {
      rowData.push('"' + cells[i].innerText.replace(/"/g, '""') + '"');
    }

    csvContent += rowData.join(",") + "\r\n";
  });

  const encodedUri = encodeURI(csvContent);
  const link = document.createElement("a");
  link.setAttribute("href", encodedUri);
  link.setAttribute("download", `${title}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}





