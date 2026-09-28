/**
 * src/hooks/useChat.ts
 * Loads persisted chat history and keeps a live websocket open.
 */
import { useCallback, useEffect, useRef, useState } from 'react'
import { buildChatWebSocketUrl, getConversation } from '../services/chatService'
import type { ChatMessage } from '../types/chat.types'

type ChatStatus = 'connecting' | 'connected' | 'disconnected'

export function useChat(currentUserId?: string, otherUserId?: string, token?: string | null) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [status, setStatus] = useState<ChatStatus>('disconnected')
  const [error, setError] = useState('')
  const socketRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    if (!currentUserId || !otherUserId || !token) return

    let cancelled = false
    setMessages([])
    setError('')
    setStatus('connecting')

    getConversation(otherUserId)
      .then(history => {
        if (!cancelled) setMessages(history)
      })
      .catch(() => {
        if (!cancelled) setError('Unable to load chat history.')
      })

    const socket = new WebSocket(buildChatWebSocketUrl(token))
    socketRef.current = socket

    socket.onopen = () => {
      if (!cancelled) setStatus('connected')
    }
    socket.onclose = () => {
      if (!cancelled) setStatus('disconnected')
    }
    socket.onerror = () => {
      if (!cancelled) setError('Chat connection failed.')
    }
    socket.onmessage = event => {
      try {
        const data = JSON.parse(event.data)
        if (data.type === 'error') {
          setError(data.detail || 'Message could not be sent.')
          return
        }
        const message = data.message as ChatMessage
        const belongsToConversation =
          (message.sender_id === currentUserId && message.receiver_id === otherUserId) ||
          (message.sender_id === otherUserId && message.receiver_id === currentUserId)
        if (!belongsToConversation) return

        setMessages(prev => (
          prev.some(item => item.id === message.id)
            ? prev
            : [...prev, message].sort((a, b) => Date.parse(a.created_at) - Date.parse(b.created_at))
        ))
      } catch {
        setError('Received an unreadable chat message.')
      }
    }

    return () => {
      cancelled = true
      socket.close()
    }
  }, [currentUserId, otherUserId, token])

  const sendMessage = useCallback((content: string) => {
    if (!otherUserId || !content.trim()) return false
    if (socketRef.current?.readyState !== WebSocket.OPEN) {
      setError('Chat is not connected yet.')
      return false
    }

    socketRef.current.send(JSON.stringify({
      receiver_id: otherUserId,
      content: content.trim(),
    }))
    setError('')
    return true
  }, [otherUserId])

  return { messages, status, error, sendMessage }
}
