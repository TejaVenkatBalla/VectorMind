
import { useState, useEffect } from 'react';
import { Sidebar } from './Sidebar';
import { ChatInterface } from './ChatInterface';
import { FileManager } from './FileManager';
import { Button } from '@/components/ui/button';
import { Menu, X } from 'lucide-react';

interface MainAppProps {
  onLogout: () => void;
}

export const MainApp = ({ onLogout }: MainAppProps) => {
  const [currentView, setCurrentView] = useState<'chat' | 'files'>('chat');
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
      if (window.innerWidth < 768) {
        setIsSidebarOpen(false);
      }
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  return (
    <div className="flex h-screen bg-background">
      {/* Mobile menu button */}
      {isMobile && (
        <Button
          variant="ghost"
          size="icon"
          className="fixed top-4 left-4 z-50 md:hidden"
          onClick={() => setIsSidebarOpen(!isSidebarOpen)}
        >
          {isSidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </Button>
      )}

      {/* Sidebar */}
      <div className={`
        ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        ${isMobile ? 'fixed inset-y-0 left-0 z-40' : 'relative'}
        w-80 transition-transform duration-300 ease-in-out
      `}>
        <Sidebar
          currentView={currentView}
          onViewChange={setCurrentView}
          onLogout={onLogout}
          onCloseSidebar={() => isMobile && setIsSidebarOpen(false)}
        />
      </div>

      {/* Mobile overlay */}
      {isMobile && isSidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-30"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0">
        {currentView === 'chat' ? (
          <ChatInterface />
        ) : (
          <FileManager />
        )}
      </div>
    </div>
  );
};
