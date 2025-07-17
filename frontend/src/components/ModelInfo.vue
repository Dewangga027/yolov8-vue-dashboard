<template>
    <!-- File Upload: Model -->
    <div class="max-w-sm mb-4">
        <form>
            <label for="modelUpload" class="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-200">
                Upload Model File (.tflite / .onnx)
            </label>
            <input id="modelUpload" type="file" accept=".tflite,.onnx" class="block w-full text-sm text-gray-500 
                file:me-4 file:py-2 file:px-4
                file:rounded-lg file:border-0
                file:text-sm file:font-medium
                file:bg-blue-600 file:text-white
                hover:file:bg-blue-700
                bg-[var(--color-surface-alt)]
                dark:text-neutral-400
                dark:file:bg-blue-500
                dark:hover:file:bg-blue-400
                rounded-[var(--radius-card)]">
        </form>
    </div>
</template>

<script setup lang="ts">

</script>

