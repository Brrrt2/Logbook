const sidebar = document.getElementById("sidebar");
const toggleBtn = document.getElementById("toggleBtn");
const overlay = document.getElementById("overlay");

function toggleSidebar() {
  sidebar.classList.toggle("active");
  overlay.classList.toggle("active");
}

toggleBtn.addEventListener("click", toggleSidebar);

// Clicking outside or on sidebar link closes it
overlay.addEventListener("click", toggleSidebar);

sidebar.querySelectorAll("a").forEach(link => {
  link.addEventListener("click", toggleSidebar);
});
