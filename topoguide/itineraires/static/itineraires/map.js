/**
 * This function adds one to its input.
 * @param {number} slo Start longitude
 * @param {number} sla Start latitude
 * @param {number} alo Arrival longitude
 * @param {number} ala Arrival latitude
 * @returns {map} The map.
 */
function create_map(slo, sla, alo, ala) {
    med_lon = (slo + alo)/2
    med_lat = (sla + ala)/2
    
    corner1 = L.latLng(slo, sla),
    corner2 = L.latLng(alo, ala),
    bounds  = L.latLngBounds(corner1, corner2);
    
    // Actual map creation
    var map = L.map('map', {
        center : [med_lon, med_lat]
    }).fitBounds(bounds);
    
    // add the OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="https://openstreetmap.org/copyright">OpenStreetMap contributors</a>'
    }).addTo(map);
    
    L.marker({lon: start_lat, lat: start_lon})
        .bindPopup('Départ')
        .addTo(map);
    L.marker({lon: arriv_lat, lat: arriv_lon})
        .bindPopup('Arrivée')
        .addTo(map);

    // show the scale bar on the lower left corner
    L.control.scale({imperial: false, metric: true}).addTo(map);

    return map
}