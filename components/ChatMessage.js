import React from 'react'

const ChatMessage = ({ message, isStreaming = false }) => {
  const isUser = message.role === 'user'
  
  return (
    <div className={`message ${isUser ? 'user-message' : 'assistant-message'}`}>
      <div className="message-avatar">
        {isUser ? 'U' : 'AI'}
      </div>
      <div className="message-content">
        <div className="message-text">
          {message.content}
          {isStreaming && <span className="typing-indicator">▋</span>}
        </div>
      </div>
    </div>
  )
}

export default ChatMessage
