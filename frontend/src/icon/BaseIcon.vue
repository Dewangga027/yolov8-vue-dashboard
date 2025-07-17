<template>
  <component :is="icon" v-bind="iconProps" />
</template>

<script setup>
import { computed } from 'vue'
import * as icons from 'lucide-vue-next'

const props = defineProps({
  name: {
    type: String,
    required: true
  },
  size: {
    type: [Number, String],
    default: 24
  },
  color: {
    type: String,
    default: 'currentColor'
  },
  stroke: {
    type: [Number, String],
    default: 'currentColor'
  },
  class: {
    type: [String, Array, Object],
    default: ''
  }
})

const icon = computed(() => icons[props.name])

const iconProps = computed(() => ({
  size: props.size,
  color: props.color,
  stroke: props.stroke,
  class: props.class
}))
</script>
