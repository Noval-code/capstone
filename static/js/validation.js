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
