import React, { useState } from 'react';
import { useDispatch } from 'react-redux';
import { useNavigate, Link } from 'react-router-dom';
import { Eye, EyeOff, LogIn, Globe, Mail, Lock } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { GoogleLogin } from '@react-oauth/google';
import api from '../../services/api';
import { setCredentials } from '../../store/authSlice';

export default function LoginScreen() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { t, i18n } = useTranslation();
  
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const toggleLanguage = () => {
    i18n.changeLanguage(i18n.language === 'en' ? 'vi' : 'en');
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    
    try {
      const response = await api.post('/auth/signin', { 
        email, 
        password 
      });

      const { access_token } = response.data;
      
      // Fetch user profile immediately after
      const userRes = await api.get('/auth/me', {
        headers: { Authorization: `Bearer ${access_token}` }
      });

      dispatch(setCredentials({ user: userRes.data, access_token }));
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.detail || t('login_failed'));
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleSuccess = async (credentialResponse) => {
    setError('');
    setLoading(true);
    try {
      const response = await api.post('/auth/google', { google_token: credentialResponse.credential });
      const { access_token } = response.data;
      
      const userRes = await api.get('/auth/me', {
        headers: { Authorization: `Bearer ${access_token}` }
      });

      dispatch(setCredentials({ user: userRes.data, access_token }));
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.detail || t('login_failed'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-layout">
      <div className="glass-card animate-fade auth-container">
        
        {/* Language Switcher */}
        <div style={{ position: 'absolute', top: '16px', right: '16px', zIndex: 10 }}>
          <button 
            onClick={toggleLanguage}
            style={{ display: 'flex', alignItems: 'center', gap: '6px', background: 'rgba(255,255,255,0.1)', border: '1px solid rgba(255,255,255,0.1)', padding: '6px 12px', borderRadius: '20px', color: 'var(--text)', cursor: 'pointer', fontSize: '13px', backdropFilter: 'blur(10px)' }}
          >
            <Globe size={14} />
            {i18n.language === 'en' ? 'EN' : 'VI'}
          </button>
        </div>

        {/* Left Side: Banner */}
        <div className="auth-banner gradient-bg" style={{ flex: 1, padding: '60px', display: 'flex', flexDirection: 'column', justifyContent: 'center', color: 'white' }}>
          <div style={{ background: 'rgba(0,0,0,0.15)', padding: '24px', borderRadius: '20px', backdropFilter: 'blur(10px)', border: '1px solid rgba(255,255,255,0.2)' }}>
            <h1 style={{ fontSize: '36px', marginBottom: '16px', fontWeight: '800', lineHeight: 1.2 }}>
              {t('klink_ai_video')} <br/> <span style={{ color: '#fff', opacity: 0.9 }}>{t('video')}</span>
            </h1>
            <p style={{ fontSize: '15px', opacity: 0.85, lineHeight: 1.6 }}>
              {t('login_banner_text')}
            </p>
          </div>
        </div>

        {/* Right Side: Form */}
        <div className="auth-form" style={{ flex: 1, padding: '60px 48px', background: 'rgba(10, 10, 15, 0.4)' }}>
          <h2 style={{ marginBottom: '8px', fontSize: '28px', fontWeight: '700' }}>{t('welcome_back')}</h2>
          <p style={{ color: 'var(--t2)', marginBottom: '32px' }}>Vui lòng đăng nhập để tiếp tục</p>
          
          {error && <div style={{ background: 'var(--cdim)', color: 'var(--cor)', padding: '14px', borderRadius: '12px', marginBottom: '24px', fontSize: '14px', border: '1px solid var(--cor)' }}>{error}</div>}

          <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div>
              <label style={{ display: 'block', marginBottom: '8px', fontSize: '13px', color: 'var(--t2)', fontWeight: 500 }}>{t('email')}</label>
              <div className="modern-input-group">
                <Mail size={18} />
                <input 
                  type="email" 
                  className="modern-input" 
                  placeholder={t('enter_email')} 
                  value={email} 
                  onChange={(e) => setEmail(e.target.value)} 
                  required 
                />
              </div>
            </div>
            
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                <label style={{ fontSize: '13px', color: 'var(--t2)', fontWeight: 500 }}>{t('password')}</label>
                <Link to="/forgot-password" style={{ fontSize: '13px', color: 'var(--acc2)', textDecoration: 'none', fontWeight: 500 }}>{t('forgot_password')}</Link>
              </div>
              <div className="modern-input-group">
                <Lock size={18} />
                <input 
                  type={showPassword ? 'text' : 'password'} 
                  className="modern-input" 
                  placeholder={t('enter_password')} 
                  value={password} 
                  onChange={(e) => setPassword(e.target.value)} 
                  required 
                />
                <button 
                  type="button" 
                  onClick={() => setShowPassword(!showPassword)}
                  style={{ position: 'absolute', right: '16px', background: 'none', border: 'none', color: 'var(--t2)', cursor: 'pointer', display: 'flex' }}
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>

            <button type="submit" className="pill-btn" style={{ marginTop: '12px', width: '100%' }} disabled={loading}>
              <LogIn size={18} /> {loading ? t('signing_in') : t('sign_in')}
            </button>
          </form>

          <div style={{ display: 'flex', alignItems: 'center', margin: '32px 0' }}>
            <div style={{ flex: 1, height: '1px', background: 'var(--border)' }}></div>
            <span style={{ padding: '0 16px', fontSize: '12px', color: 'var(--t3)', textTransform: 'uppercase', letterSpacing: '1px' }}>Hoặc</span>
            <div style={{ flex: 1, height: '1px', background: 'var(--border)' }}></div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'center' }}>
            <GoogleLogin
              onSuccess={handleGoogleSuccess}
              onError={() => setError('Google Login Failed')}
              theme="filled_black"
              text="signin_with"
              shape="pill"
            />
          </div>

          <p style={{ marginTop: '32px', textAlign: 'center', fontSize: '14px', color: 'var(--t2)' }}>
            {t('no_account')} <Link to="/register" style={{ color: 'var(--acc2)', textDecoration: 'none', fontWeight: 600 }}>{t('create_one')}</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
