import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as Icons from '@element-plus/icons-vue'
import axios from 'axios'

// 添加这段代码来抑制ResizeObserver警告
const debounce = (fn, delay) => {
  let timer = null
  return function() {
    let context = this
    let args = arguments
    clearTimeout(timer)
    timer = setTimeout(function() {
      fn.apply(context, args)
    }, delay)
  }
}

// 抑制ResizeObserver警告
const originalError = console.error
console.error = (...args) => {
  if (args[0]?.includes?.('ResizeObserver') || 
      args[0]?.message?.includes?.('ResizeObserver')) {
    return
  }
  originalError.apply(console, args)
}

const app = createApp(App)
app.use(router)
app.use(ElementPlus)

// 注册图标
Object.keys(Icons).forEach(key => {
  app.component(key, Icons[key])
})

// 添加响应拦截器查看错误
axios.interceptors.response.use(
  response => response,
  error => {
    console.error('请求错误详情:', error.response?.data);
    console.error('请求状态码:', error.response?.status);
    return Promise.reject(error);
  }
);

app.mount('#app')

// eslint-disable-next-line no-unused-vars
const unusedVar = 'test' 

window.addEventListener('error', (event) => {
  if (event.message.includes('ResizeObserver')) {
    event.stopImmediatePropagation();
  }
});