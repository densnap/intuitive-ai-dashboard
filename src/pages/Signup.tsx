
import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Bot, Eye, EyeOff, Mail, Shield, User } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

const Signup = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [currentStep, setCurrentStep] = useState(1);
  const [showPassword, setShowPassword] = useState(false);
  const [formData, setFormData] = useState({
    email: "",
    otp: "",
    username: "",
    password: "",
    role: ""
  });

  const handleEmailSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.email) {
      toast({
        title: "Error",
        description: "Please enter your email address",
        variant: "destructive"
      });
      return;
    }
    
    toast({
      title: "OTP Sent",
      description: "Please check your email for the verification code"
    });
    setCurrentStep(2);
  };

  const handleOtpSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.otp) {
      toast({
        title: "Error",
        description: "Please enter the OTP code",
        variant: "destructive"
      });
      return;
    }
    
    toast({
      title: "Email Verified",
      description: "Please complete your profile"
    });
    setCurrentStep(3);
  };

  const handleFinalSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.username || !formData.password || !formData.role) {
      toast({
        title: "Error",
        description: "Please fill in all fields",
        variant: "destructive"
      });
      return;
    }
    
    toast({
      title: "Account Created",
      description: "Welcome to AI Assistant!"
    });
    navigate('/assistant');
  };

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <>
            <CardHeader className="text-center pb-8">
              <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-blue-600">
                <Mail className="h-8 w-8 text-white" />
              </div>
              <CardTitle className="text-2xl font-bold text-white">Email Verification</CardTitle>
              <CardDescription className="text-slate-400">
                Enter your email to get started
              </CardDescription>
            </CardHeader>
            
            <CardContent>
              <form onSubmit={handleEmailSubmit} className="space-y-6">
                <div className="space-y-2">
                  <Label htmlFor="email" className="text-slate-300">Email Address</Label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="Enter your email"
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    className="bg-slate-700 border-slate-600 text-white placeholder:text-slate-400 focus:border-blue-500"
                  />
                </div>
                
                <Button 
                  type="submit" 
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 rounded-lg font-semibold transition-all duration-200"
                >
                  Send Verification Code
                </Button>
              </form>
            </CardContent>
          </>
        );
        
      case 2:
        return (
          <>
            <CardHeader className="text-center pb-8">
              <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-green-600">
                <Shield className="h-8 w-8 text-white" />
              </div>
              <CardTitle className="text-2xl font-bold text-white">Enter OTP</CardTitle>
              <CardDescription className="text-slate-400">
                We sent a code to {formData.email}
              </CardDescription>
            </CardHeader>
            
            <CardContent>
              <form onSubmit={handleOtpSubmit} className="space-y-6">
                <div className="space-y-2">
                  <Label htmlFor="otp" className="text-slate-300">Verification Code</Label>
                  <Input
                    id="otp"
                    type="text"
                    placeholder="Enter 6-digit code"
                    value={formData.otp}
                    onChange={(e) => setFormData({...formData, otp: e.target.value})}
                    className="bg-slate-700 border-slate-600 text-white placeholder:text-slate-400 focus:border-blue-500 text-center text-lg tracking-widest"
                    maxLength={6}
                  />
                </div>
                
                <Button 
                  type="submit" 
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 rounded-lg font-semibold transition-all duration-200"
                >
                  Verify Code
                </Button>
                
                <Button 
                  type="button"
                  variant="ghost"
                  onClick={() => setCurrentStep(1)}
                  className="w-full text-slate-400 hover:text-slate-300"
                >
                  Back to Email
                </Button>
              </form>
            </CardContent>
          </>
        );
        
      case 3:
        return (
          <>
            <CardHeader className="text-center pb-8">
              <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-purple-600">
                <User className="h-8 w-8 text-white" />
              </div>
              <CardTitle className="text-2xl font-bold text-white">Complete Setup</CardTitle>
              <CardDescription className="text-slate-400">
                Create your account credentials
              </CardDescription>
            </CardHeader>
            
            <CardContent>
              <form onSubmit={handleFinalSubmit} className="space-y-6">
                <div className="space-y-2">
                  <Label htmlFor="username" className="text-slate-300">Username</Label>
                  <Input
                    id="username"
                    type="text"
                    placeholder="Choose a username"
                    value={formData.username}
                    onChange={(e) => setFormData({...formData, username: e.target.value})}
                    className="bg-slate-700 border-slate-600 text-white placeholder:text-slate-400 focus:border-blue-500"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="password" className="text-slate-300">Password</Label>
                  <div className="relative">
                    <Input
                      id="password"
                      type={showPassword ? "text" : "password"}
                      placeholder="Create a password"
                      value={formData.password}
                      onChange={(e) => setFormData({...formData, password: e.target.value})}
                      className="bg-slate-700 border-slate-600 text-white placeholder:text-slate-400 focus:border-blue-500 pr-10"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-300"
                    >
                      {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                </div>
                
                <div className="space-y-2">
                  <Label className="text-slate-300">Role</Label>
                  <Select onValueChange={(value) => setFormData({...formData, role: value})}>
                    <SelectTrigger className="bg-slate-700 border-slate-600 text-white">
                      <SelectValue placeholder="Select your role" />
                    </SelectTrigger>
                    <SelectContent className="bg-slate-700 border-slate-600">
                      <SelectItem value="admin">Admin</SelectItem>
                      <SelectItem value="dealer">Dealer</SelectItem>
                      <SelectItem value="sales">Sales</SelectItem>
                      <SelectItem value="manager">Manager</SelectItem>
                      <SelectItem value="support">Support</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <Button 
                  type="submit" 
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 rounded-lg font-semibold transition-all duration-200"
                >
                  Create Account
                </Button>
              </form>
            </CardContent>
          </>
        );
        
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center p-4">
      <Card className="w-full max-w-md bg-slate-800/50 border-slate-700 backdrop-blur-sm">
        {renderStep()}
        
        <div className="px-6 pb-6">
          <div className="text-center text-slate-400 text-sm">
            Already have an account?{" "}
            <Link 
              to="/login" 
              className="text-blue-400 hover:text-blue-300 font-medium transition-colors"
            >
              Sign in
            </Link>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default Signup;
