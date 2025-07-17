<template>
  <div class="min-h-screen flex flex-col lg:flex-row bg-[var(--color-bg)] text-[var(--color-text)]">
    <!-- Sidebar -->
    <!-- <aside class="w-full lg:w-[250px] shrink-0 dark:border-zinc-800">
      <SidebarPanel />
    </aside> -->

    <!-- Main Content -->
    <main class="flex-1 overflow-y-auto px-4 py-6">
      <ContentPanel />
    </main>
  </div>
</template>

<script setup lang="ts">
// import SidebarPanel from '@/components/SidebarPanel.vue'
import ContentPanel from '@/components/ContentPanel.vue'
</script>
