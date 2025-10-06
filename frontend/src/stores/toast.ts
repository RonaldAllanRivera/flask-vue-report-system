import { defineStore } from 'pinia'

export type ToastType = 'info' | 'success' | 'error'
export interface ToastItem { id: number; message: string; type: ToastType; timeout?: number }

let _id = 1

export const useToastStore = defineStore('toast', {
  state: () => ({ items: [] as ToastItem[] }),
  actions: {
    push(message: string, type: ToastType = 'info', timeout = 3000) {
      const id = _id++
      const item: ToastItem = { id, message, type, timeout }
      this.items.push(item)
      if (timeout > 0) setTimeout(() => this.remove(id), timeout)
      return id
    },
    info(message: string, timeout = 3000) { return this.push(message, 'info', timeout) },
    success(message: string, timeout = 3000) { return this.push(message, 'success', timeout) },
    error(message: string, timeout = 4000) { return this.push(message, 'error', timeout) },
    remove(id: number) { this.items = this.items.filter(i => i.id !== id) },
    clear() { this.items = [] },
  },
})
