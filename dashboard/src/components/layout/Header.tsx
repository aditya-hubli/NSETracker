'use client';

import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import { useState, useEffect } from 'react';

export default function Header() {
  const { user, isAuthenticated, logout } = useAuth();
  const [showMenu, setShowMenu] = useState(false);
  const [currentTime, setCurrentTime] = useState(new Date());
  const [isMarketOpen, setIsMarketOpen] = useState(false);

  useEffect(() => {
    const timer = setInterval(() => {
      const now = new Date();
      setCurrentTime(now);
      
      // Check if Indian market is open (9:15 AM - 3:30 PM IST, Mon-Fri)
      const istHours = now.getUTCHours() + 5.5;
      const istMinutes = (istHours % 1) * 60 + now.getUTCMinutes();
      const totalMinutes = Math.floor(istHours) * 60 + istMinutes;
      const day = now.getDay();
      
      const marketOpen = 9 * 60 + 15; // 9:15 AM
      const marketClose = 15 * 60 + 30; // 3:30 PM
      
      setIsMarketOpen(day >= 1 && day <= 5 && totalMinutes >= marketOpen && totalMinutes <= marketClose);
    }, 1000);
    
    return () => clearInterval(timer);
  }, []);

  return (
    <header className="bg-white border-b border-gray-100 sticky top-0 z-50 shadow-sm">
      <div className="w-full px-6 lg:px-10">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link href={isAuthenticated ? '/dashboard' : '/'} className="flex items-center space-x-3">
            <div className="w-11 h-11 bg-gradient-to-br from-emerald-500 to-green-600 rounded-xl flex items-center justify-center shadow-lg shadow-emerald-500/30">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
            <div>
              <span className="font-bold text-xl text-gray-900">NSE<span className="text-emerald-600">Tracker</span></span>
              <p className="text-xs text-gray-500 -mt-0.5">Real-Time Indian Markets</p>
            </div>
          </Link>

          {/* Center - Live Time & Market Status */}
          <div className="hidden lg:flex items-center space-x-6">
            <div className="text-center">
              <p className="text-lg font-bold text-gray-900">
                {currentTime.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true })}
              </p>
              <p className="text-xs text-gray-500">
                {currentTime.toLocaleDateString('en-IN', { weekday: 'short', day: 'numeric', month: 'short' })} IST
              </p>
            </div>
            
            <div className={`flex items-center space-x-2 px-4 py-2 rounded-full ${
              isMarketOpen 
                ? 'bg-emerald-50 border border-emerald-200' 
                : 'bg-gray-50 border border-gray-200'
            }`}>
              <span className={`w-2.5 h-2.5 rounded-full ${
                isMarketOpen ? 'bg-emerald-500 animate-pulse' : 'bg-gray-400'
              }`}></span>
              <span className={`text-sm font-semibold ${
                isMarketOpen ? 'text-emerald-700' : 'text-gray-600'
              }`}>
                {isMarketOpen ? 'Market Open' : 'Market Closed'}
              </span>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex items-center space-x-4">
            {!isAuthenticated ? (
              <>
                <Link href="/" className="text-gray-600 hover:text-emerald-600 transition font-medium px-3 py-2">
                  Home
                </Link>
                <Link href="/login" className="text-gray-600 hover:text-emerald-600 transition font-medium px-3 py-2">
                  Sign In
                </Link>
                <Link
                  href="/register"
                  className="bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-600 hover:to-green-700 text-white px-6 py-2.5 rounded-xl transition shadow-lg shadow-emerald-500/30 font-semibold"
                >
                  Get Started
                </Link>
              </>
            ) : (
              <>
                <Link href="/dashboard" className="text-gray-600 hover:text-emerald-600 transition font-medium px-3 py-2 hidden md:block">
                  Markets
                </Link>
                <Link href="/dashboard/watchlist" className="text-gray-600 hover:text-emerald-600 transition font-medium px-3 py-2 hidden md:block">
                  Watchlist
                </Link>
                <Link href="/dashboard/analytics" className="text-gray-600 hover:text-emerald-600 transition font-medium px-3 py-2 hidden md:block">
                  Analytics
                </Link>
                
                {/* User Menu */}
                <div className="relative ml-4">
                  <button 
                    onClick={() => setShowMenu(!showMenu)}
                    className="flex items-center space-x-3 bg-gray-50 hover:bg-gray-100 pl-3 pr-4 py-2 rounded-xl transition border border-gray-200"
                  >
                    <div className="w-8 h-8 bg-gradient-to-br from-emerald-500 to-green-600 rounded-lg flex items-center justify-center text-white font-bold text-sm">
                      {user?.full_name?.charAt(0).toUpperCase() || user?.username?.charAt(0).toUpperCase()}
                    </div>
                    <div className="text-left hidden sm:block">
                      <p className="text-sm font-semibold text-gray-900">{user?.full_name || user?.username}</p>
                    </div>
                    <svg className={`w-4 h-4 text-gray-400 transition-transform ${showMenu ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                  
                  {showMenu && (
                    <>
                      <div className="fixed inset-0 z-10" onClick={() => setShowMenu(false)}></div>
                      <div className="absolute right-0 mt-2 w-56 bg-white rounded-xl shadow-xl border border-gray-100 py-2 z-20">
                        <div className="px-4 py-3 border-b border-gray-100">
                          <p className="text-sm font-semibold text-gray-900">{user?.full_name}</p>
                          <p className="text-xs text-gray-500">{user?.email}</p>
                        </div>
                        <Link href="/dashboard" className="flex items-center px-4 py-2.5 text-sm text-gray-700 hover:bg-emerald-50 hover:text-emerald-700">
                          <svg className="w-4 h-4 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                          </svg>
                          Dashboard
                        </Link>
                        <Link href="/dashboard/settings" className="flex items-center px-4 py-2.5 text-sm text-gray-700 hover:bg-emerald-50 hover:text-emerald-700">
                          <svg className="w-4 h-4 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                          </svg>
                          Settings
                        </Link>
                        <hr className="my-2 border-gray-100" />
                        <button
                          onClick={logout}
                          className="flex items-center w-full px-4 py-2.5 text-sm text-red-600 hover:bg-red-50"
                        >
                          <svg className="w-4 h-4 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                          </svg>
                          Sign Out
                        </button>
                      </div>
                    </>
                  )}
                </div>
              </>
            )}
          </nav>
        </div>
      </div>
    </header>
  );
}
