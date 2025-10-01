import { useState, useEffect } from 'react';
import { ManthanChat } from './ManthanChat';
import { Button } from '@/components/ui/button';
import { Sparkles } from 'lucide-react';

export function ManthanButton() {
  const [isOpen, setIsOpen] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isHovered, setIsHovered] = useState(false);

  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Toggle chat with Ctrl+K or Cmd+K
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        setIsOpen(prev => !prev);
      }
      // Close with Escape
      if (e.key === 'Escape' && isOpen) {
        setIsOpen(false);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen]);

  const handleToggleChat = () => {
    setIsOpen(prev => {
      if (prev) {
        setUnreadCount(0);
      }
      return !prev;
    });
  };

  // Notify when there are unread messages
  const handleNewMessage = () => {
    if (!isOpen) {
      setUnreadCount(prev => prev + 1);
    }
  };

  return (
    <div className="relative">
      <Button
        variant={isOpen ? 'outline' : 'default'}
        size="sm"
        onClick={handleToggleChat}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        className="relative group transition-all duration-200"
        aria-label="Open Manthan AI Chat"
      >
        <div className="flex items-center gap-2">
          <Sparkles className={`w-4 h-4 transition-transform ${isHovered ? 'animate-pulse' : ''}`} />
          <span className="hidden sm:inline">Manthan AI</span>
          <kbd className="hidden md:inline-flex items-center gap-1 rounded bg-muted px-1.5 font-mono text-[10px] font-medium text-muted-foreground ml-2">
            <span className="text-xs">⌘</span>K
          </kbd>
        </div>
        
        {unreadCount > 0 && (
          <span className="absolute -top-2 -right-2 flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-xs font-medium text-white">
            {unreadCount}
          </span>
        )}
      </Button>

      {isOpen && (
        <ManthanChat 
          onClose={() => setIsOpen(false)}
          onNewMessage={handleNewMessage}
        />
      )}
    </div>
  );
}
