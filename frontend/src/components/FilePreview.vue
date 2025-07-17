<template>
  <div class="w-full h-full flex items-center justify-center relative">
    <transition name="fade-slide" mode="out-in" appear>
      <!-- IMAGE preview with canvas -->
      <div v-if="previewUrl && isImage" key="image" class="relative w-full h-full flex items-center justify-center">
        <div class="relative">
          <img 
            ref="imageEl" 
            :src="previewUrl"
            class="object-contain max-w-full max-h-full rounded-xl border"
            alt="preview"
            @load="onImageLoad" 
            @error="onImageError"
          />
          <canvas 
            ref="canvasEl" 
            class="absolute top-0 left-0 w-full h-full pointer-events-none" 
          />
        </div>
      </div>

      <!-- VIDEO preview -->
      <div v-else-if="previewUrl && isVideo" key="video" class="flex items-center justify-center">
        <video 
          :src="previewUrl" 
          controls 
          class="object-contain max-w-full max-h-full rounded-xl" 
        />
      </div>

      <!-- EMPTY state -->
      <div v-else key="empty" class="text-gray-400 text-center">
        <div class="flex flex-col items-center justify-center space-y-4">
          <svg class="w-16 h-16 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
          </svg>
          <div>
            <p class="text-lg font-medium text-gray-500">No image selected</p>
            <p class="text-sm text-gray-400">Upload an image to see detection results</p>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { defineProps, ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'

interface DetectionBox {
  // XYWH format (from our backend)
  x?: number
  y?: number
  width?: number
  height?: number
  confidence: number
  class?: string
  label?: string
  detection_id?: string
  
  // XYXY format (legacy/alternative)
  xyxy?: number[]
}

const props = defineProps<{
  previewUrl: string | null | undefined
  previewName?: string | null
  previewType?: string | null
  boxes: DetectionBox[]
}>()

// Refs for canvas + image element
const imageEl = ref<HTMLImageElement | null>(null)
const canvasEl = ref<HTMLCanvasElement | null>(null)

// Store animation frame ID for cleanup
let animationFrameId: number | null = null

// Computed properties
const isImage = computed(() => {
  if (!props.previewUrl) return false
  
  const imageExtensions = /\.(jpg|jpeg|png|webp|gif|bmp)$/i
  if (imageExtensions.test(props.previewUrl)) {
    return true
  }
  
  if (props.previewType && props.previewType.startsWith('image/')) {
    return true
  }
  
  if (props.previewUrl.startsWith('blob:') || props.previewUrl.startsWith('data:image/')) {
    return true
  }
  
  return false
})

const isVideo = computed(() => {
  if (!props.previewUrl) return false
  
  const videoExtensions = /\.(mp4|avi|webm|mov|mkv)$/i
  if (videoExtensions.test(props.previewUrl)) {
    return true
  }
  
  if (props.previewType && props.previewType.startsWith('video/')) {
    return true
  }
  
  if (props.previewUrl.startsWith('blob:') && props.previewType?.startsWith('video/')) {
    return true
  }
  
  return false
})

// Debounced drawing function for smooth performance
let drawTimeout: ReturnType<typeof setTimeout> | null = null

// Watch for changes in boxes - REALTIME UPDATE
watch(
  () => props.boxes,
  (newBoxes) => {
    // Clear previous timeout
    if (drawTimeout) {
      clearTimeout(drawTimeout)
    }
    
    // Use requestAnimationFrame for smooth rendering
    drawTimeout = setTimeout(() => {
      if (isImage.value && imageEl.value && imageEl.value.complete) {
        // Cancel previous animation frame if exists
        if (animationFrameId) {
          cancelAnimationFrame(animationFrameId)
        }
        
        animationFrameId = requestAnimationFrame(() => {
          drawBoundingBoxesWithContrast(newBoxes || [])
        })
      }
    }, 16) // ~60fps
  },
  { deep: true, immediate: true }
)

// Watch for URL changes
watch(
  () => props.previewUrl,
  () => {
    // Clear canvas when URL changes
    if (canvasEl.value) {
      const ctx = canvasEl.value.getContext('2d')
      if (ctx) {
        ctx.clearRect(0, 0, canvasEl.value.width, canvasEl.value.height)
      }
    }
  }
)

// Handle image load event
const onImageLoad = () => {
  console.log('🖼️ Image loaded successfully')
  // Immediate draw after image loads
  if (props.boxes && props.boxes.length > 0) {
    requestAnimationFrame(() => {
      drawBoundingBoxesWithContrast(props.boxes)
    })
  }
}

// Handle image error
const onImageError = (e: Event) => {
  console.error('❌ Error loading image:', e)
}

// Enhanced color palette with better contrast
const CONTRAST_COLORS = [
  { primary: '#FF3E3E', secondary: '#FFFFFF', shadow: 'rgba(0,0,0,0.8)' }, // Red
  { primary: '#00D9FF', secondary: '#000033', shadow: 'rgba(0,0,0,0.8)' }, // Cyan
  { primary: '#00FF44', secondary: '#003300', shadow: 'rgba(0,0,0,0.8)' }, // Green
  { primary: '#FFD700', secondary: '#332200', shadow: 'rgba(0,0,0,0.8)' }, // Gold
  { primary: '#FF00FF', secondary: '#330033', shadow: 'rgba(0,0,0,0.8)' }, // Magenta
  { primary: '#FF8C00', secondary: '#331100', shadow: 'rgba(0,0,0,0.8)' }, // Orange
  { primary: '#9400D3', secondary: '#FFFFFF', shadow: 'rgba(255,255,255,0.8)' }, // Violet
  { primary: '#00CED1', secondary: '#001414', shadow: 'rgba(0,0,0,0.8)' }, // Dark Turquoise
  { primary: '#FF1493', secondary: '#330011', shadow: 'rgba(0,0,0,0.8)' }, // Deep Pink
  { primary: '#32CD32', secondary: '#002200', shadow: 'rgba(0,0,0,0.8)' }, // Lime Green
]

// Main drawing function with contrast colors
function drawBoundingBoxesWithContrast(boxes: DetectionBox[]) {
  const canvas = canvasEl.value
  const image = imageEl.value
  if (!canvas || !image || !boxes.length) return

  const ctx = canvas.getContext('2d')
  if (!ctx) return

  // Get actual rendered size
  const rect = image.getBoundingClientRect()
  const { width, height } = rect
  
  // Set canvas size to match rendered image
  canvas.width = width
  canvas.height = height
  
  // Clear previous drawings
  ctx.clearRect(0, 0, width, height)

  // Enable smoothing for better quality
  ctx.imageSmoothingEnabled = true
  ctx.imageSmoothingQuality = 'high'

  // Map untuk menyimpan warna setiap class
  const classColors = new Map<string, typeof CONTRAST_COLORS[0]>()
  let colorIndex = 0

  // Sort boxes by area (larger first) to prevent overlap issues
  const sortedBoxes = [...boxes].sort((a, b) => {
    const areaA = (a.width || 0) * (a.height || 0)
    const areaB = (b.width || 0) * (b.height || 0)
    return areaB - areaA
  })

  sortedBoxes.forEach(box => {
    // Get coordinates
    let x1, y1, x2, y2
    
    if (box.xyxy && Array.isArray(box.xyxy) && box.xyxy.length === 4) {
      [x1, y1, x2, y2] = box.xyxy
    } else if (box.x !== undefined && box.y !== undefined && box.width !== undefined && box.height !== undefined) {
      x1 = box.x - (box.width / 2)
      y1 = box.y - (box.height / 2)
      x2 = box.x + (box.width / 2)
      y2 = box.y + (box.height / 2)
    } else {
      console.warn('Invalid box format:', box)
      return
    }

    // Scale coordinates to canvas size
    const scaleX = width / image.naturalWidth
    const scaleY = height / image.naturalHeight
    
    const left = x1 * scaleX
    const top = y1 * scaleY
    const boxWidth = (x2 - x1) * scaleX
    const boxHeight = (y2 - y1) * scaleY

    // Get class name
    const className = box.class || box.label || 'unknown'
    
    // Assign color for class if not exists
    if (!classColors.has(className)) {
      classColors.set(className, CONTRAST_COLORS[colorIndex % CONTRAST_COLORS.length])
      colorIndex++
    }

    const colorScheme = classColors.get(className)!
    
    // 1. Draw shadow/outline for contrast
    ctx.save()
    ctx.shadowColor = colorScheme.shadow
    ctx.shadowBlur = 4
    ctx.shadowOffsetX = 0
    ctx.shadowOffsetY = 0
    
    // Draw thick outline
    ctx.strokeStyle = colorScheme.shadow
    ctx.lineWidth = 5
    ctx.strokeRect(left, top, boxWidth, boxHeight)
    
    // 2. Draw main bounding box
    ctx.shadowBlur = 0
    ctx.strokeStyle = colorScheme.primary
    ctx.lineWidth = 3
    ctx.strokeRect(left, top, boxWidth, boxHeight)
    
    // 3. Draw corner accents for better visibility
    const cornerLength = Math.min(20, boxWidth * 0.2, boxHeight * 0.2)
    ctx.lineWidth = 4
    ctx.strokeStyle = colorScheme.primary
    
    // Top-left corner
    ctx.beginPath()
    ctx.moveTo(left, top + cornerLength)
    ctx.lineTo(left, top)
    ctx.lineTo(left + cornerLength, top)
    ctx.stroke()
    
    // Top-right corner
    ctx.beginPath()
    ctx.moveTo(left + boxWidth - cornerLength, top)
    ctx.lineTo(left + boxWidth, top)
    ctx.lineTo(left + boxWidth, top + cornerLength)
    ctx.stroke()
    
    // Bottom-left corner
    ctx.beginPath()
    ctx.moveTo(left, top + boxHeight - cornerLength)
    ctx.lineTo(left, top + boxHeight)
    ctx.lineTo(left + cornerLength, top + boxHeight)
    ctx.stroke()
    
    // Bottom-right corner
    ctx.beginPath()
    ctx.moveTo(left + boxWidth - cornerLength, top + boxHeight)
    ctx.lineTo(left + boxWidth, top + boxHeight)
    ctx.lineTo(left + boxWidth, top + boxHeight - cornerLength)
    ctx.stroke()
    
    ctx.restore()

    // 4. Prepare label text
    const confidence = (box.confidence * 100).toFixed(1)
    const labelText = `${className} ${confidence}%`
    
    // Set font with better readability
    ctx.font = 'bold 14px Inter, system-ui, -apple-system, sans-serif'
    
    // Measure text
    const textMetrics = ctx.measureText(labelText)
    const textWidth = textMetrics.width
    const textHeight = 20
    const padding = 6
    
    // Position label above box (or below if too close to top)
    let labelX = left
    let labelY = top - padding - 2
    
    if (top < textHeight + padding * 2) {
      labelY = top + boxHeight + padding + textHeight
    }
    
    // Keep label within canvas bounds
    if (labelX + textWidth + padding * 2 > width) {
      labelX = width - textWidth - padding * 2
    }
    if (labelX < 0) {
      labelX = padding
    }
    
    // 5. Draw label background with rounded corners
    const bgX = labelX - padding
    const bgY = labelY - textHeight
    const bgWidth = textWidth + padding * 2
    const bgHeight = textHeight + padding
    const radius = 4
    
    ctx.save()
    
    // Shadow for label
    ctx.shadowColor = 'rgba(0,0,0,0.3)'
    ctx.shadowBlur = 4
    ctx.shadowOffsetY = 2
    
    // Draw rounded rectangle background
    ctx.fillStyle = colorScheme.primary
    ctx.beginPath()
    ctx.moveTo(bgX + radius, bgY)
    ctx.lineTo(bgX + bgWidth - radius, bgY)
    ctx.quadraticCurveTo(bgX + bgWidth, bgY, bgX + bgWidth, bgY + radius)
    ctx.lineTo(bgX + bgWidth, bgY + bgHeight - radius)
    ctx.quadraticCurveTo(bgX + bgWidth, bgY + bgHeight, bgX + bgWidth - radius, bgY + bgHeight)
    ctx.lineTo(bgX + radius, bgY + bgHeight)
    ctx.quadraticCurveTo(bgX, bgY + bgHeight, bgX, bgY + bgHeight - radius)
    ctx.lineTo(bgX, bgY + radius)
    ctx.quadraticCurveTo(bgX, bgY, bgX + radius, bgY)
    ctx.closePath()
    ctx.fill()
    
    // Draw border for label
    ctx.strokeStyle = colorScheme.secondary
    ctx.lineWidth = 1
    ctx.stroke()
    
    ctx.restore()
    
    // 6. Draw text with high contrast
    ctx.fillStyle = colorScheme.secondary
    ctx.textBaseline = 'bottom'
    ctx.fillText(labelText, labelX, labelY)
  })

  // Draw detection count in corner
  if (boxes.length > 0) {
    ctx.save()
    const countText = `${boxes.length} detections`
    ctx.font = 'bold 12px Inter, system-ui, -apple-system, sans-serif'
    const countMetrics = ctx.measureText(countText)
    const countX = width - countMetrics.width - 15
    const countY = height - 10
    
    // Background for count
    ctx.fillStyle = 'rgba(0,0,0,0.7)'
    ctx.fillRect(countX - 5, countY - 15, countMetrics.width + 10, 20)
    
    // Text
    ctx.fillStyle = '#FFFFFF'
    ctx.fillText(countText, countX, countY)
    ctx.restore()
  }
}

// Cleanup on unmount
onUnmounted(() => {
  if (drawTimeout) {
    clearTimeout(drawTimeout)
  }
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId)
  }
})

// Expose methods for parent component
defineExpose({
  drawBoundingBoxes: drawBoundingBoxesWithContrast,
  onImageLoad
})
</script>

<style scoped>
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

.fade-slide-enter-to,
.fade-slide-leave-from {
  opacity: 1;
  transform: translateY(0);
}

canvas {
  pointer-events: none;
}

img {
  transition: opacity 0.3s ease;
}

img:not([src]) {
  opacity: 0;
}

img[src] {
  opacity: 1;
}
</style>