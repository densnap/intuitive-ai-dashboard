
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Bot, Sparkles, ArrowRight, MessageSquare, Users, Zap } from "lucide-react";

const Index = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-gray-100 flex items-center justify-center p-4">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <div className="mx-auto mb-8 w-20 h-20 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center">
            <Bot className="h-10 w-10 text-white" />
          </div>
          
          <h1 className="text-6xl font-bold text-gray-900 mb-6 tracking-tight">
            AI Assistant
            <span className="text-purple-500 ml-2">
              <Sparkles className="inline h-12 w-12" />
            </span>
          </h1>
          
          <p className="text-xl text-gray-600 mb-12 max-w-3xl mx-auto leading-relaxed">
            Experience the future of intelligent conversation with our advanced AI assistant. 
            Seamless, powerful, and designed for productivity.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
            <Button 
              onClick={() => navigate('/login')}
              size="lg"
              className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white px-8 py-4 rounded-xl font-semibold transition-all duration-200 transform hover:scale-105 h-14"
            >
              Get Started
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
            
            <Button 
              onClick={() => navigate('/signup')}
              variant="outline"
              size="lg"
              className="border-gray-300 text-gray-700 hover:bg-gray-50 px-8 py-4 rounded-xl font-semibold transition-all duration-200 h-14"
            >
              Create Account
            </Button>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
          <div className="text-center p-6 bg-white/50 backdrop-blur-sm rounded-2xl border border-gray-200 hover:shadow-lg transition-all duration-200">
            <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center mx-auto mb-4">
              <MessageSquare className="h-6 w-6 text-purple-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Smart Conversations</h3>
            <p className="text-gray-600">Engage in natural, intelligent conversations with advanced AI capabilities.</p>
          </div>

          <div className="text-center p-6 bg-white/50 backdrop-blur-sm rounded-2xl border border-gray-200 hover:shadow-lg transition-all duration-200">
            <div className="w-12 h-12 bg-pink-100 rounded-xl flex items-center justify-center mx-auto mb-4">
              <Users className="h-6 w-6 text-pink-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Team Collaboration</h3>
            <p className="text-gray-600">Work together with your team in shared AI-powered workspaces.</p>
          </div>

          <div className="text-center p-6 bg-white/50 backdrop-blur-sm rounded-2xl border border-gray-200 hover:shadow-lg transition-all duration-200">
            <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center mx-auto mb-4">
              <Zap className="h-6 w-6 text-purple-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Lightning Fast</h3>
            <p className="text-gray-600">Get instant responses and quick solutions to boost your productivity.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Index;
