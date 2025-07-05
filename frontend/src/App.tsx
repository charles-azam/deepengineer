
import Header from '@/components/layout/header';
import Sidebar from '@/components/layout/sidebar';
import Chat from '@/components/chat/chat';
import ChatInput from '@/components/chat/chat-input';
import CheckoutForm from '@/components/payment/CheckoutForm';
import { useAuth } from '@/context/AuthContext';

function App() {
  const { user } = useAuth();

  return (
    <div className="flex flex-col h-screen">
      <Header />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <main className="flex flex-col flex-1">
          {user ? (
            <>
              <Chat />
              <ChatInput />
              <CheckoutForm />
            </>
          ) : (
            <div className="flex items-center justify-center flex-1">
              <p>Please log in to use the DeepSearch application.</p>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
