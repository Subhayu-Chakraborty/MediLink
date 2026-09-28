/**
 * src/components/common/ChatWindow.tsx
 * Compact patient-doctor chat panel.
 */
import { useState, type FC } from 'react'
import { useAuth } from '../../hooks/useAuth'
import { useChat } from '../../hooks/useChat'

interface ChatWindowProps {
  receiverId: string
  receiverName: string
}

const ChatWindow: FC<ChatWindowProps> = ({ receiverId, receiverName }) => {
  const { user, token } = useAuth()
  const [input, setInput] = useState('')
  const { messages, status, error, sendMessage } = useChat(user?.id, receiverId, token)

  const handleSend = () => {
    if (sendMessage(input)) setInput('')
  }

  return (
    <div className="border border-slate-200 rounded-lg bg-white overflow-hidden">
      <div className="px-4 py-3 border-b border-slate-200 bg-slate-50 flex items-center justify-between gap-3">
        <div className="min-w-0">
          <p className="font-semibold text-slate-800 text-sm truncate">Chat with {receiverName}</p>
          <p className="text-xs text-slate-400 capitalize">{status}</p>
        </div>
        <span className={`w-2.5 h-2.5 rounded-full shrink-0 ${
          status === 'connected' ? 'bg-emerald-500' :
          status === 'connecting' ? 'bg-amber-500' : 'bg-slate-300'
        }`} />
      </div>

      <div className="h-64 overflow-y-auto p-3 space-y-2 bg-slate-50">
        {messages.length === 0 ? (
          <div className="h-full flex items-center justify-center text-xs text-slate-400 text-center px-6">
            No messages yet. Start the conversation when you are ready.
          </div>
        ) : messages.map(message => {
          const mine = message.sender_id === user?.id
          return (
            <div key={message.id} className={`flex ${mine ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[78%] rounded-lg px-3 py-2 text-sm shadow-sm ${
                mine ? 'bg-blue-600 text-white' : 'bg-white text-slate-700 border border-slate-200'
              }`}>
                <p className="whitespace-pre-wrap break-words">{message.content}</p>
                <p className={`text-[10px] mt-1 ${mine ? 'text-blue-100' : 'text-slate-400'}`}>
                  {new Date(message.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </p>
              </div>
            </div>
          )
        })}
      </div>

      {error && <div className="px-3 py-2 text-xs text-red-700 bg-red-50 border-t border-red-100">{error}</div>}

      <div className="p-3 border-t border-slate-200 flex gap-2">
        <input
          type="text"
          className="form-input flex-1"
          placeholder="Type a message"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => {
            if (e.key === 'Enter') handleSend()
          }}
        />
        <button onClick={handleSend} disabled={!input.trim()} className="btn-primary shrink-0">
          Send
        </button>
      </div>
    </div>
  )
}

export default ChatWindow
