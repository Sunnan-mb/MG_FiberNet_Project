// Register the PWA service worker where supported.
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => navigator.serviceWorker.register('/static/pwa/service-worker.js').catch(console.error));
}

// Location is collected only after the customer explicitly taps the button.
const locateButton = document.getElementById('locate-btn');
if (locateButton) {
  locateButton.addEventListener('click', () => {
    const status = document.getElementById('location-status');
    if (!navigator.geolocation) { status.textContent = 'Location is not supported by this browser.'; return; }
    status.textContent = 'Requesting location permission…';
    navigator.geolocation.getCurrentPosition((position) => {
      document.getElementById('id_latitude').value = position.coords.latitude;
      document.getElementById('id_longitude').value = position.coords.longitude;
      status.textContent = 'Location added to this complaint.';
    }, () => { status.textContent = 'Location was not shared. You can enter the address manually.'; }, { enableHighAccuracy: true, timeout: 10000 });
  });
}
