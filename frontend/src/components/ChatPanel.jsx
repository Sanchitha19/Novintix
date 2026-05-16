import React, { useState, useRef, useEffect } from 'react';
import { Send, User, Bot, Sparkles } from 'lucide-react';
import QuickChips from './QuickChips';
import AgentResponseCard from './AgentResponseCard';
import { sendQuery } from '../api';

const ChatPanel = ({ token, onNewInteraction }) => {
  const [messages, setMessages] = useState([
    { type: 'ai', text: "Hello! I'm your Novintix AI assistant. How can I help you with your order today?", timestamp: new Date().toISOString(), agent_name: "FAQAgent", confidence: 1.0 }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  const handleSend = async (text) => {
    const messageText = text || input;
    if (!messageText.trim()) return;

    const userMessage = { type: 'user', text: messageText, timestamp: new Date().toISOString() };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // For demo, we use a fixed user_id and session_id
      const data = await sendQuery(messageText, "user_001", "session_demo_123", token);
      
      // Data is a list of AgentResponses
      const aiResponses = data.map(res => ({
        ...res,
        type: 'ai',
      }));
      
      setMessages(prev => [...prev, ...aiResponses]);
      onNewInteraction(messageText, data);
    } catch (error) {
      console.error(error);
      setMessages(prev => [...prev, { type: 'ai', text: "I'm sorry, I encountered an error connecting to the backend. Please ensure the server is running on port 8000.", timestamp: new Date().toISOString(), agent_name: "System" }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-dark-bg border-r border-dark-border relative">
      {/* Header */}
      <div className="p-4 border-b border-dark-border flex items-center justify-between bg-dark-panel/50 backdrop-blur-md sticky top-0 z-10">
        <div className="flex items-center gap-3">
          <div className="relative">
            <div className="w-10 h-10 rounded-xl bg-brand-blue/20 flex items-center justify-center">
              <Bot className="w-6 h-6 text-brand-blue" />
            </div>
            <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-brand-green border-2 border-dark-bg rounded-full status-pulse"></div>
          </div>
          <div>
            <h1 className="text-sm font-bold text-white tracking-tight">Novintix Support</h1>
            <p className="text-[10px] text-brand-blue font-bold uppercase tracking-widest">Powered by Agentic AI</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs font-medium text-slate-400">John Doe</span>
          <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center text-xs font-bold text-white">JD</div>
        </div>
      </div>

      {/* Messages */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-6 grid-bg">
        {messages.map((msg, idx) => (
          msg.type === 'user' ? (
            <div key={idx} className="flex justify-end animate-in fade-in slide-in-from-right-4 duration-300">
              <div className="max-w-[80%] flex flex-col items-end">
                <div className="p-3 px-4 rounded-2xl bg-brand-blue text-white text-sm shadow-lg shadow-brand-blue/10">
                  {msg.text}
                </div>
                <span className="text-[9px] font-mono text-slate-500 mt-1 mr-1">
                  {new Date(msg.timestamp).toLocaleTimeString()}
                </span>
              </div>
            </div>
          ) : (
            <AgentResponseCard key={idx} response={msg} />
          )
        ))}
        {isLoading && (
          <div className="flex items-center gap-3 animate-pulse">
            <div className="w-8 h-8 rounded-lg bg-slate-800 flex items-center justify-center">
              <Bot className="w-5 h-5 text-slate-600" />
            </div>
            <div className="flex gap-1">
              <div className="w-2 h-2 rounded-full bg-slate-600"></div>
              <div className="w-2 h-2 rounded-full bg-slate-600"></div>
              <div className="w-2 h-2 rounded-full bg-slate-600"></div>
            </div>
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="p-4 bg-dark-panel/50 border-t border-dark-border">
        <QuickChips onSelect={handleSend} />
        <div className="relative glowing-border rounded-xl bg-dark-bg border border-dark-border transition-all">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            disabled={isLoading}
            placeholder="Ask anything about your order..."
            className="w-full py-4 pl-4 pr-14 text-sm bg-transparent border-none focus:ring-0 text-slate-200 placeholder:text-slate-600"
          />
          <button
            onClick={() => handleSend()}
            disabled={isLoading || !input.trim()}
            className="absolute right-2 top-1/2 -translate-y-1/2 w-10 h-10 flex items-center justify-center rounded-lg bg-brand-blue text-white disabled:opacity-50 disabled:bg-slate-800 transition-all"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
        <p className="text-[10px] text-center text-slate-600 mt-3 font-medium uppercase tracking-tighter">
          End-to-end encrypted & AI Moderated • Novintix v1.2
        </p>
      </div>
    </div>
  );
};

export default ChatPanel;
