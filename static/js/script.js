document.addEventListener("DOMContentLoaded", function () {
  // Trigger fade-in
  document.body.classList.add('transition-enabled');

  // Transition links
  const links = document.querySelectorAll('.transition-link');
  links.forEach(link => {
    link.addEventListener('click', function (e) {
      e.preventDefault();
      const url = this.href;
      document.body.classList.add('fade-slide-out');

      setTimeout(() => {
        window.location.href = url;
      }, 600); 
    });
  });
});
