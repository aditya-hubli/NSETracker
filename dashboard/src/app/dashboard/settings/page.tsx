'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';

interface UserSettings {
  notifications: {
    priceAlerts: boolean;
    dailyDigest: boolean;
    marketOpen: boolean;
    marketClose: boolean;
    emailEnabled: boolean;
  };
  display: {
    theme: 'light' | 'dark';
    showPercent: boolean;
  };
  realtime: {
    enabled: boolean;
    refreshInterval: number;
  };
}

const defaultSettings: UserSettings = {
  notifications: {
    priceAlerts: true,
    dailyDigest: false,
    marketOpen: true,
    marketClose: true,
    emailEnabled: false,
  },
  display: {
    theme: 'light',
    showPercent: true,
  },
  realtime: {
    enabled: true,
    refreshInterval: 5,
  },
};

export default function SettingsPage() {
  const { user } = useAuth();
  const [settings, setSettings] = useState<UserSettings>(defaultSettings);
  const [saved, setSaved] = useState(false);
  const [emailTesting, setEmailTesting] = useState(false);
  const [emailTestResult, setEmailTestResult] = useState<{ success: boolean; message: string } | null>(null);

  useEffect(() => {
    const savedSettings = localStorage.getItem('userSettings');
    if (savedSettings) {
      setSettings(JSON.parse(savedSettings));
    }
  }, []);

  const saveSettings = () => {
    localStorage.setItem('userSettings', JSON.stringify(settings));
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const testEmail = async () => {
    const userEmail = user?.email;
    if (!userEmail) {
      setEmailTestResult({ success: false, message: 'No email address found for your account' });
      return;
    }

    setEmailTesting(true);
    setEmailTestResult(null);

    try {
      const response = await fetch('http://localhost:8000/api/v1/notifications/email/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: userEmail }),
      });

      const result = await response.json();
      setEmailTestResult(result);
    } catch (error) {
      setEmailTestResult({ 
        success: false, 
        message: 'Failed to connect to server. Make sure the backend is running.' 
      });
    } finally {
      setEmailTesting(false);
    }
  };

  const Toggle = ({ enabled, onChange }: { enabled: boolean; onChange: () => void }) => (
    <button
      onClick={onChange}
      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
        enabled ? 'bg-emerald-500' : 'bg-gray-300'
      }`}
    >
      <span
        className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform shadow ${
          enabled ? 'translate-x-6' : 'translate-x-1'
        }`}
      />
    </button>
  );

  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-500 mt-1">Manage your preferences and account settings</p>
      </div>

      {/* Notifications */}
      <div className="bg-white border border-gray-100 rounded-2xl shadow-sm overflow-hidden">
        <div className="p-5 border-b border-gray-100">
          <h2 className="text-lg font-semibold text-gray-900 flex items-center">
            <svg className="w-5 h-5 mr-2 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
            Notifications
          </h2>
        </div>
        <div className="divide-y divide-gray-100">
          <div className="p-5 flex justify-between items-center">
            <div>
              <span className="font-medium text-gray-900">Price Alerts</span>
              <p className="text-sm text-gray-500">Get notified when stocks hit your target price</p>
            </div>
            <Toggle
              enabled={settings.notifications.priceAlerts}
              onChange={() =>
                setSettings({
                  ...settings,
                  notifications: { ...settings.notifications, priceAlerts: !settings.notifications.priceAlerts },
                })
              }
            />
          </div>
          <div className="p-5 flex justify-between items-center">
            <div>
              <span className="font-medium text-gray-900">Daily Digest</span>
              <p className="text-sm text-gray-500">Receive a daily summary of your watchlist</p>
            </div>
            <Toggle
              enabled={settings.notifications.dailyDigest}
              onChange={() =>
                setSettings({
                  ...settings,
                  notifications: { ...settings.notifications, dailyDigest: !settings.notifications.dailyDigest },
                })
              }
            />
          </div>
          <div className="p-5 flex justify-between items-center">
            <div>
              <span className="font-medium text-gray-900">Market Open Alert</span>
              <p className="text-sm text-gray-500">Get notified when NSE/BSE markets open (9:15 AM IST)</p>
            </div>
            <Toggle
              enabled={settings.notifications.marketOpen}
              onChange={() =>
                setSettings({
                  ...settings,
                  notifications: { ...settings.notifications, marketOpen: !settings.notifications.marketOpen },
                })
              }
            />
          </div>
          <div className="p-5 flex justify-between items-center">
            <div>
              <span className="font-medium text-gray-900">Market Close Alert</span>
              <p className="text-sm text-gray-500">Get notified when NSE/BSE markets close (3:30 PM IST)</p>
            </div>
            <Toggle
              enabled={settings.notifications.marketClose}
              onChange={() =>
                setSettings({
                  ...settings,
                  notifications: { ...settings.notifications, marketClose: !settings.notifications.marketClose },
                })
              }
            />
          </div>
          <div className="p-5 border-t border-gray-200">
            <div className="flex justify-between items-center mb-3">
              <div>
                <span className="font-medium text-gray-900">Email Notifications</span>
                <p className="text-sm text-gray-500">Receive alerts and digests via email</p>
              </div>
              <Toggle
                enabled={settings.notifications.emailEnabled}
                onChange={() =>
                  setSettings({
                    ...settings,
                    notifications: { ...settings.notifications, emailEnabled: !settings.notifications.emailEnabled },
                  })
                }
              />
            </div>
            {settings.notifications.emailEnabled && (
              <div className="space-y-3">
                {/* Show registered email - read only */}
                <div className="flex items-center space-x-3">
                  <div className="flex-1 px-4 py-2.5 bg-gray-50 rounded-xl border border-gray-200">
                    <div className="flex items-center">
                      <svg className="w-5 h-5 text-gray-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                      </svg>
                      <span className="text-gray-900">{user?.email || 'No email found'}</span>
                    </div>
                  </div>
                  <button
                    onClick={testEmail}
                    disabled={emailTesting || !user?.email}
                    className="px-4 py-2.5 bg-gray-100 hover:bg-gray-200 disabled:bg-gray-50 disabled:text-gray-400 text-gray-700 rounded-xl font-medium transition flex items-center space-x-2"
                  >
                    {emailTesting ? (
                      <>
                        <div className="w-4 h-4 border-2 border-gray-400 border-t-transparent rounded-full animate-spin"></div>
                        <span>Sending...</span>
                      </>
                    ) : (
                      <>
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                        </svg>
                        <span>Test</span>
                      </>
                    )}
                  </button>
                </div>
                <p className="text-xs text-gray-500">
                  Notifications will be sent to your registered email address
                </p>
                {emailTestResult && (
                  <div className={`p-3 rounded-lg text-sm ${
                    emailTestResult.success 
                      ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' 
                      : 'bg-red-50 text-red-700 border border-red-200'
                  }`}>
                    {emailTestResult.message}
                  </div>
                )}
                <p className="text-xs text-gray-500">
                  Get a free API key from <a href="https://resend.com" target="_blank" rel="noopener noreferrer" className="text-emerald-600 hover:underline">resend.com</a> and add RESEND_API_KEY to your .env file.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Real-time Updates */}
      <div className="bg-white border border-gray-100 rounded-2xl shadow-sm overflow-hidden">
        <div className="p-5 border-b border-gray-100">
          <h2 className="text-lg font-semibold text-gray-900 flex items-center">
            <svg className="w-5 h-5 mr-2 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            Real-time Updates
          </h2>
        </div>
        <div className="divide-y divide-gray-100">
          <div className="p-5 flex justify-between items-center">
            <div>
              <span className="font-medium text-gray-900">Enable Real-time Prices</span>
              <p className="text-sm text-gray-500">Live WebSocket connection for instant price updates</p>
            </div>
            <Toggle
              enabled={settings.realtime.enabled}
              onChange={() =>
                setSettings({
                  ...settings,
                  realtime: { ...settings.realtime, enabled: !settings.realtime.enabled },
                })
              }
            />
          </div>
          <div className="p-5 flex justify-between items-center">
            <div>
              <span className="font-medium text-gray-900">Refresh Interval</span>
              <p className="text-sm text-gray-500">How often to update prices (seconds)</p>
            </div>
            <select
              value={settings.realtime.refreshInterval}
              onChange={(e) =>
                setSettings({
                  ...settings,
                  realtime: { ...settings.realtime, refreshInterval: parseInt(e.target.value) },
                })
              }
              disabled={!settings.realtime.enabled}
              className="px-4 py-2 rounded-xl border border-gray-200 text-gray-900 bg-white focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 disabled:opacity-50"
            >
              <option value={1}>1 second</option>
              <option value={5}>5 seconds</option>
              <option value={10}>10 seconds</option>
              <option value={30}>30 seconds</option>
              <option value={60}>1 minute</option>
            </select>
          </div>
        </div>
      </div>

      {/* Display */}
      <div className="bg-white border border-gray-100 rounded-2xl shadow-sm overflow-hidden">
        <div className="p-5 border-b border-gray-100">
          <h2 className="text-lg font-semibold text-gray-900 flex items-center">
            <svg className="w-5 h-5 mr-2 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
            Display
          </h2>
        </div>
        <div className="divide-y divide-gray-100">
          <div className="p-5 flex justify-between items-center">
            <div>
              <span className="font-medium text-gray-900">Show Percentage Change</span>
              <p className="text-sm text-gray-500">Display percentage change alongside price</p>
            </div>
            <Toggle
              enabled={settings.display.showPercent}
              onChange={() =>
                setSettings({
                  ...settings,
                  display: { ...settings.display, showPercent: !settings.display.showPercent },
                })
              }
            />
          </div>
        </div>
      </div>

      {/* Save Button */}
      <div className="flex justify-end">
        <button
          onClick={saveSettings}
          className={`px-6 py-3 rounded-xl font-semibold transition shadow-sm flex items-center space-x-2 ${
            saved
              ? 'bg-emerald-100 text-emerald-700'
              : 'bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-600 hover:to-green-700 text-white'
          }`}
        >
          {saved ? (
            <>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <span>Saved!</span>
            </>
          ) : (
            <>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
              </svg>
              <span>Save Settings</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
}
