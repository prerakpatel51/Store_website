import * as maplibregl from 'https://unpkg.com/maplibre-gl@6.16.0/dist/maplibre-gl.mjs';

const storeMapElement = document.getElementById('store-map');
const storeMapData = document.getElementById('store-map-data');

if (storeMapElement && storeMapData) {
  const stores = JSON.parse(storeMapData.textContent);
  if (!stores.length) {
    storeMapElement.textContent = 'Store map locations are being updated.';
  } else {
    storeMapElement.textContent = '';
    const map = new maplibregl.Map({
      container: storeMapElement,
      style: 'https://tiles.openfreemap.org/styles/positron',
      center: [-80.63, 28.1],
      zoom: 9,
      scrollZoom: false,
    });
    map.addControl(new maplibregl.NavigationControl({showCompass: false}), 'top-left');

    const bounds = new maplibregl.LngLatBounds();
    const markers = [];
    stores.forEach(store => {
      const coordinates = [store.longitude, store.latitude];
      bounds.extend(coordinates);
      const popup = document.createElement('div');
      popup.className = 'store-map-popup';
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

      const anchor = document.createElement('div');
      anchor.className = 'store-map-anchor';
      const connector = document.createElement('span');
      connector.className = 'store-map-connector';
      const point = document.createElement('span');
      point.className = 'store-map-point';
      const marker = document.createElement('button');
      marker.type = 'button';
      marker.className = 'store-map-marker';
      marker.textContent = store.name;
      marker.setAttribute('aria-label', `Show ${store.name}, store ${store.number}, on the map`);
      anchor.append(connector, point, marker);
      new maplibregl.Marker({element: anchor, anchor: 'center'})
        .setLngLat(coordinates)
        .setPopup(new maplibregl.Popup({offset: 16}).setDOMContent(popup))
        .addTo(map);
      markers.push({coordinates, marker, connector});
    });

    // Place labels around their actual map points without merging locations.
    function positionLabels() {
      const placed = [];
      const width = storeMapElement.clientWidth;
      const height = storeMapElement.clientHeight;
      const projected = markers.map(entry => ({...entry, point: map.project(entry.coordinates)}))
        .sort((a, b) => a.point.y - b.point.y || a.point.x - b.point.x);
      projected.forEach(entry => {
        const labelWidth = entry.marker.offsetWidth;
        const labelHeight = entry.marker.offsetHeight;
        const side = labelWidth / 2 + 19;
        const step = labelHeight + 10;
        const offsets = [
          [0, -labelHeight / 2 - 17], [side, 0], [-side, 0],
          [0, labelHeight / 2 + 17],
          [side, -step], [-side, -step], [side, step], [-side, step],
          [side, -step * 2], [-side, -step * 2],
          [side, step * 2], [-side, step * 2],
          [0, -step * 2], [0, step * 2],
          [side * 1.8, 0], [-side * 1.8, 0],
        ];
        let choice = offsets[0];
        let lowestScore = Infinity;
        offsets.forEach(([dx, dy]) => {
          const rect = {
            left: entry.point.x + dx - labelWidth / 2,
            right: entry.point.x + dx + labelWidth / 2,
            top: entry.point.y + dy - labelHeight / 2,
            bottom: entry.point.y + dy + labelHeight / 2,
          };
          const overlaps = placed.reduce((total, other) => total + Math.max(0, Math.min(rect.right + 5, other.right) - Math.max(rect.left - 5, other.left)) * Math.max(0, Math.min(rect.bottom + 5, other.bottom) - Math.max(rect.top - 5, other.top)), 0);
          const coversPoint = projected.some(other =>
            other.point.x > rect.left - 6 && other.point.x < rect.right + 6 &&
            other.point.y > rect.top - 6 && other.point.y < rect.bottom + 6
          );
          const outside = rect.left < 7 || rect.right > width - 7 || rect.top < 7 || rect.bottom > height - 42;
          const score = overlaps * 100 + (outside ? 100000 : 0) + (coversPoint ? 100000 : 0) + Math.hypot(dx, dy);
          if (score < lowestScore) {
            lowestScore = score;
            choice = [dx, dy];
          }
        });
        const [dx, dy] = choice;
        entry.marker.style.left = `${dx}px`;
        entry.marker.style.top = `${dy}px`;
        entry.connector.style.width = `${Math.hypot(dx, dy)}px`;
        entry.connector.style.transform = `rotate(${Math.atan2(dy, dx)}rad)`;
        placed.push({
          left: entry.point.x + dx - labelWidth / 2,
          right: entry.point.x + dx + labelWidth / 2,
          top: entry.point.y + dy - labelHeight / 2,
          bottom: entry.point.y + dy + labelHeight / 2,
        });
      });
    }
    map.on('moveend', positionLabels);
    map.on('resize', positionLabels);
    map.fitBounds(bounds, {padding: {top: 45, right: 45, bottom: 72, left: 45}, maxZoom: 12, duration: 0});
    requestAnimationFrame(positionLabels);
  }
}
