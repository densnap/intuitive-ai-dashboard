import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Bot, Eye, EyeOff, CheckCircle } from "lucide-react";
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
        title: "Email Required",
        description: "Please enter your email address",
        variant: "destructive"
      });
      return;
    }

    toast({
      title: "Verification Code Sent",
      description: "Please check your email for the OTP"
    });
    setCurrentStep(2);
  };

  const handleOTPSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.otp) {
      toast({
        title: "OTP Required",
        description: "Please enter the verification code",
        variant: "destructive"
      });
      return;
    }

    toast({
      title: "Email Verified!",
      description: "Please complete your account setup"
    });
    setCurrentStep(3);
  };

  const handleFinalSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.username || !formData.password || !formData.role) {
      toast({
        title: "Missing Information",
        description: "Please fill in all fields",
        variant: "destructive"
      });
      return;
    }

    toast({
      title: "Account Created!",
      description: "Welcome to the AI Assistant"
    });

    setTimeout(() => {
      navigate('/assistant');
    }, 1000);
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return (
          <form onSubmit={handleEmailSubmit} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="email" className="text-sm font-medium text-gray-700">
                Email Address
              </Label>
              <Input
                id="email"
                type="email"
                placeholder="Enter your email"
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
                className="h-12 border-gray-200 focus:border-purple-500 focus:ring-purple-500"
              />
            </div>
            <Button
              type="submit"
              className="w-full h-12 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-medium rounded-lg shadow-lg"
            >
              Send Verification Code
            </Button>
          </form>
        );

      case 2:
        return (
          <form onSubmit={handleOTPSubmit} className="space-y-6">
            <div className="text-center mb-4">
              <p className="text-sm text-gray-600">
                We've sent a verification code to<br />
                <span className="font-medium text-gray-900">{formData.email}</span>
              </p>
            </div>
            <div className="space-y-2">
              <Label htmlFor="otp" className="text-sm font-medium text-gray-700">
                Verification Code
              </Label>
              <Input
                id="otp"
                type="text"
                placeholder="Enter 6-digit code"
                value={formData.otp}
                onChange={(e) => setFormData({...formData, otp: e.target.value})}
                className="h-12 border-gray-200 focus:border-purple-500 focus:ring-purple-500 text-center text-lg tracking-widest"
                maxLength={6}
              />
            </div>
            <Button
              type="submit"
              className="w-full h-12 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-medium rounded-lg shadow-lg"
            >
              Verify Code
            </Button>
            <div className="text-center">
              <button
                type="button"
                className="text-sm text-purple-600 hover:text-purple-700 font-medium"
                onClick={() => setCurrentStep(1)}
              >
                Change Email
              </button>
            </div>
          </form>
        );

      case 3:
        return (
          <form onSubmit={handleFinalSubmit} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="username" className="text-sm font-medium text-gray-700">
                Username
              </Label>
              <Input
                id="username"
                type="text"
                placeholder="Choose a username"
                value={formData.username}
                onChange={(e) => setFormData({...formData, username: e.target.value})}
                className="h-12 border-gray-200 focus:border-purple-500 focus:ring-purple-500"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="password" className="text-sm font-medium text-gray-700">
                Password
              </Label>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  placeholder="Create a password"
                  value={formData.password}
                  onChange={(e) => setFormData({...formData, password: e.target.value})}
                  className="h-12 border-gray-200 focus:border-purple-500 focus:ring-purple-500 pr-10"
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="absolute right-2 top-1/2 -translate-y-1/2 h-8 w-8 p-0"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </Button>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="role" className="text-sm font-medium text-gray-700">
                Role
              </Label>
              <Select value={formData.role} onValueChange={(value) => setFormData({...formData, role: value})}>
                <SelectTrigger className="h-12 border-gray-200 focus:border-purple-500 focus:ring-purple-500">
                  <SelectValue placeholder="Select your role" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="admin">Admin</SelectItem>
                  <SelectItem value="dealer">Dealer</SelectItem>
                  <SelectItem value="sales">Sales</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <Button
              type="submit"
              className="w-full h-12 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-medium rounded-lg shadow-lg"
            >
              Create Account
            </Button>
          </form>
        );

      default:
        return null;
    }
  };

  const getStepTitle = () => {
    switch (currentStep) {
      case 1:
        return "Email Verification";
      case 2:
        return "Enter Code";
      case 3:
        return "Account Setup";
      default:
        return "Sign Up";
    }
  };

  const getStepDescription = () => {
    switch (currentStep) {
      case 1:
        return "Enter your email to get started";
      case 2:
        return "Check your email for the verification code";
      case 3:
        return "Complete your account information";
      default:
        return "Create your account";
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br  flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="mx-auto mb-4 w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center shadow-lg">
            {currentStep === 3 ? (
              <CheckCircle className="h-8 w-8 text-white" />
            ) : (
              <Bot className="h-8 w-8 text-white" />
            )}
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Create Account</h1>
          <p className="text-gray-600">Join the Wheely Assistant</p>
        </div>

        <Card className="border-0 shadow-xl bg-white/90 backdrop-blur-sm">
          <CardHeader className="text-center pb-6">
            <CardTitle className="text-xl">{getStepTitle()}</CardTitle>
            <CardDescription>{getStepDescription()}</CardDescription>
            
            {/* Step indicator */}
            <div className="flex justify-center space-x-2 mt-4">
              {[1, 2, 3].map((step) => (
                <div
                  key={step}
                  className={`w-2 h-2 rounded-full ${
                    step <= currentStep ? 'bg-purple-500' : 'bg-gray-300'
                  }`}
                />
              ))}
            </div>
          </CardHeader>
          <CardContent>
            {renderStepContent()}
            
            <div className="text-center text-sm text-gray-600 mt-6">
              Already have an account?{" "}
              <button
                type="button"
                onClick={() => navigate('/login')}
                className="text-purple-600 hover:text-purple-700 font-medium"
              >
                Sign in
              </button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Signup;
