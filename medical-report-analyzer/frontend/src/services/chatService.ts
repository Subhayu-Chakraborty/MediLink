/**
 * src/services/chatService.ts
 * Patient-doctor chat history and websocket URL helpers.
 */
import api from './api'
import type { ChatMessage } from '../types/chat.types'

export async function getConversation(otherUserId: string): Promise<ChatMessage[]> {
  const res = await api.get<ChatMessage[]>(`/chat/messages/${otherUserId}`)
  return res.data
}

export function buildChatWebSocketUrl(token: string): string {
  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
  return `${protocol}://${window.location.host}/chat/ws?token=${encodeURIComponent(token)}`
}
