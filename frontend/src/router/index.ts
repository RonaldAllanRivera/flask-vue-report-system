import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import GoogleData from '@/views/GoogleData.vue'
import BinomGoogle from '@/views/BinomGoogle.vue'
import GoogleBinomReport from '@/views/GoogleBinomReport.vue'

const routes: RouteRecordRaw[] = [
  { path: '/', redirect: '/google' },
  { path: '/google', component: GoogleData },
  { path: '/binom-google', component: BinomGoogle },
  { path: '/google-binom-report', component: GoogleBinomReport },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
