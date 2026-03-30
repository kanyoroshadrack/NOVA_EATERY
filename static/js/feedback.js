// feedback.js - Star rating and char counter
document.addEventListener('DOMContentLoaded', () => {
  const stars = document.querySelectorAll('.star');
  const ratingInput = document.getElementById('ratingInput');
  const commentArea = document.getElementById('commentArea');
  const charCount = document.getElementById('charCount');

  let selectedRating = 0;

  stars.forEach((star, i) => {
    star.addEventListener('mouseenter', () => {
      stars.forEach((s, j) => s.classList.toggle('active', j <= i));
    });
    star.addEventListener('mouseleave', () => {
      stars.forEach((s, j) => s.classList.toggle('active', j < selectedRating));
    });
    star.addEventListener('click', () => {
      selectedRating = i + 1;
      if (ratingInput) ratingInput.value = selectedRating;
      stars.forEach((s, j) => s.classList.toggle('active', j < selectedRating));
    });
  });

  commentArea?.addEventListener('input', () => {
    const len = commentArea.value.length;
    if (charCount) charCount.textContent = `${len}/500`;
    if (len > 500) commentArea.value = commentArea.value.slice(0, 500);
  });

  document.getElementById('feedbackForm')?.addEventListener('submit', (e) => {
    if (!selectedRating) {
      e.preventDefault();
      alert('Please select a star rating.');
    }
  });
});
