
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Bot, Send, Menu, X, Plus, Search, MoreHorizontal, User, Settings, LogOut, MessageSquare } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
}

interface Chat {
  id: string;
  title: string;
  lastMessage: string;
  timestamp: Date;
  messages: Message[];
}

const Assistant = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [currentInput, setCurrentInput] = useState("");
  const [currentChatId, setCurrentChatId] = useState("1");
  const [isTyping, setIsTyping] = useState(false);
  
  const [chats, setChats] = useState<Chat[]>([
    {
      id: "1",
      title: "Welcome Chat",
      lastMessage: "Hello! How can I help you today?",
      timestamp: new Date(),
      messages: [
        {
          id: "1",
          content: "Hello! How can I help you today?",
          sender: 'assistant',
          timestamp: new Date()
        }
      ]
    }
  ]);

  const currentChat = chats.find(chat => chat.id === currentChatId);

  const handleSendMessage = async () => {
    if (!currentInput.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: currentInput,
      sender: 'user',
      timestamp: new Date()
    };

    // Add user message
    setChats(prev => prev.map(chat => 
      chat.id === currentChatId 
        ? { ...chat, messages: [...chat.messages, userMessage] }
        : chat
    ));

    setCurrentInput("");
    setIsTyping(true);

    // Simulate AI response
    setTimeout(() => {
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: "I'm an AI assistant UI demo. In a real implementation, I would connect to an AI service to provide intelligent responses to your questions and help you with various tasks.",
        sender: 'assistant',
        timestamp: new Date()
      };

      setChats(prev => prev.map(chat => 
        chat.id === currentChatId 
          ? { 
              ...chat, 
              messages: [...chat.messages, assistantMessage],
              lastMessage: assistantMessage.content.substring(0, 50) + "..."
            }
          : chat
      ));
      setIsTyping(false);
    }, 1500);
  };

  const handleNewChat = () => {
    const newChat: Chat = {
      id: Date.now().toString(),
      title: `New Chat ${chats.length + 1}`,
      lastMessage: "",
      timestamp: new Date(),
      messages: []
    };
    
    setChats(prev => [newChat, ...prev]);
    setCurrentChatId(newChat.id);
    
    toast({
      title: "New Chat Created",
      description: "Start a fresh conversation"
    });
  };

  const handleDeleteChat = (chatId: string) => {
    setChats(prev => prev.filter(chat => chat.id !== chatId));
    if (currentChatId === chatId && chats.length > 1) {
      setCurrentChatId(chats.find(chat => chat.id !== chatId)?.id || "");
    }
    
    toast({
      title: "Chat Deleted",
      description: "The conversation has been removed"
    });
  };

  const handleLogout = () => {
    toast({
      title: "Logged Out",
      description: "You have been successfully logged out"
    });
    navigate('/login');
  };

  return (
    <div className="h-screen bg-slate-900 flex">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'w-80' : 'w-0'} transition-all duration-300 bg-slate-800 border-r border-slate-700 flex flex-col overflow-hidden`}>
        <div className="p-4 border-b border-slate-700">
          <Button 
            onClick={handleNewChat}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white justify-start"
          >
            <Plus className="h-4 w-4 mr-2" />
            New Chat
          </Button>
        </div>
        
        <div className="p-4 border-b border-slate-700">
          <div className="relative">
            <Search className="h-4 w-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" />
            <Input 
              placeholder="Search conversations..."
              className="pl-10 bg-slate-700 border-slate-600 text-white placeholder:text-slate-400"
            />
          </div>
        </div>
        
        <div className="flex-1 overflow-hidden">
          <ScrollArea className="h-full">
            <div className="p-2 space-y-1">
              <div className="px-3 py-2 text-xs font-medium text-slate-400 uppercase tracking-wider">
                Recent Conversations
              </div>
              {chats.map((chat) => (
                <div
                  key={chat.id}
                  className={`group flex items-center justify-between p-3 rounded-lg cursor-pointer transition-colors ${
                    currentChatId === chat.id 
                      ? 'bg-blue-600/20 border border-blue-600/30' 
                      : 'hover:bg-slate-700/50'
                  }`}
                  onClick={() => setCurrentChatId(chat.id)}
                >
                  <div className="flex items-center space-x-3 flex-1 min-w-0">
                    <MessageSquare className="h-4 w-4 text-slate-400 flex-shrink-0" />
                    <div className="min-w-0 flex-1">
                      <div className="text-sm font-medium text-white truncate">
                        {chat.title}
                      </div>
                      <div className="text-xs text-slate-400 truncate">
                        {chat.lastMessage || "No messages yet"}
                      </div>
                    </div>
                  </div>
                  
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button 
                        variant="ghost" 
                        size="sm"
                        className="opacity-0 group-hover:opacity-100 h-6 w-6 p-0 text-slate-400 hover:text-white"
                      >
                        <MoreHorizontal className="h-3 w-3" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent className="bg-slate-700 border-slate-600">
                      <DropdownMenuItem className="text-slate-300 hover:bg-slate-600">
                        Rename Chat
                      </DropdownMenuItem>
                      <DropdownMenuItem 
                        className="text-red-400 hover:bg-slate-600"
                        onClick={() => handleDeleteChat(chat.id)}
                      >
                        Delete Chat
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              ))}
            </div>
          </ScrollArea>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="h-16 bg-slate-800 border-b border-slate-700 flex items-center justify-between px-6">
          <div className="flex items-center space-x-4">
            <Button 
              variant="ghost" 
              size="sm"
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="text-slate-400 hover:text-white"
            >
              {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </Button>
            
            <div className="flex items-center space-x-3">
              <div className="h-8 w-8 bg-blue-600 rounded-full flex items-center justify-center">
                <Bot className="h-5 w-5 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-semibold text-white">AI Assistant</h1>
                <p className="text-xs text-slate-400">Always ready to help</p>
              </div>
            </div>
          </div>
          
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="relative h-10 w-10 rounded-full">
                <Avatar className="h-10 w-10">
                  <AvatarFallback className="bg-blue-600 text-white">
                    <User className="h-5 w-5" />
                  </AvatarFallback>
                </Avatar>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-56 bg-slate-700 border-slate-600" align="end">
              <div className="px-4 py-3">
                <p className="text-sm font-medium text-white">John Doe</p>
                <p className="text-xs text-slate-400">john@example.com</p>
                <Badge variant="secondary" className="mt-1 bg-blue-600/20 text-blue-400">
                  Admin
                </Badge>
              </div>
              <DropdownMenuSeparator className="bg-slate-600" />
              <DropdownMenuItem className="text-slate-300 hover:bg-slate-600">
                <User className="mr-2 h-4 w-4" />
                Profile
              </DropdownMenuItem>
              <DropdownMenuItem className="text-slate-300 hover:bg-slate-600">
                <Settings className="mr-2 h-4 w-4" />
                Settings
              </DropdownMenuItem>
              <DropdownMenuSeparator className="bg-slate-600" />
              <DropdownMenuItem 
                className="text-red-400 hover:bg-slate-600"
                onClick={handleLogout}
              >
                <LogOut className="mr-2 h-4 w-4" />
                Logout
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        {/* Chat Area */}
        <div className="flex-1 flex flex-col">
          <ScrollArea className="flex-1 p-6">
            <div className="max-w-4xl mx-auto space-y-6">
              {currentChat?.messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div className={`flex space-x-3 max-w-2xl ${message.sender === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                    <div className={`h-8 w-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                      message.sender === 'user' 
                        ? 'bg-blue-600' 
                        : 'bg-slate-700'
                    }`}>
                      {message.sender === 'user' ? (
                        <User className="h-4 w-4 text-white" />
                      ) : (
                        <Bot className="h-4 w-4 text-slate-300" />
                      )}
                    </div>
                    
                    <div className={`rounded-lg p-4 ${
                      message.sender === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-slate-700 text-slate-100'
                    }`}>
                      <p className="text-sm leading-relaxed">{message.content}</p>
                      <p className="text-xs opacity-70 mt-2">
                        {message.timestamp.toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
              
              {isTyping && (
                <div className="flex justify-start">
                  <div className="flex space-x-3 max-w-2xl">
                    <div className="h-8 w-8 bg-slate-700 rounded-full flex items-center justify-center flex-shrink-0">
                      <Bot className="h-4 w-4 text-slate-300" />
                    </div>
                    <div className="bg-slate-700 rounded-lg p-4">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                        <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </ScrollArea>
          
          {/* Input Area */}
          <div className="border-t border-slate-700 p-6">
            <div className="max-w-4xl mx-auto">
              <div className="flex space-x-4">
                <div className="flex-1 relative">
                  <Input
                    placeholder="Type your message here..."
                    value={currentInput}
                    onChange={(e) => setCurrentInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                    className="pr-12 bg-slate-700 border-slate-600 text-white placeholder:text-slate-400 focus:border-blue-500"
                  />
                  <Button
                    onClick={handleSendMessage}
                    disabled={!currentInput.trim() || isTyping}
                    size="sm"
                    className="absolute right-2 top-1/2 transform -translate-y-1/2 h-8 w-8 p-0 bg-blue-600 hover:bg-blue-700"
                  >
                    <Send className="h-4 w-4" />
                  </Button>
                </div>
              </div>
              
              <p className="text-xs text-slate-400 text-center mt-3">
                AI Assistant can make mistakes. Please verify important information.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Assistant;
