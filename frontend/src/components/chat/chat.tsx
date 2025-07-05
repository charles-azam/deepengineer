
import React from 'react';
import ChatMessage from './chat-message';
import { useChat } from '@/context/ChatContext';

const Chat: React.FC = () => {
  const { messages } = useChat();

  return (
    <div className="flex-1 p-4 overflow-y-auto">
      {messages.map((message) => (
        <ChatMessage key={message.id} message={message} />
      ))}
    </div>
  );
};

export default Chat;
