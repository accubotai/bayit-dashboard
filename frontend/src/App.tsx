import { useState, useEffect } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MapView } from './components/MapView';
import { LoginPage } from './components/LoginPage';

const queryClient = new QueryClient();

function App() {
  const [authenticated, setAuthenticated] = useState<boolean | null>(null);

  useEffect(() => {
    fetch('/api/auth/check', { credentials: 'include' })
      .then(res => setAuthenticated(res.ok))
      .catch(() => setAuthenticated(false));
  }, []);

  // Loading state while checking auth
  if (authenticated === null) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <p className="text-gray-500">Loading...</p>
      </div>
    );
  }

  if (!authenticated) {
    return <LoginPage onLogin={() => setAuthenticated(true)} />;
  }

  return (
    <QueryClientProvider client={queryClient}>
      <div className="w-full h-screen">
        <MapView />
      </div>
    </QueryClientProvider>
  );
}

export default App;
