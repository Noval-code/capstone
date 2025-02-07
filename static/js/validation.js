// pesan dari sweet alert dengan menerima flash message
document.addEventListener("DOMContentLoaded", function () {
  // Ambil pesan dari elemen data di HTML
  const messages = JSON.parse(document.getElementById("flash-messages").textContent);

  // Tampilkan pesan menggunakan SweetAlert
  messages.forEach((message) => {
    Swal.fire({
      title: message.category === "success" ? "Success" : "Error",
      text: message.text,
      icon: message.category,
      confirmButtonText: "OK",
    });
  });
});
// togglePassword.js
document.getElementById("togglePassword").addEventListener("click", function () {
  const passwordInput = document.getElementById("password");
  const eyeOpen = document.getElementById("eyeOpen");
  const eyeClosed = document.getElementById("eyeClosed");

  if (passwordInput.type === "password") {
    passwordInput.type = "text";
    eyeOpen.classList.add("hidden");
    eyeClosed.classList.remove("hidden");
  } else {
    passwordInput.type = "password";
    eyeOpen.classList.remove("hidden");
    eyeClosed.classList.add("hidden");
  }
});
