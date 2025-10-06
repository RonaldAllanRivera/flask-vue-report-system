<template>
  <div class="fixed inset-x-0 top-3 z-[100] flex justify-center px-2 pointer-events-none">
    <div class="space-y-2 w-full max-w-md">
      <div v-for="t in items" :key="t.id" class="pointer-events-auto rounded-md border px-3 py-2 text-sm shadow-md"
           :class="{
             'bg-slate-900 border-slate-700 text-slate-200': t.type==='info',
             'bg-emerald-900/50 border-emerald-700 text-emerald-100': t.type==='success',
             'bg-rose-900/50 border-rose-700 text-rose-100': t.type==='error',
           }">
        <div class="flex items-start gap-2">
          <span class="mt-0.5">
            <span v-if="t.type==='success'">✅</span>
            <span v-else-if="t.type==='error'">⚠️</span>
            <span v-else>ℹ️</span>
          </span>
          <div class="flex-1">{{ t.message }}</div>
          <button class="text-xs text-slate-400 hover:text-slate-200" @click="remove(t.id)">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { useToastStore } from '@/stores/toast'

const toast = useToastStore()
const { items } = storeToRefs(toast)
const remove = (id: number) => toast.remove(id)
</script>
