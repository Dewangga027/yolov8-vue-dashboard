<template>
    <div class="flex flex-col items-center justify-center w-full">
        <!-- Label atas -->
        <div class="flex flex-row justify-between mb-2 w-full max-w-md">
            <div class="flex items-center gap-2">
                <p class="font-medium">Confidence Threshold:</p>
            </div>
            <div class="flex items-center gap-2">
                <span class="font-bold text-lg">{{ displayValue }}%</span>
                <span v-if="detectionCount !== undefined" class="text-xs text-gray-500">
                    ({{ detectionCount }} objects)
                </span>
            </div>
        </div>

        <!-- Slider wrapper -->
        <div class="flex flex-row justify-center gap-2 w-full max-w-md">
            <div class="text-xs text-gray-500 dark:text-neutral-500 w-8 text-center">
                <p>0%</p>
            </div>

            <div class="relative w-full">
                <input type="range" v-model.number="confidence" min="0" max="100" step="1" @input="onInput"
                    @change="onChange" class="relative w-full bg-transparent cursor-pointer appearance-none focus:outline-none z-10
                    [&::-webkit-slider-thumb]:w-2.5
                    [&::-webkit-slider-thumb]:h-2.5
                    [&::-webkit-slider-thumb]:-mt-0.5
                    [&::-webkit-slider-thumb]:appearance-none
                    [&::-webkit-slider-thumb]:bg-white
                    [&::-webkit-slider-thumb]:shadow-[0_0_0_4px_rgba(37,99,235,1)]
                    [&::-webkit-slider-thumb]:rounded-full
                    [&::-webkit-slider-thumb]:transition-all
                    [&::-webkit-slider-thumb]:duration-150
                    [&::-webkit-slider-thumb]:ease-in-out
                    dark:[&::-webkit-slider-thumb]:bg-neutral-700

                    [&::-moz-range-thumb]:w-2.5
                    [&::-moz-range-thumb]:h-2.5
                    [&::-moz-range-thumb]:appearance-none
                    [&::-moz-range-thumb]:bg-white
                    [&::-moz-range-thumb]:border-4
                    [&::-moz-range-thumb]:border-blue-600
                    [&::-moz-range-thumb]:rounded-full
                    [&::-moz-range-thumb]:transition-all
                    [&::-moz-range-thumb]:duration-150
                    [&::-moz-range-thumb]:ease-in-out

                    [&::-webkit-slider-runnable-track]:w-full
                    [&::-webkit-slider-runnable-track]:h-2
                    [&::-webkit-slider-runnable-track]:bg-gray-100
                    [&::-webkit-slider-runnable-track]:rounded-full
                    dark:[&::-webkit-slider-runnable-track]:bg-neutral-700

                    [&::-moz-range-track]:w-full
                    [&::-moz-range-track]:h-2
                    [&::-moz-range-track]:bg-gray-100
                    [&::-moz-range-track]:rounded-full" />

                <!-- Tooltip -->
                <div class="absolute -top-8 transform -translate-x-1/2 bg-gray-800 text-white text-xs px-2 py-1 rounded opacity-0 transition-opacity duration-200 pointer-events-none"
                    :style="{ left: `${confidence}%` }" :class="{ 'opacity-100': isDragging }">
                    {{ confidence }}%
                </div>
            </div>

            <div class="text-xs text-gray-500 dark:text-neutral-500 w-10 text-center">
                <p>100%</p>
            </div>
        </div>
    </div>
</template>


<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useThresholdSocket } from '@/composables/useThresholdSocket'

// Props and emit for v-model
const props = defineProps<{
    modelValue: number,
    detectionCount?: number
}>()
const emit = defineEmits(['update:modelValue'])

// Local state
const isDragging = ref(false)
const isUpdating = ref(false)
const displayValue = ref(props.modelValue)


// WebSocket composable
const { setThreshold, isConnected } = useThresholdSocket()

// Computed v-model
const confidence = computed({
    get: () => props.modelValue,
    set: (v) => {
        emit('update:modelValue', v)
        displayValue.value = v
    }
})

// Debounce timer
let debounceTimer: ReturnType<typeof setTimeout> | null = null

// Handle input (while dragging)
const onInput = (event: Event) => {
    isDragging.value = true
    const value = parseInt((event.target as HTMLInputElement).value)
    displayValue.value = value

    // Clear existing timer
    if (debounceTimer) {
        clearTimeout(debounceTimer)
    }

    // Update immediately for UI responsiveness
    confidence.value = value

    // Debounce WebSocket update
    if (isConnected.value) {
        isUpdating.value = true
        debounceTimer = setTimeout(() => {
            setThreshold(value)
            isUpdating.value = false
        }, 100) // 100ms debounce for smooth updates
    }
}

// Handle change (when releasing)
const onChange = () => {
    isDragging.value = false

    // Ensure final value is sent
    if (debounceTimer) {
        clearTimeout(debounceTimer)
    }

    if (isConnected.value) {
        setThreshold(confidence.value)
    }
}

// Watch for external changes
watch(() => props.modelValue, (newVal) => {
    displayValue.value = newVal
})

// Cleanup
import { onUnmounted } from 'vue'
onUnmounted(() => {
    if (debounceTimer) {
        clearTimeout(debounceTimer)
    }
})
</script>

<style scoped></style>