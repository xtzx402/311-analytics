<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <nav style="padding: 12px; background: #333;">
    <RouterLink to="/" style="color: white; margin-right: 16px;">Map</RouterLink>
    <RouterLink to="/stats" style="color: white;">Statistics</RouterLink>
  </nav>
  <RouterView />
</template>