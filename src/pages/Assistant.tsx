import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Bot, Send, Menu, X, Plus, Search, MoreHorizontal, User, Settings, LogOut, MessageSquare, Paperclip, Sparkles } from "lucide-react";
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
  const [searchQuery, setSearchQuery] = useState("");
  const [inputFocused, setInputFocused] = useState(false);
  const [showSuggestedQueries, setShowSuggestedQueries] = useState(false);
  
  const [chats, setChats] = useState<Chat[]>([
    {
      id: "1",
      title: "New Thread",
      lastMessage: "",
      timestamp: new Date(),
      messages: []
    }
  ]);

  const currentChat = chats.find(chat => chat.id === currentChatId);
  const filteredChats = chats.filter(chat => 
    chat.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    chat.lastMessage.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const hasMessages = currentChat?.messages && currentChat.messages.length > 0;
  const showGreeting = !hasMessages && !inputFocused && !currentInput.trim();

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
    setInputFocused(false);
    setIsTyping(true);
    setShowSuggestedQueries(true);

    // Simulate AI response
    setTimeout(() => {
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: "I'm here to help you with any questions or tasks you might have. Whether you need assistance with writing, analysis, problem-solving, or creative projects, I'm ready to provide thoughtful and helpful responses.",
        sender: 'assistant',
        timestamp: new Date()
      };

      setChats(prev => prev.map(chat => 
        chat.id === currentChatId 
          ? { 
              ...chat, 
              messages: [...chat.messages, assistantMessage],
              lastMessage: assistantMessage.content.substring(0, 50) + "...",
              title: userMessage.content.substring(0, 30) + "..."
            }
          : chat
      ));
      setIsTyping(false);
    }, 1500);
  };

  const handleNewChat = () => {
    const newChat: Chat = {
      id: Date.now().toString(),
      title: "New Thread",
      lastMessage: "",
      timestamp: new Date(),
      messages: []
    };
    
    setChats(prev => [newChat, ...prev]);
    setCurrentChatId(newChat.id);
    setInputFocused(false);
    setCurrentInput("");
    setShowSuggestedQueries(false);
    
    toast({
      title: "New Thread Created",
      description: "Start a fresh conversation"
    });
  };

  const handleDeleteChat = (chatId: string) => {
    setChats(prev => prev.filter(chat => chat.id !== chatId));
    if (currentChatId === chatId && chats.length > 1) {
      setCurrentChatId(chats.find(chat => chat.id !== chatId)?.id || "");
    }
    
    toast({
      title: "Thread Deleted",
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

  const handleSuggestedQuery = (query: string) => {
    setCurrentInput(query);
    setInputFocused(true);
  };

  const suggestedQueries = [
    { text: "Write a to-do list for a personal project", icon: "👤" },
    { text: "Generate an email to reply to a job offer", icon: "📧" },
    { text: "Summarize this article in one paragraph", icon: "📋" },
    { text: "How does AI work in a technical capacity", icon: "⚙️" }
  ];

  const rightSideSuggestions = [
    "Create a marketing strategy",
    "Explain quantum computing",
    "Write a business proposal",
    "Analyze market trends",
    "Generate code snippets",
    "Plan a project timeline"
  ];

  return (
    <div className="h-screen bg-gray-50 flex overflow-hidden">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'w-80' : 'w-0'} transition-all duration-300 bg-white border-r border-gray-200 flex flex-col overflow-hidden shadow-sm`}>
        {/* Sidebar Content */}
        <div className="p-4 border-b border-gray-100">
          <Button 
            onClick={handleNewChat}
            className="w-full bg-black hover:bg-gray-800 text-white h-12 rounded-xl font-medium"
          >
            <Plus className="h-4 w-4 mr-2" />
            New Thread
          </Button>
        </div>
        
        <div className="p-4 border-b border-gray-100">
          <div className="relative">
            <Search className="h-4 w-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <Input 
              placeholder="Search thread"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 bg-gray-50 border-gray-200 h-10 rounded-lg focus:bg-white"
            />
          </div>
        </div>
        
        <div className="flex-1 overflow-hidden">
          <ScrollArea className="h-full">
            <div className="p-2 space-y-1">
              {filteredChats.map((chat) => (
                <div
                  key={chat.id}
                  className={`group flex items-center justify-between p-3 rounded-lg cursor-pointer transition-all hover:bg-gray-50 ${
                    currentChatId === chat.id ? 'bg-gray-100 border border-gray-200' : ''
                  }`}
                  onClick={() => setCurrentChatId(chat.id)}
                >
                  <div className="flex items-center space-x-3 flex-1 min-w-0">
                    <MessageSquare className="h-4 w-4 text-gray-400 flex-shrink-0" />
                    <div className="min-w-0 flex-1">
                      <div className="text-sm font-medium text-gray-900 truncate">
                        {chat.title}
                      </div>
                      <div className="text-xs text-gray-500 truncate">
                        {chat.lastMessage || "No messages yet"}
                      </div>
                    </div>
                  </div>
                  
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button 
                        variant="ghost" 
                        size="sm"
                        className="opacity-0 group-hover:opacity-100 h-6 w-6 p-0 text-gray-400 hover:text-gray-600"
                      >
                        <MoreHorizontal className="h-3 w-3" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent className="bg-white border-gray-200 shadow-lg">
                      <DropdownMenuItem className="text-gray-700 hover:bg-gray-50">
                        Rename Thread
                      </DropdownMenuItem>
                      <DropdownMenuItem 
                        className="text-red-600 hover:bg-red-50"
                        onClick={() => handleDeleteChat(chat.id)}
                      >
                        Delete Thread
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              ))}
            </div>
          </ScrollArea>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex">
        {/* Chat Area */}
        <div className={`${showSuggestedQueries ? 'flex-1' : 'w-full'} flex flex-col bg-white relative transition-all duration-300`}>
          {/* Header */}
          <div className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6 relative z-10">
            <div className="flex items-center space-x-4">
              <Button 
                variant="ghost" 
                size="sm"
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="text-gray-600 hover:text-gray-900 hover:bg-gray-100 h-10 w-10 p-0 rounded-lg"
              >
                {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
              </Button>
              
              <div className="flex items-center space-x-3">
                <div className="text-sm font-medium text-gray-900">ChatGPT 4o</div>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <Button
                variant="ghost"
                size="sm"
                className="text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg px-3 h-10"
              >
                <User className="h-4 w-4 mr-2" />
                Invite
              </Button>
              
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="relative h-10 w-10 rounded-full hover:bg-gray-100">
                    <Avatar className="h-10 w-10">
                      <AvatarFallback className="bg-gray-200 text-gray-700 text-sm font-medium">
                        JD
                      </AvatarFallback>
                    </Avatar>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent className="w-56 bg-white border-gray-200 shadow-lg" align="end">
                  <div className="px-4 py-3">
                    <p className="text-sm font-medium text-gray-900">Jason</p>
                    <p className="text-xs text-gray-500">jason@example.com</p>
                    <Badge variant="secondary" className="mt-1 bg-purple-100 text-purple-700 text-xs">
                      Admin
                    </Badge>
                  </div>
                  <DropdownMenuSeparator className="bg-gray-200" />
                  <DropdownMenuItem className="text-gray-700 hover:bg-gray-50">
                    <User className="mr-2 h-4 w-4" />
                    Profile
                  </DropdownMenuItem>
                  <DropdownMenuItem className="text-gray-700 hover:bg-gray-50">
                    <Settings className="mr-2 h-4 w-4" />
                    Settings
                  </DropdownMenuItem>
                  <DropdownMenuSeparator className="bg-gray-200" />
                  <DropdownMenuItem 
                    className="text-red-600 hover:bg-red-50"
                    onClick={handleLogout}
                  >
                    <LogOut className="mr-2 h-4 w-4" />
                    Logout
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>

          {/* Chat Content */}
          <div className="flex-1 flex flex-col overflow-hidden relative">
            {/* Greeting Section - Centered */}
            {showGreeting && (
              <div className="flex-1 flex flex-col items-center justify-center px-8 transition-all duration-500 ease-in-out">
                {/* Floating AI Orb */}
                <div className="relative mb-8">
                  <div className="w-20 h-20 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center shadow-lg animate-pulse">
                    <Sparkles className="h-10 w-10 text-white" />
                  </div>
                  <div className="absolute -inset-4 bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded-full blur-xl animate-pulse"></div>
                </div>
                
                <h1 className="text-4xl font-bold text-gray-900 mb-2 text-center">
                  Good Afternoon, Jason
                </h1>
                <p className="text-xl text-gray-600 mb-12 text-center">
                  What's on <span className="text-purple-600">your mind?</span>
                </p>

                {/* Centered Input */}
                <div className="w-full max-w-2xl mb-8">
                  <div className="relative">
                    <Input
                      placeholder="Ask AI a question or make a request..."
                      value={currentInput}
                      onChange={(e) => setCurrentInput(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                      onFocus={() => setInputFocused(true)}
                      className="w-full h-14 pl-4 pr-20 bg-white border-gray-300 rounded-2xl text-gray-700 placeholder:text-gray-500 focus:border-purple-300 focus:outline-none focus:ring-2 focus:ring-purple-500/20"
                    />
                    <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center space-x-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-8 w-8 p-0 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg"
                      >
                        <Paperclip className="h-4 w-4" />
                      </Button>
                      <Button
                        onClick={handleSendMessage}
                        disabled={!currentInput.trim() || isTyping}
                        className="h-8 w-8 p-0 bg-black hover:bg-gray-800 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        <Send className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </div>

                {/* Suggested Queries - Centered Grid */}
                <div className="w-full max-w-4xl">
                  <div className="text-xs text-gray-500 text-center mb-4 uppercase tracking-wide">
                    Get started with an example below
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    {suggestedQueries.map((query, index) => (
                      <button
                        key={index}
                        onClick={() => handleSuggestedQuery(query.text)}
                        className="p-4 bg-white border border-gray-200 rounded-xl hover:border-gray-300 hover:shadow-sm transition-all text-left group"
                      >
                        <div className="text-2xl mb-2">{query.icon}</div>
                        <p className="text-sm text-gray-700 group-hover:text-gray-900">{query.text}</p>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Chat Messages */}
            {(hasMessages || (!showGreeting && (inputFocused || currentInput.trim()))) && (
              <>
                <ScrollArea className="flex-1 p-6">
                  <div className="max-w-4xl mx-auto space-y-6">
                    {currentChat?.messages.map((message) => (
                      <div
                        key={message.id}
                        className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                      >
                        <div className={`flex space-x-4 max-w-3xl ${message.sender === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                          <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                            message.sender === 'user' 
                              ? 'bg-gray-200 text-gray-700' 
                              : 'bg-gradient-to-br from-purple-500 to-pink-500 text-white'
                          }`}>
                            {message.sender === 'user' ? (
                              <User className="h-4 w-4" />
                            ) : (
                              <Bot className="h-4 w-4" />
                            )}
                          </div>
                          
                          <div className={`rounded-2xl p-4 ${
                            message.sender === 'user'
                              ? 'bg-gray-100 text-gray-900'
                              : 'bg-white text-gray-900 border border-gray-100'
                          }`}>
                            <p className="text-sm leading-relaxed">{message.content}</p>
                            <p className="text-xs text-gray-500 mt-2">
                              {message.timestamp.toLocaleTimeString()}
                            </p>
                          </div>
                        </div>
                      </div>
                    ))}
                    
                    {isTyping && (
                      <div className="flex justify-start">
                        <div className="flex space-x-4 max-w-3xl">
                          <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center flex-shrink-0">
                            <Bot className="h-4 w-4 text-white" />
                          </div>
                          <div className="bg-white rounded-2xl p-4 border border-gray-100">
                            <div className="flex space-x-1">
                              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </ScrollArea>

                {/* Sticky Input at bottom */}
                <div className="border-t border-gray-200 p-6 bg-white">
                  <div className="max-w-4xl mx-auto">
                    <div className="relative">
                      <Input
                        placeholder="Ask AI a question or make a request..."
                        value={currentInput}
                        onChange={(e) => setCurrentInput(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                        className="w-full h-14 pl-4 pr-20 bg-white border-gray-300 rounded-2xl text-gray-700 placeholder:text-gray-500 focus:border-purple-300 focus:outline-none focus:ring-2 focus:ring-purple-500/20"
                      />
                      <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center space-x-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-8 w-8 p-0 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg"
                        >
                          <Paperclip className="h-4 w-4" />
                        </Button>
                        <Button
                          onClick={handleSendMessage}
                          disabled={!currentInput.trim() || isTyping}
                          className="h-8 w-8 p-0 bg-black hover:bg-gray-800 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          <Send className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Right Sidebar - Suggested Queries */}
        {showSuggestedQueries && (
          <div className="w-80 bg-gray-50 border-l border-gray-200 p-6 overflow-y-auto">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Suggested Prompts</h3>
            <div className="space-y-3">
              {rightSideSuggestions.map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => handleSuggestedQuery(suggestion)}
                  className="w-full text-left p-3 bg-white border border-gray-200 rounded-lg hover:border-purple-300 hover:bg-purple-50 transition-all group"
                >
                  <p className="text-sm text-gray-700 group-hover:text-purple-700">{suggestion}</p>
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Assistant;
