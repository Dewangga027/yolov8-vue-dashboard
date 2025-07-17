<template>
  <div class="drop-files-container">
    <!-- Header -->
    <div class="mb-4">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">
        Upload Image for Detection
      </h3>
      <p class="text-sm text-gray-600 dark:text-gray-400">
        Drag and drop an image or click to select - Auto upload & detection
      </p>
    </div>

    <!-- Drop Zone -->
    <div 
      @drop="handleDrop"
      @dragover.prevent="!isProcessing"
      @dragenter.prevent="!isProcessing"
      @dragleave="handleDragLeave"
      @dragover="handleDragOver"
      :class="[
        'border-2 border-dashed rounded-lg p-6 text-center transition-all duration-200',
        // Conditional cursor and hover states
        !isProcessing && !hasCompletedUpload ? 'cursor-pointer' : 'cursor-default',
        // Drag over state (only when not processing and not completed)
        isDragOver && !isProcessing && !hasCompletedUpload
          ? 'border-blue-400 bg-blue-50 dark:bg-blue-900/20' 
          : '',
        // Default state (only when not processing and not completed)
        !isProcessing && !hasCompletedUpload && !isDragOver
          ? 'border-gray-300 dark:border-gray-600 hover:border-blue-400 hover:bg-gray-50 dark:hover:bg-gray-800'
          : '',
        // Processing state
        isProcessing
          ? 'border-blue-300 dark:border-blue-600 bg-blue-50 dark:bg-blue-900/20'
          : '',
        // Completed state
        hasCompletedUpload && !isProcessing
          ? 'border-green-300 dark:border-green-600 bg-green-50 dark:bg-green-900/20'
          : ''
      ]"
      @click="!isProcessing && !hasCompletedUpload ? triggerFileInput() : null"
    >
      <input
        ref="fileInput"
        type="file"
        accept="image/*"
        @change="handleFileSelect"
        class="hidden"
      />

      <!-- Upload Icon and Text (Default State) -->
      <div v-if="!isProcessing && !hasCompletedUpload">
        <svg class="mx-auto h-12 w-12 text-gray-400 mb-4" stroke="currentColor" fill="none" viewBox="0 0 48 48">
          <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
        </svg>
        <p class="text-gray-600 dark:text-gray-400">
          <span class="font-medium text-blue-600 hover:text-blue-500">Click to upload</span>
          or drag and drop
        </p>
        <p class="text-xs text-gray-500 mt-1">PNG, JPG, WebP up to 16MB</p>
        <p class="text-xs text-blue-500 mt-2 font-medium">✨ Auto detection after upload</p>
      </div>

      <!-- Processing State -->
      <div v-else-if="isProcessing" class="space-y-4">
        <div class="flex items-center justify-center">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mr-3"></div>
          <span class="text-sm font-medium text-gray-900 dark:text-white">{{ processingMessage }}</span>
        </div>
        
        <!-- File Info During Processing -->
        <div v-if="selectedFile" class="text-xs text-gray-600 dark:text-gray-400">
          <p>📁 {{ selectedFile.name }}</p>
          <p>📏 {{ formatFileSize(selectedFile.size) }}</p>
        </div>
        
        <!-- Progress Bar -->
        <div class="w-full bg-gray-200 rounded-full h-2 dark:bg-gray-700">
          <div 
            class="bg-blue-600 h-2 rounded-full transition-all duration-300"
            :style="{ width: progress + '%' }"
          ></div>
        </div>
        
        <p class="text-xs text-gray-500">{{ progressText }}</p>
      </div>

      <!-- Completed State -->
      <div v-else-if="hasCompletedUpload" class="space-y-3">
        <div class="flex items-center justify-center">
          <svg class="h-8 w-8 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          <span class="text-sm font-medium text-green-800 dark:text-green-200">Detection Complete!</span>
        </div>
        
        <div v-if="lastResult" class="text-xs text-gray-600 dark:text-gray-400 space-y-1">
          <p>📁 {{ lastResult.filename }}</p>
          <p>🎯 Found {{ lastResult.detectionCount }} objects</p>
          <p>🕒 {{ lastResult.processingTime }}ms</p>
        </div>
        
        <!-- Action Buttons -->
        <div class="flex gap-2 justify-center">
          <button 
            @click.stop="uploadAnother"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
          >
            Upload Another
          </button>
          <button 
            @click.stop="clearResults"
            class="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors text-sm font-medium"
          >
            Clear
          </button>
        </div>
      </div>
    </div>

    <!-- Error Display -->
    <div v-if="error" class="mt-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
      <div class="flex items-start">
        <svg class="h-5 w-5 text-red-400 mt-0.5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.728-.833-2.498 0L3.316 16.5c-.77.833.192 2.5 1.732 2.5z"/>
        </svg>
        <div>
          <h4 class="text-sm font-medium text-red-800 dark:text-red-200">Detection Error</h4>
          <p class="text-sm text-red-700 dark:text-red-300 mt-1">{{ error }}</p>
          <div class="mt-2 flex gap-2">
            <button 
              @click="clearError" 
              class="text-xs text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-200 underline"
            >
              Dismiss
            </button>
            <button 
              @click="retryUpload" 
              class="text-xs text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-200 underline"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Success Message -->
    <div v-if="successMessage" class="mt-4 p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
      <div class="flex items-center">
        <svg class="h-5 w-5 text-green-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
        <p class="text-sm text-green-800 dark:text-green-200">{{ successMessage }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

// Props & Emits
const emit = defineEmits<{
  uploaded: [
    file: File | null,
    name: string,
    type: string,
    resultUrl?: string,
    resultBoxesJson?: any[],
    uploadedFilename?: string
  ]
}>()

// Reactive state
const selectedFile = ref<File | null>(null)
const isDragOver = ref(false)
const isUploading = ref(false)
const isProcessing = ref(false)
const hasCompletedUpload = ref(false)
const progress = ref(0)
const processingMessage = ref('')
const progressText = ref('')
const error = ref('')
const successMessage = ref('')
const confidenceThreshold = ref(0.3)
const iouThreshold = ref(0.5)
const lastResult = ref<{
  filename: string
  detectionCount: number
  processingTime: number
} | null>(null)

// Refs
const fileInput = ref<HTMLInputElement>()

// Constants
const MAX_FILE_SIZE = 16 * 1024 * 1024 // 16MB
const ALLOWED_TYPES = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/bmp']
const API_BASE_URL = 'http://localhost:5000'

// Methods
const triggerFileInput = () => {
  // Only allow file input when not processing and not completed
  if (!isProcessing.value && !hasCompletedUpload.value) {
    fileInput.value?.click()
  }
}

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    handleFile(target.files[0])
  }
}

const handleDragOver = (event: DragEvent) => {
  if (!isProcessing.value) {
    isDragOver.value = true
  }
}

const handleDragLeave = (event: DragEvent) => {
  const rect = (event.currentTarget as HTMLElement).getBoundingClientRect()
  const x = event.clientX
  const y = event.clientY
  
  if (x < rect.left || x >= rect.right || y < rect.top || y >= rect.bottom) {
    isDragOver.value = false
  }
}

const handleDrop = (event: DragEvent) => {
  event.preventDefault()
  isDragOver.value = false
  
  if (!isProcessing.value && event.dataTransfer?.files && event.dataTransfer.files[0]) {
    handleFile(event.dataTransfer.files[0])
  }
}

const handleFile = (file: File) => {
  // Reset state
  clearError()
  clearSuccess()
  hasCompletedUpload.value = false
  
  // Validate file
  if (!ALLOWED_TYPES.includes(file.type)) {
    error.value = 'Invalid file type. Please select a valid image file (JPEG, PNG, WebP, BMP).'
    return
  }
  
  if (file.size > MAX_FILE_SIZE) {
    error.value = `File too large. Maximum size is ${MAX_FILE_SIZE / (1024 * 1024)}MB.`
    return
  }
  
  selectedFile.value = file
  
  // 🚀 AUTO UPLOAD: Immediately start upload and inference
  runInference()
}

const runInference = async () => {
  if (!selectedFile.value) return
  
  clearError()
  clearSuccess()
  isUploading.value = true
  isProcessing.value = true
  progress.value = 0
  processingMessage.value = 'Uploading file...'
  progressText.value = 'Preparing upload...'
  
  const startTime = Date.now()
  
  try {
    // Step 1: Upload file
    progress.value = 10
    processingMessage.value = 'Uploading file...'
    progressText.value = 'Sending file to server...'
    
    console.log('🚀 Starting auto upload for:', selectedFile.value.name)
    
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    
    const uploadResponse = await fetch(`${API_BASE_URL}/upload`, {
      method: 'POST',
      body: formData
    })
    
    const uploadResult = await uploadResponse.json()
    
    if (!uploadResult.success) {
      throw new Error(uploadResult.error || 'Upload failed')
    }
    
    console.log('✅ Upload successful:', uploadResult.filename)
    
    progress.value = 30
    isUploading.value = false
    processingMessage.value = 'Running AI Detection...'
    progressText.value = 'Analyzing image with YOLO...'
    
    // Step 2: Run inference
    const inferenceResponse = await fetch(`${API_BASE_URL}/inference`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        filename: uploadResult.filename,
        conf: confidenceThreshold.value,
        iou: iouThreshold.value
      })
    })
    
    progress.value = 70
    progressText.value = 'Processing detection results...'
    
    const inferenceResult = await inferenceResponse.json()
    
    if (!inferenceResult.success) {
      throw new Error(inferenceResult.error || 'Inference failed')
    }
    
    console.log('🎯 Inference successful:', inferenceResult)
    
    progress.value = 90
    progressText.value = 'Finalizing results...'
    
    // Step 3: Format results
    const detectionResults = inferenceResult.result
    const boxes = detectionResults.predictions || []
    
    const formattedBoxes = boxes.map((prediction: any) => ({
      x: prediction.x,
      y: prediction.y,
      width: prediction.width,
      height: prediction.height,
      confidence: prediction.confidence,
      class: prediction.class,
      label: prediction.class,
      class_id: prediction.class_id,
      detection_id: prediction.detection_id,
      area: prediction.area,
      position: prediction.position,
      xyxy: prediction.xyxy
    }))
    
    progress.value = 100
    processingMessage.value = 'Complete!'
    progressText.value = `Found ${boxes.length} objects`
    
    // Store result info
    const processingTime = Date.now() - startTime
    lastResult.value = {
      filename: selectedFile.value.name,
      detectionCount: boxes.length,
      processingTime
    }
    
    console.log('🎉 Auto detection completed:', {
      boxes: boxes.length,
      time: processingTime + 'ms',
      url: inferenceResult.output_url
    })
    
    // Emit results to parent
    emit('uploaded', 
      selectedFile.value,
      selectedFile.value.name,
      selectedFile.value.type,
      inferenceResult.output_url,
      formattedBoxes,
      uploadResult.filename
    )
    
    // Set completion state
    hasCompletedUpload.value = true
    
    successMessage.value = `🎉 Detection complete! Found ${boxes.length} objects in ${(processingTime / 1000).toFixed(1)}s`
    
    // Auto-hide success message
    setTimeout(() => {
      clearSuccess()
    }, 5000)
    
  } catch (err) {
    console.error('❌ Auto upload error:', err)
    error.value = err instanceof Error ? err.message : 'An unexpected error occurred'
    hasCompletedUpload.value = false
  } finally {
    isProcessing.value = false
    isUploading.value = false
    progress.value = 0
    processingMessage.value = ''
    progressText.value = ''
  }
}

const uploadAnother = () => {
  // Reset all state for new upload
  selectedFile.value = null
  hasCompletedUpload.value = false
  lastResult.value = null
  clearError()
  clearSuccess()
  
  // Clear file input
  if (fileInput.value) {
    fileInput.value.value = ''
  }
  
  // Trigger file selector
  setTimeout(() => {
    triggerFileInput()
  }, 100)
}

const clearResults = () => {
  selectedFile.value = null
  hasCompletedUpload.value = false
  lastResult.value = null
  clearError()
  clearSuccess()
  
  if (fileInput.value) {
    fileInput.value.value = ''
  }
  
  // Emit clear to parent
  emit('uploaded', null, '', '', undefined, [], undefined)
}

const retryUpload = () => {
  if (selectedFile.value) {
    clearError()
    runInference()
  } else {
    clearError()
    triggerFileInput()
  }
}

const clearError = () => {
  error.value = ''
}

const clearSuccess = () => {
  successMessage.value = ''
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// Expose methods for parent component
defineExpose({
  clearResults,
  triggerFileInput,
  uploadAnother
})
</script>

<style scoped>
/* Custom range slider styles */
input[type="range"]::-webkit-slider-thumb {
  appearance: none;
  height: 16px;
  width: 16px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  border: 2px solid #ffffff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

input[type="range"]::-moz-range-thumb {
  height: 16px;
  width: 16px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  border: 2px solid #ffffff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

input[type="range"]::-webkit-slider-track {
  height: 4px;
  border-radius: 2px;
  background: #e5e7eb;
}

input[type="range"]::-moz-range-track {
  height: 4px;
  border-radius: 2px;
  background: #e5e7eb;
}

input[type="range"]:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.drop-files-container {
  min-height: 200px;
}

/* Loading animation enhancement */
@keyframes pulse-glow {
  0%, 100% {
    box-shadow: 0 0 5px rgba(59, 130, 246, 0.5);
  }
  50% {
    box-shadow: 0 0 20px rgba(59, 130, 246, 0.8);
  }
}

.animate-spin {
  animation: spin 1s linear infinite, pulse-glow 2s ease-in-out infinite;
}
</style>