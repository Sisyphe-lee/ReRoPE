const yearEl = document.getElementById('year');
if (yearEl) {
  yearEl.textContent = new Date().getFullYear();
}

// Hero video autoplay with sound
(function() {
  const heroVideo = document.getElementById('heroVideo');
  if (!heroVideo) return;

  const hasSource = Boolean(heroVideo.getAttribute('src')) || Array.from(heroVideo.querySelectorAll('source'))
    .some(source => source.getAttribute('src'));
  if (!hasSource) return;

  // Ensure video is NOT muted and volume is max
  heroVideo.muted = false;
  heroVideo.volume = 1.0;

  const playWithSound = () => {
    heroVideo.muted = false;
    heroVideo.volume = 1.0;
    return heroVideo.play().catch(err => {
      console.log('Autoplay with sound blocked, will play on interaction');
      return Promise.reject(err);
    });
  };

  // Try immediately when script loads
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      playWithSound();
    });
  } else {
    playWithSound();
  }

  // Also try when video is ready
  heroVideo.addEventListener('loadeddata', () => {
    playWithSound();
  });

  heroVideo.addEventListener('canplay', () => {
    playWithSound();
  });

  // Try again after a short delay
  setTimeout(() => {
    playWithSound();
  }, 100);

  // Enable sound on any user interaction
  const enableSoundOnInteraction = () => {
    playWithSound().then(() => {
      document.removeEventListener('click', enableSoundOnInteraction);
      document.removeEventListener('touchstart', enableSoundOnInteraction);
      document.removeEventListener('keydown', enableSoundOnInteraction);
    });
  };

  document.addEventListener('click', enableSoundOnInteraction, { once: true });
  document.addEventListener('touchstart', enableSoundOnInteraction, { once: true });
  document.addEventListener('keydown', enableSoundOnInteraction, { once: true });
})();

// Modal functionality
const modal = document.getElementById('modal');
const modalVideo = document.getElementById('modalVideo');

function openModal(videoSrc) {
  if (!modal || !modalVideo) return;
  modalVideo.src = videoSrc;
  modal.classList.add('is-open');
  modalVideo.play();
}

function closeModal() {
  if (!modal || !modalVideo) return;
  modal.classList.remove('is-open');
  modalVideo.pause();
  modalVideo.src = '';
}

// Close modal when clicking backdrop or close button
if (modal) {
  modal.querySelectorAll('[data-close]').forEach(el => {
    el.addEventListener('click', closeModal);
  });
}

// Close modal with Escape key
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && modal && modal.classList.contains('is-open')) {
    closeModal();
  }
});

// Click on grid videos to open in modal
document.querySelectorAll('.video-item video').forEach(video => {
  const source = video.querySelector('source');
  const srcAttr = video.getAttribute('src') || source?.getAttribute('src');
  if (!srcAttr) return;
  const resolvedSrc = source?.src || video.currentSrc || srcAttr;

  // Force load the video
  video.load();
  
  video.addEventListener('click', function() {
    openModal(resolvedSrc);
  });
  
  // Ensure video plays when loaded
  video.addEventListener('loadeddata', function() {
    const playPromise = this.play();
    if (playPromise !== undefined) {
      playPromise.catch(err => {
        console.log('Autoplay prevented for:', this.querySelector('source')?.src);
        // Video will play on click
      });
    }
  });
  
  // Handle video loading errors
  video.addEventListener('error', function(e) {
    const source = this.querySelector('source');
    console.error('Video failed to load:', source?.src);
    console.error('Error code:', this.error?.code);
    console.error('Error message:', this.error?.message);
    // Show error message on video element
    this.style.border = '2px solid red';
    const label = this.parentElement.querySelector('p');
    if (label) {
      label.textContent += ' (Failed to load - check console)';
      label.style.color = 'red';
    }
  });
  
  // Log when video can play
  video.addEventListener('canplay', function() {
    console.log('Video can play:', this.querySelector('source')?.src);
    // Try to play again when ready
    this.play().catch(() => {});
  });
  
  // Try to play immediately after a short delay
  setTimeout(() => {
    video.play().catch(err => {
      console.log('Initial play failed (will play on click):', video.querySelector('source')?.src);
    });
  }, 100);
});
