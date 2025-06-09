
import { useState, useEffect } from 'react';
import { AuthScreen } from '../components/AuthScreen';
import { MainApp } from '../components/MainApp';

const Index = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check if user is already authenticated
    const token = localStorage.getItem('access_token');
    if (token) {
      setIsAuthenticated(true);
    }
    setIsLoading(false);
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {isAuthenticated ? (
        <MainApp onLogout={() => setIsAuthenticated(false)} />
      ) : (
        <AuthScreen onLogin={() => setIsAuthenticated(true)} />
      )}
    </div>
  );
};

export default Index;
