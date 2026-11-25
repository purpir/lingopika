export {}

declare global {
  interface Window {
    Telegram?: {
      WebApp?: {
        initData: string
        ready: () => void
        expand: () => void
        openInvoice: (url: string, callback?: (status: string) => void) => void
        showAlert: (message: string) => void
        HapticFeedback?: { impactOccurred: (style: string) => void }
      }
    }
  }
}