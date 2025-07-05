
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import './index.css';
import App from './App.tsx';
import { AgentStatusProvider } from './context/AgentStatusContext';
import { ChatProvider } from './context/ChatContext';
import { AuthProvider } from './context/AuthContext';
import { StripeProvider } from './context/StripeContext';

const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
  },
]);

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AuthProvider>
      <AgentStatusProvider>
        <ChatProvider>
          <StripeProvider>
            <RouterProvider router={router} />
          </StripeProvider>
        </ChatProvider>
      </AgentStatusProvider>
    </AuthProvider>
  </StrictMode>
);

