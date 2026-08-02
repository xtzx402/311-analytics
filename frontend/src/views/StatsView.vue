<script setup>
import { ref, onMounted, watch } from 'vue'
import { Bar, Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title, Tooltip, Legend, BarElement, LineElement,
  CategoryScale, LinearScale, PointElement,
} from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, BarElement, LineElement, CategoryScale, LinearScale, PointElement)

const selectedYear = ref(2025)
const years = [2023, 2024, 2025, 2026]
const stats = ref(null)

async function loadStats() {
  const res = await fetch(`http://localhost:8000/complaints/stats/summary?year=${selectedYear.value}`)
  stats.value = await res.json()
}

onMounted(loadStats)
watch(selectedYear, loadStats)

function byTypeChartData(stats) {
  return {
    labels: stats.by_type.map((r) => r.type),
    datasets: [{ label: 'Complaints', data: stats.by_type.map((r) => r.count), backgroundColor: '#3b82f6' }],
  }
}

function byBoroughChartData(stats) {
  return {
    labels: stats.by_borough.map((r) => r.borough),
    datasets: [{ label: 'Complaints', data: stats.by_borough.map((r) => r.count), backgroundColor: '#10b981' }],
  }
}

function trendChartData(stats) {
  return {
    labels: stats.trend.map((r) => r.month.slice(0, 7)),
    datasets: [{ label: 'Complaints per Month', data: stats.trend.map((r) => r.count), borderColor: '#f59e0b', fill: false }],
  }
}
</script>

<template>
  <div style="padding: 24px;">
    <h2>Statistics</h2>

    <label>Year</label>
    <select v-model="selectedYear">
      <option v-for="y in years" :key="y" :value="y">{{ y }}</option>
    </select>

    <p v-if="stats">Total complaints: {{ stats.total.toLocaleString() }}</p>

    <div v-if="stats" style="max-width: 700px; margin-top: 24px;">
      <h3>Top 10 Complaint Types</h3>
      <Bar :data="byTypeChartData(stats)" />
    </div>

    <div v-if="stats" style="max-width: 700px; margin-top: 24px;">
      <h3>By Borough</h3>
      <Bar :data="byBoroughChartData(stats)" />
    </div>

    <div v-if="stats" style="max-width: 700px; margin-top: 24px;">
      <h3>Monthly Trend</h3>
      <Line :data="trendChartData(stats)" />
    </div>
  </div>
</template>