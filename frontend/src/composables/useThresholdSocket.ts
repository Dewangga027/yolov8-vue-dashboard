import { ref, onMounted, onUnmounted } from 'vue'
import io, { Socket } from 'socket.io-client'

// Global socket instance
let socket: Socket | null = null
const isConnected = ref(false)
const currentThreshold = ref<number>(30)

export function useThresholdSocket() {
  // Initialize socket connection
  const initSocket = () => {
    if (!socket) {
      socket = io('http://localhost:5000', {
        transports: ['websocket'],
        reconnection: true,
        reconnectionAttempts: 5,
        reconnectionDelay: 1000,
      })

      // Connection events
      socket.on('connect', () => {
        console.log('✅ WebSocket connected')
        isConnected.value = true
      })

      socket.on('disconnect', () => {
        console.log('❌ WebSocket disconnected')
        isConnected.value = false
      })

      // Listen for threshold updates from server
      socket.on('thresholds_updated', (data: { confidence: number, iou: number }) => {
        console.log('📊 Threshold updated from server:', data)
        currentThreshold.value = data.confidence * 100 // Convert to percentage
      })

      // Error handling
      socket.on('error', (error: any) => {
        console.error('❌ WebSocket error:', error)
      })
    }
  }

  // Send threshold update to server   
  const setThreshold = (confidencePercent: number) => {
    if (socket && isConnected.value) {
      const confidenceDecimal = confidencePercent / 100
      
      socket.emit('set_threshold', {
        confidence: confidenceDecimal
      })
      
      console.log(`📤 Sent threshold update: ${confidencePercent}% (${confidenceDecimal})`)
    } else {
      console.warn('⚠️ Socket not connected, cannot send threshold')
    }
  }

  // Get current status
  const getStatus = () => {
    if (socket && isConnected.value) {
      socket.emit('get_status')
    }
  }

  // Lifecycle
  onMounted(() => {
    initSocket()
  })

  onUnmounted(() => {
    // Don't disconnect socket on component unmount
    // Keep it alive for other components
  })

  return {
    isConnected,
    currentThreshold,
    setThreshold,
    getStatus,
    socket
  }
}