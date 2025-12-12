import { useState } from 'react'
import Head from 'next/head'
import ChatMessage from '../components/ChatMessage'
import ImageUpload from '../components/ImageUpload'

export default function Home() {
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [streamingMessage, setStreamingMessage] = useState('')

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return

    const userMessage = { role: 'user', content: inputMessage }
    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsLoading(true)
    setStreamingMessage('')

    try {
      const response = await fetch(`http://localhost:8000/chat-stream?prompt=${encodeURIComponent(inputMessage)}`)
      const reader = response.body.getReader()
      const decoder = new TextDecoder()

      let assistantMessage = ''
      while (true) {
        const { value, done } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        assistantMessage += chunk
        setStreamingMessage(assistantMessage)
      }

      setMessages(prev => [...prev, { role: 'assistant', content: assistantMessage }])
      setStreamingMessage('')
    } catch (error) {
      console.error('Error sending message:', error)
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, there was an error processing your request.' }])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <>
      <Head>
        <title>ML Assistant Chat</title>
        <meta name="description" content="AI-powered medical assistant" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>
      
      <div className="app">
        <header className="header">
          <h1>Medical AI Assistant</h1>
          <p>Your intelligent healthcare companion</p>
        </header>

        <main className="main">
          <div className="chat-container">
            <div className="messages">
              {messages.length === 0 && (
                <div className="welcome-message">
                  <h3>Welcome to Medical AI Assistant</h3>
                  <p>I'm here to help with your medical questions and document analysis. How can I assist you today?</p>
                </div>
              )}
              
              {messages.map((message, index) => (
                <ChatMessage key={index} message={message} />
              ))}
              
              {streamingMessage && (
                <ChatMessage 
                  message={{ role: 'assistant', content: streamingMessage }} 
                  isStreaming={true}
                />
              )}
            </div>

            <div className="input-section">
              <ImageUpload />
              
              <div className="input-container">
                <textarea
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask me anything about medical topics..."
                  disabled={isLoading}
                  rows={3}
                />
                <button 
                  onClick={sendMessage} 
                  disabled={!inputMessage.trim() || isLoading}
                  className="send-button"
                >
                  {isLoading ? 'Sending...' : 'Send'}
                </button>
              </div>
            </div>
          </div>
        </main>
      </div>
    </>
  )
}
