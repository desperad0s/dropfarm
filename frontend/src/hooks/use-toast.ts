"use client"

import { useState, useCallback } from 'react'

type ToastProps = {
  title: string
  description?: string
  duration?: number
  variant?: 'default' | 'destructive'
}

export const useToast = () => {
  const [toasts, setToasts] = useState<ToastProps[]>([])

  const toast = useCallback((props: ToastProps) => {
    setToasts((prevToasts) => [...prevToasts, props])
    if (props.duration) {
      setTimeout(() => {
        setToasts((prevToasts) => prevToasts.filter((t) => t !== props))
      }, props.duration)
    }
  }, [])

  return { toast, toasts }
}

export const toastOriginal = (props: ToastProps) => {
  console.log('Toast:', props)
  // You can implement a more sophisticated toast system here if needed
}
