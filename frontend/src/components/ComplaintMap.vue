<script setup>
import { onMounted, ref } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const mapContainer = ref(null)

onMounted(async () => {
  const map = L.map(mapContainer.value).setView([40.7128, -73.9860], 11) // 纽约市中心

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors',
  }).addTo(map)

  const res = await fetch('http://localhost:8000/complaints?limit=100')
  const data = await res.json()

  data.items.forEach((complaint) => {
    if (complaint.latitude && complaint.longitude) {
      L.marker([complaint.latitude, complaint.longitude])
        .bindPopup(`${complaint.complaint_type}<br>${complaint.borough ?? ''}`)
        .addTo(map)
    }
  })
})
</script>

<template>
  <div ref="mapContainer" style="height: 600px; width: 100%;"></div>
</template>