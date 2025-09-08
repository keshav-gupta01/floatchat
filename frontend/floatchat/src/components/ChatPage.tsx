import React, { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import "./ChatMessage.css";
import { FaRegThumbsUp, FaRegThumbsDown, FaPaperclip, FaRegSmile, FaMicrophone } from "react-icons/fa";
import bot from "../assets/bot.svg";
import { useTheme } from "./ThemeContext";

type Msg = { message: string; isUser: boolean; timestamp: string; reaction?: 'up' | 'down' | null };

const suggestions = [
  "Summarize this text",
  "Write an email draft",
  "Generate ideas for a post",
  "Explain a concept simply"
];

const ChatPage: React.FC = () => {
  const [messages, setMessages] = useState<Array<Msg>>([]);
  const [input, setInput] = useState("");
  const listRef = useRef<HTMLDivElement>(null);

  const send = () => {
    const text = input.trim();
    if (!text) return;
    const ts = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const userMsg: Msg = { message: text, isUser: true, timestamp: ts, reaction: null };
    const aiMsg: Msg = { message: "Smart reply will be given on ai integration", isUser: false, timestamp: ts, reaction: null };
    setMessages((prev) => [...prev, userMsg, aiMsg]);
    setInput("");
  };

  const setReaction = (index: number, reaction: 'up' | 'down') => {
    setMessages((prev) => prev.map((m, i) => {
      if (i !== index) return m;
      if (m.isUser) return m;
      return { ...m, reaction: m.reaction === reaction ? null : reaction };
    }));
  };

  useEffect(() => {
    const el = listRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages.length]);

  return (
    <div className="chatgpt-shell">
      <div className="navbar">
        <div className="nav-left">
          <div className="logo-f">F</div>
          FloatChat
        </div>
        <div className="nav-actions">
          <ThemeToggle />
          <Link className="nav-btn" to="/signin">Log in</Link>
          <Link className="nav-btn primary" to="/signin">Sign up</Link>
        </div>
      </div>

      <div className="chatgpt-main" ref={listRef}>
        <div className="chatgpt-container">
          <div className="chat-header">
            <div className="chat-title">Welcome back</div>
            <div className="chat-subtitle">Ask anything or pick a suggestion to get started.</div>
            {messages.length === 0 && (
              <div className="suggestions">
                {suggestions.map((s) => (
                  <button key={s} className="suggestion" onClick={() => setInput(s)}>{s}</button>
                ))}
              </div>
            )}
          </div>

          {messages.length === 0 ? (
            <div className="message-row assistant">
              <div className="message-avatar img"><img src={bot} alt="AI" /></div>
              <div className="message-content">
                <div className="bubble">
                  <div className="message-text">How can I help you today?</div>
                </div>
                <div className="bubble-meta">{new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
                <div className="assistant-actions">
                  <button className="assistant-action" aria-label="Like"><FaRegThumbsUp size={14} /></button>
                  <button className="assistant-action" aria-label="Dislike"><FaRegThumbsDown size={14} /></button>
                </div>
              </div>
            </div>
          ) : null}

          {messages.map((m, i) => (
            <div key={i} className={`message-row ${m.isUser ? 'user' : 'assistant'}`}>
              <div className={m.isUser ? "message-avatar" : "message-avatar img"}>{m.isUser ? 'U' : <img src={bot} alt="AI" />}</div>
              <div className="message-content">
                {m.isUser ? (
                  <>
                    <div className="bubble">
                      <div className="message-text">{m.message}</div>
                    </div>
                    <div className="bubble-meta">{m.timestamp}</div>
                  </>
                ) : (
                  <>
                    <div className="bubble">
                      <div className="message-text">{m.message}</div>
                    </div>
                    <div className="bubble-meta">{m.timestamp}</div>
                    <div className="assistant-actions">
                      <button className={`assistant-action ${m.reaction === 'up' ? 'active' : ''}`} aria-label="Like" onClick={() => setReaction(i, 'up')}><FaRegThumbsUp size={14} /></button>
                      <button className={`assistant-action ${m.reaction === 'down' ? 'active' : ''}`} aria-label="Dislike" onClick={() => setReaction(i, 'down')}><FaRegThumbsDown size={14} /></button>
                    </div>
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="chatgpt-composer">
        <div className="composer-inner">
          <div className="composer-pill">
            <button className="composer-icon" aria-label="Attach file"><FaPaperclip size={16} /></button>
            <input
              className="composer-input"
              placeholder="Type your message here..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter') send(); }}
            />
            <button className="composer-icon" aria-label="Emoji"><FaRegSmile size={16} /></button>
            <button className="composer-icon" aria-label="Voice"><FaMicrophone size={16} /></button>
          </div>
          <button className="composer-send" onClick={send}>➤</button>
        </div>
      </div>
    </div>
  );
};

export default ChatPage; 

const ThemeToggle: React.FC = () => {
  const { theme, toggleTheme } = useTheme();
  return (
    <button className="nav-btn" onClick={toggleTheme} aria-label="Toggle theme">
      {theme === 'dark' ? 'Light' : 'Dark'} mode
    </button>
  );
};