
import React from 'react';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/context/AuthContext';

const Header: React.FC = () => {
  const { user, signInWithGoogle, signOut } = useAuth();

  return (
    <header className="flex items-center justify-between p-4 border-b">
      <h1 className="text-xl font-bold">DeepSearch</h1>
      <div>
        {user ? (
          <div className="flex items-center space-x-2">
            <span>Hello, {user.email}</span>
            <Button onClick={signOut}>Logout</Button>
          </div>
        ) : (
          <Button onClick={signInWithGoogle}>Login with Google</Button>
        )}
      </div>
    </header>
  );
};

export default Header;
