import { cn } from "@/lib/utils";
import "./ChatMessage.css";

interface ChatMessageProps {
  message: string;
  isUser: boolean;
}

const ChatMessage = ({ message, isUser }: ChatMessageProps) => {
  return (
    <div className={cn("message-row", isUser ? "user" : "assistant")}>
      <div className="message-avatar">{isUser ? 'U' : 'AI'}</div>
      <div className="message-content">
        <div className="bubble">
          <div className="message-text">{message}</div>
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;