const locationCards = [...document.querySelectorAll('.landing-location-card')];
const locationSearch = document.getElementById('location-search');
const viewAllLocations = document.getElementById('view-all-locations');
const nearbyButton = document.getElementById('find-nearby');
const locationStatus = document.getElementById('location-status');
let expandedLocations = false;
let nearbyMode = false;

function filterLocations() {
  const query = locationSearch.value.trim().toLocaleLowerCase();
  let visibleCount = 0;
  locationCards.forEach((card, index) => {
    const matches = card.dataset.search.toLocaleLowerCase().includes(query);
    const shown = matches && (!nearbyMode || (card.dataset.latitude && card.dataset.longitude)) && (query || expandedLocations || index < 4);
    card.hidden = !shown;
    if (shown) visibleCount += 1;
  });
  document.getElementById('location-no-results').hidden = visibleCount !== 0 || !query;
  if (viewAllLocations) viewAllLocations.hidden = Boolean(query) || expandedLocations;
}

locationSearch.addEventListener('input', () => {
  nearbyMode = false;
  locationStatus.hidden = true;
  filterLocations();
});
document.querySelector('.landing-search').addEventListener('submit', event => {
  event.preventDefault();
  filterLocations();
  document.getElementById('locations').scrollIntoView({behavior: 'smooth'});
});
viewAllLocations?.addEventListener('click', () => {
  expandedLocations = true;
  filterLocations();
});
nearbyButton?.addEventListener('click', () => {
  if (!navigator.geolocation) {
    locationStatus.textContent = 'Location is not available in this browser.';
    locationStatus.hidden = false;
    return;
  }
  nearbyButton.disabled = true;
  locationStatus.textContent = 'Finding stores near you…';
  locationStatus.hidden = false;
  navigator.geolocation.getCurrentPosition(position => {
    const {latitude, longitude} = position.coords;
    const toRadians = degrees => degrees * Math.PI / 180;
    const distances = locationCards.map(card => {
      const storeLatitude = Number(card.dataset.latitude);
      const storeLongitude = Number(card.dataset.longitude);
      if (!card.dataset.latitude || !card.dataset.longitude) return {card, miles: Infinity};
      const deltaLatitude = toRadians(storeLatitude - latitude);
      const deltaLongitude = toRadians(storeLongitude - longitude);
      const arc = Math.sin(deltaLatitude / 2) ** 2 + Math.cos(toRadians(latitude)) * Math.cos(toRadians(storeLatitude)) * Math.sin(deltaLongitude / 2) ** 2;
      return {card, miles: 3958.8 * 2 * Math.atan2(Math.sqrt(arc), Math.sqrt(1 - arc))};
    }).sort((first, second) => first.miles - second.miles);
    const nearby = distances.filter(item => Number.isFinite(item.miles));
    if (!nearby.length) {
      locationStatus.textContent = 'Store locations are being updated. Try searching by city instead.';
      nearbyButton.disabled = false;
      return;
    }
    const grid = document.getElementById('location-grid');
    distances.forEach(({card, miles}) => {
      grid.append(card);
      const label = card.querySelector('.landing-distance');
      if (Number.isFinite(miles)) {
        label.textContent = `${miles.toFixed(1)} miles away`;
        label.hidden = false;
      }
    });
    locationCards.splice(0, locationCards.length, ...distances.map(item => item.card));
    locationSearch.value = '';
    nearbyMode = true;
    expandedLocations = true;
    filterLocations();
    locationStatus.textContent = `Showing ${nearby.length} stores ordered by distance. Select a store to see its hours.`;
    document.getElementById('locations').scrollIntoView({behavior: 'smooth'});
    nearbyButton.disabled = false;
  }, () => {
    locationStatus.textContent = 'Location access was unavailable. Search by city or store name instead.';
    nearbyButton.disabled = false;
  }, {enableHighAccuracy: false, timeout: 10000, maximumAge: 300000});
});
filterLocations();
