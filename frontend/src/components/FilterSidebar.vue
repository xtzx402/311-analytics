<script setup>
import { ref, onMounted, watch } from 'vue'

const emit = defineEmits(['filterChange'])

const types = ref([])
const selectedYear = ref(2025)
const selectedType = ref('')
const years = [2023, 2024, 2025, 2026]

onMounted(async () => {
  const res = await fetch('http://localhost:8000/complaints/types')
  const data = await res.json()
  types.value = data.types
})

watch([selectedYear, selectedType], () => {
  emit('filterChange', {
    year: selectedYear.value,
    complaintType: selectedType.value,
  })
})
</script>

<template>
  <div class="sidebar">
    <h3>Filters</h3>

    <label>Year</label>
    <select v-model="selectedYear">
      <option v-for="y in years" :key="y" :value="y">{{ y }}</option>
    </select>

    <label>Complaint Type</label>
    <select v-model="selectedType">
      <option value="">All Types</option>
      <option v-for="t in types" :key="t" :value="t">{{ t }}</option>
    </select>
  </div>
</template>

<style scoped>
.sidebar {
  width: 250px;
  padding: 16px;
  background: #f5f5f5;
  height: 100vh;
  box-sizing: border-box;
}
label {
  display: block;
  margin-top: 12px;
  font-weight: bold;
}
select {
  width: 100%;
  padding: 6px;
  margin-top: 4px;
}
</style>