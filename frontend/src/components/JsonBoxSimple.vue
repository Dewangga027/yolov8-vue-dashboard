<template>
  <div class="json-box-container">
    <!-- Header -->
    <div class="flex items-center justify-between mb-3">
      <div class="flex items-center gap-2">
        <svg class="size-5 text-blue-600" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
          <polyline points="14,2 14,8 20,8"/>
          <line x1="16" y1="13" x2="8" y2="13"/>
          <line x1="16" y1="17" x2="8" y2="17"/>
          <polyline points="10,9 9,9 8,9"/>
        </svg>
        <h3 class="text-sm font-semibold text-gray-800 dark:text-white">
          Detection Results
        </h3>
        <span v-if="hasDetections" 
              class="text-xs bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 px-2 py-1 rounded-full">
          {{ detectionData.length }} objects
        </span>
      </div>
      
      <!-- View Mode Toggle -->
      <div class="flex items-center gap-2">
        <select v-model="viewMode" 
                class="text-xs border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-800 dark:text-white rounded px-2 py-1">
          <option value="formatted">Formatted</option>
          <option value="json">Raw JSON</option>
          <option value="summary">Summary</option>
        </select>
      </div>
    </div>

    <!-- Content Container -->
    <div class="h-[350px] bg-white/60 dark:bg-black/30 rounded-lg shadow border border-gray-200 dark:border-gray-700 overflow-hidden relative">
      
      <!-- No Data State -->
      <div v-if="!hasDetections" class="flex items-center justify-center h-full">
        <div class="text-center">
          <svg class="mx-auto w-12 h-12 text-gray-400 mb-3" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
            <polyline points="14,2 14,8 20,8"/>
          </svg>
          <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">No detection data available</p>
          <p class="text-xs text-gray-400 dark:text-gray-500">Upload and process an image to see results</p>
        </div>
      </div>

      <!-- Content Area -->
      <div v-else class="h-full flex flex-col">
        
        <!-- Formatted View -->
        <div v-if="viewMode === 'formatted'" class="flex-1 overflow-auto p-4 space-y-3">
          <!-- Summary Stats -->
          <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-3 border border-blue-200 dark:border-blue-800">
            <h4 class="text-sm font-semibold text-blue-800 dark:text-blue-200 mb-2">📊 Summary</h4>
            <div class="grid grid-cols-2 gap-2 text-xs">
              <div>
                <span class="text-gray-600 dark:text-gray-400">Total:</span>
                <span class="ml-1 font-semibold text-gray-800 dark:text-white">{{ detectionData.length }}</span>
              </div>
              <div>
                <span class="text-gray-600 dark:text-gray-400">Classes:</span>
                <span class="ml-1 font-semibold text-gray-800 dark:text-white">{{ uniqueClasses.length }}</span>
              </div>
              <div>
                <span class="text-gray-600 dark:text-gray-400">Avg Conf:</span>
                <span class="ml-1 font-semibold text-gray-800 dark:text-white">{{ averageConfidence }}%</span>
              </div>
              <div>
                <span class="text-gray-600 dark:text-gray-400">Min Conf:</span>
                <span class="ml-1 font-semibold text-gray-800 dark:text-white">{{ minConfidence }}%</span>
              </div>
            </div>
          </div>

          <!-- Detection Items -->
          <div class="space-y-2">
            <h4 class="text-sm font-semibold text-gray-800 dark:text-white">🔍 Detections</h4>
            <div class="space-y-2 max-h-40 overflow-y-auto">
              <div v-for="(detection, index) in detectionData" 
                   :key="detection.detection_id || index" 
                   class="bg-gray-50 dark:bg-gray-800 rounded-lg p-3 border border-gray-200 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors cursor-pointer"
                   @click="selectDetection(detection)">
                <div class="flex items-center justify-between mb-2">
                  <span class="text-sm font-semibold text-gray-800 dark:text-white capitalize">
                    {{ detection.class || detection.label }}
                  </span>
                  <span class="text-xs bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 px-2 py-1 rounded-full">
                    {{ (detection.confidence * 100).toFixed(1) }}%
                  </span>
                </div>
                <div class="grid grid-cols-2 gap-2 text-xs text-gray-600 dark:text-gray-400">
                  <div>Position: ({{ Math.round(detection.x || 0) }}, {{ Math.round(detection.y || 0) }})</div>
                  <div>Size: {{ Math.round(detection.width || 0) }}×{{ Math.round(detection.height || 0) }}</div>
                  <div>Area: {{ Math.round(detection.area || ((detection.width || 0) * (detection.height || 0))) }} px²</div>
                  <div v-if="detection.detection_id">ID: {{ detection.detection_id.substring(0, 8) }}...</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Summary View -->
        <div v-else-if="viewMode === 'summary'" class="flex-1 overflow-auto p-4">
          <div class="space-y-4">
            <!-- Quick Stats -->
            <div class="grid grid-cols-2 gap-3">
              <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-3 text-center">
                <div class="text-2xl font-bold text-blue-600 dark:text-blue-400">{{ detectionData.length }}</div>
                <div class="text-xs text-gray-600 dark:text-gray-400">Total Objects</div>
              </div>
              <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3 text-center">
                <div class="text-2xl font-bold text-green-600 dark:text-green-400">{{ uniqueClasses.length }}</div>
                <div class="text-xs text-gray-600 dark:text-gray-400">Unique Classes</div>
              </div>
            </div>

            <!-- Class Breakdown -->
            <div v-if="classStats" class="bg-gray-50 dark:bg-gray-800 rounded-lg p-3">
              <h5 class="text-sm font-semibold text-gray-800 dark:text-white mb-2">Class Breakdown</h5>
              <div class="space-y-1">
                <div v-for="(count, className) in classStats" :key="className" 
                     class="flex items-center justify-between text-xs">
                  <span class="text-gray-600 dark:text-gray-400 capitalize">{{ className }}</span>
                  <div class="flex items-center gap-2">
                    <div class="w-16 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                      <div class="bg-blue-500 h-2 rounded-full" 
                           :style="{ width: (count / detectionData.length * 100) + '%' }"></div>
                    </div>
                    <span class="font-medium w-8 text-right">{{ count }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Raw JSON View -->
        <div v-else class="flex-1 overflow-auto p-4">
          <pre ref="jsonRef" 
               class="text-xs whitespace-pre-wrap w-full select-text font-mono leading-relaxed text-gray-700 dark:text-gray-300">{{ jsonOutput }}</pre>
        </div>

        <!-- Action Buttons -->
        <div class="flex items-center gap-2 px-4 py-3 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
          <button type="button" @click="copyToClipboard"
                  class="py-1 px-3 group inline-flex items-center gap-x-2 text-xs font-medium rounded-lg border border-gray-200 bg-white text-gray-800 shadow-sm hover:bg-gray-50 focus:outline-none focus:bg-gray-50 dark:bg-neutral-800 dark:border-neutral-700 dark:text-white dark:hover:bg-neutral-700 dark:focus:bg-neutral-700">
            <svg v-if="!copied" class="size-3 group-hover:rotate-6 transition" xmlns="http://www.w3.org/2000/svg"
                 width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                 stroke-linecap="round" stroke-linejoin="round">
              <rect width="8" height="4" x="8" y="2" rx="1" ry="1"></rect>
              <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path>
            </svg>
            <svg v-else class="size-3 text-blue-600 transition" xmlns="http://www.w3.org/2000/svg" width="24"
                 height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                 stroke-linecap="round" stroke-linejoin="round">
              <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
            <span>{{ copied ? 'Copied!' : 'Copy' }}</span>
          </button>

          <button type="button" @click="downloadJson"
                  class="py-1 px-3 inline-flex items-center gap-x-2 text-xs font-medium rounded-lg border border-gray-200 bg-white text-gray-800 shadow-sm hover:bg-gray-50 focus:outline-none focus:bg-gray-50 dark:bg-neutral-800 dark:border-neutral-700 dark:text-white dark:hover:bg-neutral-700 dark:focus:bg-neutral-700">
            <svg class="size-3" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="7 10 12 15 17 10"/>
              <line x1="12" y1="15" x2="12" y2="3"/>
            </svg>
            <span>Download</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

// Props
interface DetectionBox {
  confidence: number
  class: string
  class_id?: number
  label?: string
  x?: number
  y?: number
  width?: number
  height?: number
  area?: number
  detection_id?: string
  xyxy?: number[]
  position?: string
}

interface Props {
  detectionData?: DetectionBox[]
}

const props = withDefaults(defineProps<Props>(), {
  detectionData: () => []
})

// Emits
const emit = defineEmits<{
  detectionSelected: [detection: DetectionBox]
}>()

// Reactive state
const copied = ref(false)
const jsonRef = ref<HTMLElement | null>(null)
const viewMode = ref<'formatted' | 'json' | 'summary'>('formatted')

// Computed properties
const hasDetections = computed(() => props.detectionData && props.detectionData.length > 0)

const uniqueClasses = computed(() => {
  if (!hasDetections.value) return []
  return [...new Set(props.detectionData.map(item => item.class || item.label))]
})

const classStats = computed(() => {
  if (!hasDetections.value) return {}
  
  const stats: Record<string, number> = {}
  props.detectionData.forEach(item => {
    const className = item.class || item.label || 'unknown'
    stats[className] = (stats[className] || 0) + 1
  })
  return stats
})

const averageConfidence = computed(() => {
  if (!hasDetections.value) return '0'
  
  const total = props.detectionData.reduce((sum, item) => sum + (item.confidence || 0), 0)
  return ((total / props.detectionData.length) * 100).toFixed(1)
})

const minConfidence = computed(() => {
  if (!hasDetections.value) return '0'
  
  const min = Math.min(...props.detectionData.map(item => item.confidence || 0))
  return (min * 100).toFixed(1)
})

const jsonOutput = computed(() => {
  if (!hasDetections.value) return ''
  
  const outputData = {
    total_detections: props.detectionData.length,
    unique_classes: uniqueClasses.value.length,
    class_statistics: classStats.value,
    confidence_stats: {
      average: parseFloat(averageConfidence.value),
      minimum: parseFloat(minConfidence.value)
    },
    detections: props.detectionData
  }
  
  return JSON.stringify(outputData, null, 2)
})

// Methods
const selectDetection = (detection: DetectionBox) => {
  console.log('Selected detection:', detection)
  emit('detectionSelected', detection)
}

const copyToClipboard = async () => {
  try {
    const textToCopy = jsonOutput.value
    await navigator.clipboard.writeText(textToCopy)
    copied.value = true
    setTimeout(() => copied.value = false, 2000)
  } catch (error) {
    console.error('Failed to copy:', error)
  }
}

const downloadJson = () => {
  if (!hasDetections.value) return
  
  const dataStr = jsonOutput.value
  const dataBlob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(dataBlob)
  
  const link = document.createElement('a')
  link.href = url
  link.download = `detection_results_${new Date().getTime()}.json`
  link.click()
  
  URL.revokeObjectURL(url)
}
</script>

<style scoped>
/* Custom scrollbar */
.overflow-auto::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

.overflow-auto::-webkit-scrollbar-track {
  background: transparent;
}

.overflow-auto::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 3px;
}

.dark .overflow-auto::-webkit-scrollbar-thumb {
  background: #4b5563;
}
</style>