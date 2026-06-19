import React, { createContext, useState, useEffect, useContext } from 'react';
import axios from 'axios';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('police_token') || null);
  const [role, setRole] = useState(localStorage.getItem('police_role') || null);
  const [loading, setLoading] = useState(true);

  // Set default axios header
  if (token) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  }

  useEffect(() => {
    const fetchUser = async () => {
      if (!token) {
        setLoading(false);
        return;
      }
      try {
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        const response = await axios.get('/api/v1/auth/me');
        setUser(response.data);
      } catch (error) {
        console.error("Token verification failed, logging out:", error);
        logout();
      } finally {
        setLoading(false);
      }
    };
    fetchUser();
  }, [token]);

  const login = async (username, password) => {
    const params = new URLSearchParams();
    params.append('username', username);
    params.append('password', password);

    const response = await axios.post('/api/v1/auth/login', params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    });

    const { access_token, role: userRole } = response.data;
    localStorage.setItem('police_token', access_token);
    localStorage.setItem('police_role', userRole);
    localStorage.setItem('police_username', username);
    
    setToken(access_token);
    setRole(userRole);
    axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
    
    const userProfile = await axios.get('/api/v1/auth/me');
    setUser(userProfile.data);
    return userProfile.data;
  };

  const logout = () => {
    localStorage.removeItem('police_token');
    localStorage.removeItem('police_role');
    localStorage.removeItem('police_username');
    setToken(null);
    setRole(null);
    setUser(null);
    delete axios.defaults.headers.common['Authorization'];
  };

  return (
    <AuthContext.Provider value={{ user, token, role, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
