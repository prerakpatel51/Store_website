import * as maplibregl from 'https://unpkg.com/maplibre-gl@6.16.0/dist/maplibre-gl.mjs';

const storeMapElement = document.getElementById('store-map');
const storeMapData = document.getElementById('store-map-data');
const storePicker = document.getElementById('map-store-picker');

if (storeMapElement && storeMapData) {
  const stores = JSON.parse(storeMapData.textContent);
  if (!stores.length) {
    storeMapElement.textContent = 'Store map locations are being updated.';
  } else {
    storeMapElement.textContent = '';
    const firstStore = stores[0];
    const map = new maplibregl.Map({
      container: storeMapElement,
      style: 'https://tiles.openfreemap.org/styles/positron',
      center: [firstStore.longitude, firstStore.latitude],
      zoom: 11,
      scrollZoom: false,
    });
    map.addControl(new maplibregl.NavigationControl({showCompass: false}), 'top-left');
    const focusStores = stores.slice(0, storeMapElement.clientWidth < 600 ? 2 : 4);
    const focusBounds = new maplibregl.LngLatBounds();
    focusStores.forEach(store => focusBounds.extend([store.longitude, store.latitude]));
    map.fitBounds(focusBounds, {padding: 65, maxZoom: 12.5, duration: 0});

    // Stores sharing one address share one pin, with links to both pages.
    const locations = new Map();
    stores.forEach(store => {
      const key = `${store.longitude},${store.latitude}`;
      if (!locations.has(key)) locations.set(key, []);
      locations.get(key).push(store);
    });

    const markerByStore = new Map();
    locations.forEach(locationStores => {
      const firstStore = locationStores[0];
      const popup = document.createElement('div');
      popup.className = 'store-map-popup';
      locationStores.forEach(store => {
        const item = document.createElement('div');
        const link = document.createElement('a');
        link.href = store.url;
        link.textContent = `Store ${store.number} · ${store.name}`;
        item.append(link);
        if (store.address) {
          const address = document.createElement('span');
          address.textContent = store.address;
          item.append(address);
        }
        if (store.hours) {
          const hours = document.createElement('small');
          hours.textContent = `Today: ${store.hours}`;
          item.append(hours);
        }
        popup.append(item);
      });

      const markerButton = document.createElement('button');
      markerButton.type = 'button';
      markerButton.className = 'store-map-name-pin';
      const markerLabel = document.createElement('span');
      markerLabel.className = 'store-map-name-pin-label';
      markerLabel.textContent = locationStores.map(store => store.name).join(' + ');
      markerButton.append(markerLabel);
      markerButton.setAttribute('aria-label', `Show ${locationStores.map(store => store.name).join(' and ')} on the map`);
      const marker = new maplibregl.Marker({element: markerButton, anchor: 'bottom'})
        .setLngLat([firstStore.longitude, firstStore.latitude])
        .setPopup(new maplibregl.Popup({offset: 16}).setDOMContent(popup))
        .addTo(map);
      locationStores.forEach(store => markerByStore.set(String(store.number), marker));
    });

    if (storePicker) {
      stores.forEach(store => {
        const option = document.createElement('option');
        option.value = String(store.number);
        option.textContent = store.name;
        storePicker.append(option);
      });
      storePicker.addEventListener('change', () => {
        const store = stores.find(item => String(item.number) === storePicker.value);
        if (!store) return;
        map.flyTo({center: [store.longitude, store.latitude], zoom: 14, essential: true});
        const marker = markerByStore.get(String(store.number));
        if (marker && !marker.getPopup().isOpen()) marker.togglePopup();
      });
    }
  }
}
