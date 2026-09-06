import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import LoginScreen from './pages/Auth/LoginScreen';
import RegisterScreen from './pages/Auth/RegisterScreen';
import ProfileScreen from './pages/Profile/ProfileScreen';
import Header from './components/layout/Header';
import { setCredentials, logout } from './store/authSlice';
import api from './services/api';

// Protected Route Wrapper
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated } = useSelector(state => state.auth);
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return children;
};

// Main Layout for protected pages
const MainLayout = ({ children }) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Header />
      <main style={{ flex: 1, padding: '20px' }}>
        {children}
      </main>
    </div>
  );
};

// Home Screen placeholder
const HomeScreen = () => (
  <div className="glass-panel" style={{ padding: '40px', textAlign: 'center', marginTop: '20px' }}>
    <h1 className="text-gradient" style={{ fontSize: '32px' }}>Welcome to Klink AI Dashboard</h1>
    <p style={{ color: 'var(--t2)', marginTop: '16px' }}>Start creating your AI videos.</p>
  </div>
);

function App() {
  const dispatch = useDispatch();
  const { isAuthenticated, token } = useSelector(state => state.auth);

  useEffect(() => {
    // Auto hydrate user on reload if token exists in localStorage
    const hydrate = async () => {
      if (token) {
        try {
          const res = await api.get('/auth/me');
          dispatch(setCredentials({ user: res.data, access_token: token }));
        } catch (err) {
          console.error("Hydration failed", err);
          dispatch(logout());
        }
      }
    };
    hydrate();
  }, [dispatch, token]);

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginScreen />} />
        <Route path="/register" element={<RegisterScreen />} />
        
        {/* Protected Routes */}
        <Route path="/" element={
          <ProtectedRoute>
            <MainLayout>
              <HomeScreen />
            </MainLayout>
          </ProtectedRoute>
        } />
        <Route path="/profile" element={
          <ProtectedRoute>
            <MainLayout>
              <ProfileScreen />
            </MainLayout>
          </ProtectedRoute>
        } />
        
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
