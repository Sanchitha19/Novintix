import React, { useState } from 'react';
import { Lock, User, ArrowRight } from 'lucide-react';
import { login } from '../api';

const LoginForm = ({ onLogin }) => {
  const [username, setUsername] = useState('johnd');
  const [password, setPassword] = useState('m38mzuvjxl');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const data = await login(username, password);
      console.log("Login API response:", data);
      // Pass only the string token
      if (data && data.access_token) {
        onLogin(data.access_token);
      } else {
        console.error("No access token in response");
      }
    } catch (error) {
      console.error("Login failed:", error);
      alert("Login failed. Check server and credentials.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center h-full p-8">
      <div className="w-full max-w-md p-8 glass-panel rounded-2xl">
        <div className="mb-8 text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 mb-4 rounded-full bg-brand-blue/10">
            <Lock className="w-8 h-8 text-brand-blue" />
          </div>
          <h2 className="text-2xl font-bold text-white">Welcome Back</h2>
          <p className="text-slate-400">Sign in to start your support session</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-300">Username</label>
            <div className="relative">
              <User className="absolute w-5 h-5 -translate-y-1/2 left-3 top-1/2 text-slate-500" />
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full py-3 pl-10 pr-4 border rounded-xl bg-dark-bg border-dark-border focus:outline-none focus:border-brand-blue"
                placeholder="Enter username"
              />
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-300">Password</label>
            <div className="relative">
              <Lock className="absolute w-5 h-5 -translate-y-1/2 left-3 top-1/2 text-slate-500" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full py-3 pl-10 pr-4 border rounded-xl bg-dark-bg border-dark-border focus:outline-none focus:border-brand-blue"
                placeholder="Enter password"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="flex items-center justify-center w-full py-3 font-bold text-white transition-all rounded-xl bg-brand-blue hover:bg-brand-blue/90 disabled:opacity-50"
          >
            {isLoading ? "Authenticating..." : "Login to System"}
            <ArrowRight className="w-5 h-5 ml-2" />
          </button>
        </form>

        <div className="mt-8 p-4 rounded-lg bg-brand-blue/5 border border-brand-blue/20">
          <p className="text-xs text-brand-blue font-mono text-center">
            DEMO CREDENTIALS: johnd / m38mzuvjxl
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginForm;
