<template>
  <main class="container mx-auto px-4 py-8">
    <div class="container mx-auto mb-8">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white">AI Model Deployment Dashboard</h1>
      <p class="text-gray-600 dark:text-gray-400">
        Visualize and analyze real-time results from your deployed models. Upload input, monitor predictions, and gain
        insights with confidence.
      </p>
    </div>

    <!-- Main Content -->
    <div class="flex flex-wrap gap-4 items-start min-h-[600px]">
      <!-- Left Column - Upload -->
      <div class="flex-1 min-w-[250px] space-y-4">
        <div class="min-h-[150px] bg-[var(--color-surface-alt)] rounded-[var(--radius-card)] p-4">
          <DropFiles @uploaded="onFileUploaded" />
        </div>
        <div class="bg-[var(--color-surface-alt)] rounded-[var(--radius-card)] p-4 flex flex-col gap-2">
          <ConfidenceSlider v-model="confThreshold" :detection-count="filteredResultBoxes.length" />
        </div>

      </div>

      <!-- Center Column - Preview -->
      <div class="flex-[2] min-w-[250px] w-full bg-[var(--color-surface-alt)] rounded-[var(--radius-card)] p-4">
        <div class="relative aspect-square w-full max-w-[720px] mx-auto rounded-xl overflow-hidden">
          <FilePreview :preview-url="previewUrl" :preview-name="previewName" :preview-type="previewType"
            :boxes="filteredResultBoxes" />
        </div>
      </div>

      <!-- Right Column - Controls -->
      <div class="flex-1 min-w-[250px] space-y-4">
        <div
          class="flex-1 min-w-[250px] h-full bg-[var(--color-surface-alt)] rounded-[var(--radius-card)] p-4 space-y-6">
          <JsonBoxSimple :detection-data="filteredResultBoxes" />
        </div>
      </div>
    </div>
  </main>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import DropFiles from '@components/DropFiles.vue'
import FilePreview from '@components/FilePreview.vue'
import ConfidenceSlider from '@/components/ConfidenceSlider.vue'
import OverlapSlider from '@components/OverlapSlider.vue'
import JsonBoxSimple from '@components/JsonBoxSimple.vue'

// === State utama ===
const filename = ref<string | null>(null)
const previewUrl = ref<string | null>(null)
const previewName = ref<string | null>(null)
const previewType = ref<string | null>(null)
const confThreshold = ref(30)

// === ALL hasil dari backend (confidence full) ===
const fullResultBoxes = ref<any[]>([])

// === Optimized filtering with computed property ===
const filteredResultBoxes = computed(() => {
  if (!fullResultBoxes.value.length) return []

  const threshold = confThreshold.value / 100 // Convert to 0-1 range
  return fullResultBoxes.value.filter(box => box.confidence >= threshold)
})

// Optional: Add debug logging
watch(filteredResultBoxes, (newFiltered) => {
  console.log(`📊 Filtered boxes: ${newFiltered.length}/${fullResultBoxes.value.length} (threshold: ${confThreshold.value}%)`)
})

function onFileUploaded(
  _file: File | null,
  name: string,
  type: string,
  resultUrl?: string,
  resultBoxesJson?: any[],
  uploadedFilename?: string
) {
  console.log('📁 File uploaded callback:', {
    name,
    type,
    resultUrl,
    boxesCount: resultBoxesJson?.length || 0,
    uploadedFilename,
    sampleBox: resultBoxesJson?.[0]
  })

  // Update preview info
  previewUrl.value = resultUrl || null
  previewName.value = name
  previewType.value = type
  filename.value = uploadedFilename || null

  // Update detection results
  fullResultBoxes.value = resultBoxesJson || []

  console.log('📊 Detection results processed:', {
    total: fullResultBoxes.value.length,
    filtered: filteredResultBoxes.value.length,
    threshold: confThreshold.value,
    firstFilteredBox: filteredResultBoxes.value[0]
  })
}

// Helper methods
const refreshDetection = () => {
  // No need to manually refresh - computed property handles it automatically
  console.log('Detection refreshed:', filteredResultBoxes.value.length, 'objects')
}

const clearResults = () => {
  filename.value = null
  previewUrl.value = null
  previewName.value = null
  previewType.value = null
  fullResultBoxes.value = []
  console.log('All results cleared')
}

defineExpose({
  refreshDetection,
  clearResults
})
</script>