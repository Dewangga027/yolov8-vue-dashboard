import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import '@preline/file-upload';
import BaseIcon from '@/icon/BaseIcon.vue'

import _ from 'lodash'
(window as any)._ = _

import Dropzone from 'dropzone'
(window as any).Dropzone = Dropzone

import ClipboardJS from 'clipboard';
(window as any).ClipboardJS = ClipboardJS

const app = createApp(App)
app.component('BaseIcon', BaseIcon)
app.mount('#app')

import("preline/dist/index.js");
