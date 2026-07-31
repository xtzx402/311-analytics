<script setup>
import { onMounted, watch, ref } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const props = defineProps({
  year: { type: Number, default: 2025 },
  complaintType: { type: String, default: '' },
})

const mapContainer = ref(null)
let map = null
let markerLayer = null

// 用字符串的hash值生成固定的颜色，同一个complaint_type每次颜色都一样
function typeToColor(type) {
  let hash = 0
  for (let i = 0; i < type.length; i++) {
    hash = type.charCodeAt(i) + ((hash << 5) - hash)
  }
  const hue = Math.abs(hash) % 360
  return `hsl(${hue}, 70%, 50%)`
}

async function loadComplaints() {
  const startDate = `${props.year}-01-01T00:00:00`
  const endDate = `${props.year}-12-31T23:59:59`

  const params = new URLSearchParams({
    limit: 500,
    start_date: startDate,
    end_date: endDate,
  })
  if (props.complaintType) {
    params.append('complaint_type', props.complaintType)
  }

  const res = await fetch(`http://localhost:8000/complaints?${params}`)
  const data = await res.json()

  if (markerLayer) {
    map.removeLayer(markerLayer)
  }

  markerLayer = L.layerGroup()
  data.items.forEach((c) => {
    if (c.latitude && c.longitude) {
      L.circleMarker([c.latitude, c.longitude], {
        radius: 6,
        fillColor: typeToColor(c.complaint_type),
        fillOpacity: 0.8,
        color: '#333',
        weight: 1,
      })
        .bindPopup(
          `<b>${c.complaint_type}</b><br>${c.descriptor ?? ''}<br>${c.borough ?? ''}<br>Status: ${c.status}<br>Date: ${c.created_date}`
        )
        .addTo(markerLayer)
    }
  })
  markerLayer.addTo(map)
}

onMounted(() => {
  map = L.map(mapContainer.value).setView([40.7128, -73.986], 11)

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors',
  }).addTo(map)

  loadComplaints()
})

watch([() => props.year, () => props.complaintType], loadComplaints)
</script>

<template>
  <div ref="mapContainer" style="height: 100vh; width: 100%;"></div>
</template>