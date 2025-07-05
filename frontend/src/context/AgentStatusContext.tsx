
import React, { createContext, useState, useContext, ReactNode } from 'react';

interface AgentStatusContextType {
  status: string;
  setStatus: (status: string) => void;
}

const AgentStatusContext = createContext<AgentStatusContextType | undefined>(undefined);

export const AgentStatusProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [status, setStatus] = useState<string>('Idle');

  return (
    <AgentStatusContext.Provider value={{ status, setStatus }}>
      {children}
    </AgentStatusContext.Provider>
  );
};

export const useAgentStatus = () => {
  const context = useContext(AgentStatusContext);
  if (context === undefined) {
    throw new Error('useAgentStatus must be used within an AgentStatusProvider');
  }
  return context;
};
