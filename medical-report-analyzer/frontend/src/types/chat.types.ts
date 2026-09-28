/** src/types/chat.types.ts */
export interface ChatMessage {
  id: string
  sender_id: string
  receiver_id: string
  content: string
  is_read: boolean
  created_at: string
}
