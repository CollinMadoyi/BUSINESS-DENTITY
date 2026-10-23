document.addEventListener('DOMContentLoaded', function () {
  const qrImage = document.querySelector('.qr-image');
  if (qrImage) {
    qrImage.addEventListener('click', () => {
      window.open(qrImage.src, '_blank');
    });
  }
});
