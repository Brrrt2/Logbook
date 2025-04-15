const video = document.getElementById("camera");
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");
const captureBtn = document.getElementById("capture-btn");
const fileInput = document.getElementById("file-input");
const uploadBtn = document.getElementById("upload-btn");
const capturedImg = document.getElementById("captured-img");
const ocrText = document.getElementById("ocr-text");
const extractedDataSection = document.getElementById("extracted-data");

// Access live camera feed
navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        video.srcObject = stream;
    })
    .catch(error => console.error("Error accessing camera:", error));

// Capture image from live camera
captureBtn.addEventListener("click", () => {
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob(blob => {
        uploadImage(blob);
    }, "image/jpeg");
});

// Upload selected file
uploadBtn.addEventListener("click", () => {
    if (fileInput.files.length > 0) {
        let file = fileInput.files[0];
        let formData = new FormData();
        formData.append("image", file);
        uploadToServer(formData);
    }
});

// Function to upload image blob
function uploadImage(blob) {
    let formData = new FormData();
    formData.append("image", blob, "captured.jpg");
    uploadToServer(formData);
}

// Function to send image to server and get OCR result
function uploadToServer(formData) {
    fetch("/upload", { method: "POST", body: formData })
        .then(response => response.json())
        .then(data => {
            capturedImg.src = data.processed_image;
            displayStructuredText(data.ocr_result);
            displayExtractedEntities(data.extracted_entities);
        })
        .catch(error => console.error("Error:", error));
}

// Display structured OCR text
function displayStructuredText(textArray) {
    ocrText.innerHTML = "";
    textArray.forEach(line => {
        let p = document.createElement("p");
        p.textContent = line;
        ocrText.appendChild(p);
    });
}

// Display extracted entities in a table
function displayExtractedEntities(entities) {
    extractedDataSection.innerHTML = `
        <h3>Extracted Data:</h3>
        <table>
            <tr>
                <th>Entity</th>
                <th>Value</th>
            </tr>
        </table>
    `;
    const table = extractedDataSection.querySelector("table");

    entities.forEach(entity => {
        let row = document.createElement("tr");
        let entityCell = document.createElement("td");
        let valueCell = document.createElement("td");

        entityCell.textContent = entity.Entity;
        valueCell.textContent = entity.Value;

        row.appendChild(entityCell);
        row.appendChild(valueCell);
        table.appendChild(row);
    });
}
