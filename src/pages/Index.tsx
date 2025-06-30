
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Bot, Sparkles, ArrowRight } from "lucide-react";

const Index = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center p-4">
      <div className="max-w-4xl mx-auto text-center">
        <div className="mb-8 flex justify-center">
          <div className="relative">
            <div className="absolute inset-0 bg-blue-500 rounded-full blur-xl opacity-20 animate-pulse"></div>
            <Bot className="h-24 w-24 text-blue-400 relative z-10" />
          </div>
        </div>
        
        <h1 className="text-6xl font-bold text-white mb-6 tracking-tight">
          AI Assistant
          <span className="text-blue-400 ml-2">
            <Sparkles className="inline h-12 w-12" />
          </span>
        </h1>
        
        <p className="text-xl text-slate-300 mb-12 max-w-2xl mx-auto leading-relaxed">
          Experience the future of intelligent conversation with our advanced AI assistant. 
          Seamless, powerful, and designed for productivity.
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Button 
            onClick={() => navigate('/login')}
            size="lg"
            className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-xl font-semibold transition-all duration-200 transform hover:scale-105"
          >
            Get Started
            <ArrowRight className="ml-2 h-5 w-5" />
          </Button>
          
          <Button 
            onClick={() => navigate('/signup')}
            variant="outline"
            size="lg"
            className="border-slate-600 text-slate-300 hover:bg-slate-800 px-8 py-4 rounded-xl font-semibold transition-all duration-200"
          >
            Create Account
          </Button>
        </div>
      </div>
    </div>
  );
};

export default Index;
