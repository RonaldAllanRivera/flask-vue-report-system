<template>
  <div class="min-h-screen bg-slate-900 text-slate-200">
    <header class="flex items-center justify-between px-4 py-3 border-b border-slate-800">
      <h1>Reports Admin</h1>
      <nav class="flex gap-3 relative">
        <div ref="menuRef" class="relative group">
          <button
            ref="btnRef"
            type="button"
            class="inline-flex items-center gap-1 px-2.5 py-2 border border-slate-700 rounded-md bg-[#0b1220] text-slate-200 hover:border-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-400"
            aria-haspopup="true"
            :aria-expanded="isOpen ? 'true' : 'false'"
            aria-controls="main-menu"
            @click="toggle"
          >
            <span>Google and Binom Reports Only</span>
            <span aria-hidden="true">▾</span>
          </button>
          <div
            id="main-menu"
            role="menu"
            :class="[
              'absolute left-0 top-[120%] min-w-[260px] rounded-lg border border-[#1f2937] bg-[#111827] shadow-xl z-50',
              isOpen ? 'block' : 'hidden',
              'md:group-hover:block'
            ]"
          >
            <RouterLink role="menuitem" class="block px-3 py-2 text-slate-200 hover:bg-slate-800 hover:text-cyan-300" to="/google" @click="closeMenu">Google Data</RouterLink>
            <RouterLink role="menuitem" class="block px-3 py-2 text-slate-200 hover:bg-slate-800 hover:text-cyan-300" to="/binom-google" @click="closeMenu">Binom Google Spent Data</RouterLink>
            <RouterLink role="menuitem" class="block px-3 py-2 text-slate-200 hover:bg-slate-800 hover:text-cyan-300" to="/google-binom-report" @click="closeMenu">Google Binom Report</RouterLink>
          </div>
        </div>
      </nav>
    </header>
    <ToastHost />
    <main class="p-4">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import ToastHost from '@/components/ToastHost.vue'

const isOpen = ref(false)
const menuRef = ref<HTMLElement | null>(null)
const btnRef = ref<HTMLButtonElement | null>(null)

function toggle() {
  isOpen.value = !isOpen.value
}
function closeMenu() {
  isOpen.value = false
}
function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') {
    closeMenu()
    btnRef.value?.focus()
  }
}
function onClickOutside(e: MouseEvent) {
  const root = menuRef.value
  if (!root) return
  if (!root.contains(e.target as Node)) closeMenu()
}

onMounted(() => {
  document.addEventListener('keydown', onKeydown)
  document.addEventListener('click', onClickOutside)
})
onBeforeUnmount(() => {
  document.removeEventListener('keydown', onKeydown)
  document.removeEventListener('click', onClickOutside)
})
</script>