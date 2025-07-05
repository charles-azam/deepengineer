
import React from 'react';
import { useAgentStatus } from '@/context/AgentStatusContext';

const Sidebar: React.FC = () => {
  const { status } = useAgentStatus();

  return (
    <aside className="p-4 border-r">
      <h2 className="text-lg font-semibold">Agent Status</h2>
      <p>{status}</p>
    </aside>
  );
};

export default Sidebar;
