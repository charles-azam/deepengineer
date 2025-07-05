
import React, { createContext, useState, useContext, ReactNode } from 'react';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
}

interface ChatContextType {
  messages: Message[];
  addMessage: (message: Message) => void;
  updateMessage: (id: string, newText: string) => void;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const ChatProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [messages, setMessages] = useState<Message[]>([
    { id: '1', text: 'Hello, how can I help you?', sender: 'bot' },
  ]);

  const addMessage = (message: Message) => {
    setMessages((prevMessages) => [...prevMessages, message]);
  };

  const updateMessage = (id: string, newText: string) => {
    setMessages((prevMessages) =>
      prevMessages.map((msg) => (msg.id === id ? { ...msg, text: newText } : msg))
    );
  };

  return (
    <ChatContext.Provider value={{ messages, addMessage, updateMessage }}>
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => {
  const context = useContext(ChatContext);
  if (context === undefined) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};
