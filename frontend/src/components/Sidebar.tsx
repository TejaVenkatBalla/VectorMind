
import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { 
  MessageSquare, 
  FileText, 
  LogOut, 
  Plus,
  Clock,
  User
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { API_BASE_URL } from '@/config';

interface SidebarProps {
  currentView: 'chat' | 'files';
  onViewChange: (view: 'chat' | 'files') => void;
  onLogout: () => void;
  onCloseSidebar: () => void;
}

interface ChatHistory {
  id: string;
  question: string;
  answer: string;
  created_at: string;
}

export const Sidebar = ({ currentView, onViewChange, onLogout, onCloseSidebar }: SidebarProps) => {
  const [chatHistory, setChatHistory] = useState<ChatHistory[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    if (currentView === 'chat') {
      fetchChatHistory();
    }
  }, [currentView]);

  const fetchChatHistory = async () => {
    setIsLoading(true);
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/api/bot`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setChatHistory(data.slice(0, 10)); // Show only recent 10 chats
      }
    } catch (error) {
      console.error('Failed to fetch chat history:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    toast({
      title: "Logged out",
      description: "You've been logged out successfully.",
    });
    onLogout();
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 1) return 'Today';
    if (diffDays === 2) return 'Yesterday';
    if (diffDays <= 7) return `${diffDays - 1} days ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="h-full bg-secondary/50 border-r border-border flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-border">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-8 h-8 bg-gradient-to-br from-primary to-primary/60 rounded-lg flex items-center justify-center">
            <MessageSquare className="w-4 h-4 text-white" />
          </div>
          <h2 className="font-semibold gradient-text">RAG Chat</h2>
        </div>

        {/* Navigation buttons */}
        <div className="flex gap-2">
          <Button
            variant={currentView === 'chat' ? 'default' : 'ghost'}
            size="sm"
            className="flex-1"
            onClick={() => {
              onViewChange('chat');
              onCloseSidebar();
            }}
          >
            <MessageSquare className="w-4 h-4 mr-2" />
            Chat
          </Button>
          <Button
            variant={currentView === 'files' ? 'default' : 'ghost'}
            size="sm"
            className="flex-1"
            onClick={() => {
              onViewChange('files');
              onCloseSidebar();
            }}
          >
            <FileText className="w-4 h-4 mr-2" />
            Files
          </Button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-hidden">
        {currentView === 'chat' && (
          <div className="h-full flex flex-col">
            <div className="p-4">
              <div className="flex items-center gap-2 text-sm text-muted-foreground mb-3">
                <Clock className="w-4 h-4" />
                Recent Chats
              </div>
            </div>

            <ScrollArea className="flex-1 px-4">
              {isLoading ? (
                <div className="space-y-3">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="h-16 bg-muted/30 rounded-lg animate-pulse" />
                  ))}
                </div>
              ) : chatHistory.length > 0 ? (
                <div className="space-y-2">
                  {chatHistory.map((chat) => (
                    <div
                      key={chat.id}
                      className="p-3 rounded-lg bg-muted/30 hover:bg-muted/50 transition-colors cursor-pointer border border-transparent hover:border-border"
                    >
                      <p className="text-sm font-medium text-foreground line-clamp-2 mb-1">
                        {chat.question}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {formatDate(chat.created_at)}
                      </p>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <MessageSquare className="w-8 h-8 text-muted-foreground mx-auto mb-3" />
                  <p className="text-sm text-muted-foreground">
                    No chat history yet.
                    <br />
                    Start a conversation!
                  </p>
                </div>
              )}
            </ScrollArea>
          </div>
        )}

        {currentView === 'files' && (
          <div className="p-4">
            <div className="text-center py-8">
              <FileText className="w-8 h-8 text-muted-foreground mx-auto mb-3" />
              <p className="text-sm text-muted-foreground">
                Switch to Files tab to manage your documents
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-border">
        <Button
          variant="ghost"
          size="sm"
          className="w-full justify-start text-muted-foreground hover:text-foreground"
          onClick={handleLogout}
        >
          <LogOut className="w-4 h-4 mr-2" />
          Sign out
        </Button>
      </div>
    </div>
  );
};
