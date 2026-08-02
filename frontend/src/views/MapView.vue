<script setup>
import { ref } from 'vue'
import FilterSidebar from '../components/FilterSidebar.vue'
import ComplaintMap from '../components/ComplaintMap.vue'

const filters = ref({ year: 2025, complaintType: '' })

function handleFilterChange(newFilters) {
  filters.value = newFilters
}
</script>

<template>
  <div style="display: flex;">
    <FilterSidebar @filter-change="handleFilterChange" />
    <ComplaintMap :year="filters.year" :complaint-type="filters.complaintType" />
  </div>
</template>