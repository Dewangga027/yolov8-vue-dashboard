<template>
  <form @submit.prevent>
    <!-- Pixel to CM Input -->
    <div class="mb-4">
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">
        Pixel-to-CM Ratio:
      </label>
      <input
        type="number"
        v-model.number="pixelToCm"
        step="0.01"
        class="w-full px-3 py-2 border rounded-md bg-white dark:bg-neutral-800 dark:border-neutral-700 dark:text-white text-sm"
      />
    </div>

    <!-- ROI JSON Input -->
    <div>
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">
        ROI Points (JSON Format):
      </label>
      <textarea
        v-model="roiJson"
        rows="4"
        placeholder="[[100,200],[200,300],[300,200]]"
        class="w-full px-3 py-2 border rounded-md bg-white dark:bg-neutral-800 dark:border-neutral-700 dark:text-white text-sm font-mono"
      ></textarea>
    </div>
  </form>
</template>

<script setup lang="ts">
import { ref, watch, defineEmits } from 'vue'

const pixelToCm = ref(2.75)
const roiJson = ref('[[100,200],[200,300],[300,200]]')

// Emit ke parent
const emit = defineEmits(['update:pixelToCm', 'update:roi'])

watch(pixelToCm, (val) => {
  emit('update:pixelToCm', val)
})

watch(roiJson, (val) => {
  try {
    const parsed = JSON.parse(val)
    if (Array.isArray(parsed)) {
      emit('update:roi', parsed)
    }
  } catch {
    // ignore parse errors
  }
})
</script>
