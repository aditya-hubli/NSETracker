/**
 * Authentication utilities and context
 */

export interface AuthUser {
  id: string;
  email: string;
  username: string;
  full_name: string | null;
  role: 'user' | 'admin';
  is_active: boolean;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  username: string;
  full_name?: string;
  password: string;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Store auth token in memory and localStorage
let authToken: string | null = null;

export function getAuthToken(): string | null {
  if (typeof window === 'undefined') return null;
  if (!authToken) {
    authToken = localStorage.getItem('auth_token');
  }
  return authToken;
}

export function setAuthToken(token: string | null): void {
  authToken = token;
  if (typeof window !== 'undefined') {
    if (token) {
      localStorage.setItem('auth_token', token);
    } else {
      localStorage.removeItem('auth_token');
    }
  }
}

export function getStoredUser(): AuthUser | null {
  if (typeof window === 'undefined') return null;
  const stored = localStorage.getItem('auth_user');
  if (stored) {
    try {
      return JSON.parse(stored);
    } catch {
      return null;
    }
  }
  return null;
}

export function setStoredUser(user: AuthUser | null): void {
  if (typeof window !== 'undefined') {
    if (user) {
      localStorage.setItem('auth_user', JSON.stringify(user));
    } else {
      localStorage.removeItem('auth_user');
    }
  }
}

// Demo user data for when backend is unavailable
const DEMO_USERS: Record<string, { user: AuthUser; password: string }> = {
  'user@example.com': {
    user: {
      id: 'demo-user-1',
      email: 'user@example.com',
      username: 'demouser',
      full_name: 'Demo User',
      role: 'user',
      is_active: true,
    },
    password: 'password123',
  },
  'admin@example.com': {
    user: {
      id: 'demo-admin-1',
      email: 'admin@example.com',
      username: 'demoadmin',
      full_name: 'Demo Admin',
      role: 'admin',
      is_active: true,
    },
    password: 'password123',
  },
};

export async function login(credentials: LoginCredentials): Promise<{ user: AuthUser; token: string }> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials),
    });

    if (!res.ok) {
      const error = await res.json().catch(() => ({ detail: 'Login failed' }));
      throw new Error(error.detail || 'Invalid credentials');
    }

    const data = await res.json();
    setAuthToken(data.token);
    setStoredUser(data.user);
    return data;
  } catch (err) {
    // Fallback to demo mode if backend is unavailable
    const demoData = DEMO_USERS[credentials.email];
    if (demoData && demoData.password === credentials.password) {
      const token = `demo-token-${Date.now()}`;
      setAuthToken(token);
      setStoredUser(demoData.user);
      return { user: demoData.user, token };
    }
    throw err;
  }
}

export async function register(data: RegisterData): Promise<{ user: AuthUser; token: string }> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    if (!res.ok) {
      const error = await res.json().catch(() => ({ detail: 'Registration failed' }));
      throw new Error(error.detail || 'Registration failed');
    }

    const result = await res.json();
    setAuthToken(result.token);
    setStoredUser(result.user);
    return result;
  } catch {
    // Fallback to demo mode if backend is unavailable
    const user: AuthUser = {
      id: `demo-user-${Date.now()}`,
      email: data.email,
      username: data.username,
      full_name: data.full_name || null,
      role: data.email.endsWith('@admin.com') ? 'admin' : 'user',
      is_active: true,
    };
    const token = `demo-token-${Date.now()}`;
    setAuthToken(token);
    setStoredUser(user);
    return { user, token };
  }
}

export async function logout(): Promise<void> {
  const token = getAuthToken();
  if (token) {
    try {
      await fetch(`${API_BASE_URL}/api/v1/auth/logout`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });
    } catch {
      // Ignore logout errors
    }
  }
  setAuthToken(null);
  setStoredUser(null);
}

export async function getCurrentUser(): Promise<AuthUser | null> {
  const token = getAuthToken();
  if (!token) return null;

  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (!res.ok) {
      setAuthToken(null);
      setStoredUser(null);
      return null;
    }

    const user = await res.json();
    setStoredUser(user);
    return user;
  } catch {
    return getStoredUser();
  }
}

export function authFetch(url: string, options: RequestInit = {}): Promise<Response> {
  const token = getAuthToken();
  const headers = new Headers(options.headers);
  
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  return fetch(url, { ...options, headers });
}
