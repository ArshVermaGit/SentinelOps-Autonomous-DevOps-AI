import { useEffect, useRef } from "react"
import { WS_URL } from "@/lib/constants"

export function useWebSocket(onMessage: (data: Record<string, unknown>) => void) {
  const wsRef = useRef<WebSocket | null>(null)
  const onMessageRef = useRef(onMessage)
  useEffect(() => {
    onMessageRef.current = onMessage
  }, [onMessage])
  
  useEffect(() => {
    const connect = () => {
      try {
        const ws = new WebSocket(WS_URL)
        wsRef.current = ws
        
        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data)
            onMessageRef.current(data)
          } catch {
            // Ignore non-JSON messages (e.g., pong)
          }
        }
        
        ws.onclose = () => {
          // Reconnect after 3 seconds
          setTimeout(connect, 3000)
        }
        
        // Keep alive
        const ping = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send("ping")
          }
        }, 30000)
        
        ws.onopen = () => {
          // Cleanup ping on close
        }
        
        return () => {
          clearInterval(ping)
        }
      } catch {
        // WebSocket not available
      }
    }
    
    connect()
    
    return () => {
      wsRef.current?.close()
    }
  }, [])
}
