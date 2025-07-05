
import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useChat } from '@/context/ChatContext';
import { useAgentStatus } from '@/context/AgentStatusContext';

const ChatInput: React.FC = () => {
  const [inputValue, setInputValue] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const { addMessage } = useChat();
  const { setStatus } = useAgentStatus();

  const handleSendMessage = () => {
    if (inputValue.trim() || selectedFile) {
      if (inputValue.trim()) {
        addMessage({ id: Date.now().toString(), text: inputValue, sender: 'user' });
      }
      if (selectedFile) {
        addMessage({ id: Date.now().toString() + '-file', text: `Uploaded file: ${selectedFile.name}`, sender: 'user' });
      }
      setInputValue('');
      setSelectedFile(null);
      setStatus('Thinking...'); // Set agent status when message is sent
      // Here you would typically send the message and file to the backend and handle the response
      // For now, let's simulate a bot response after a short delay
      setTimeout(() => {
        addMessage({ id: Date.now().toString(), text: 'This is a simulated bot response.', sender: 'bot' });
        setStatus('Idle'); // Reset agent status after response
      }, 1000);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleSendMessage();
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    } else {
      setSelectedFile(null);
    }
  };

  return (
    <div className="p-4 border-t">
      <div className="flex items-center space-x-2">
        <Input
          type="file"
          accept=".pdf"
          onChange={handleFileChange}
          className="w-auto"
        />
        <Input
          type="text"
          placeholder="Ask a question..."
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
        />
        <Button onClick={handleSendMessage}>Send</Button>
      </div>
    </div>
  );
};

export default ChatInput;
