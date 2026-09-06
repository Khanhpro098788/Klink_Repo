import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { UserPlus, Globe, Mail, Key, User, Lock } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import api from '../../services/api';

export default function RegisterScreen() {
  // Step 1: Register, Step 2: OTP
  const [step, setStep] = useState(1);

  const [formData, setFormData] = useState({
    email: '',
    full_name: '',
    password: ''
  });
  
  const [otp, setOtp] = useState('');
  
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [serverError, setServerError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  
  const { t, i18n } = useTranslation();
  
  const navigate = useNavigate();

  const toggleLanguage = () => {
    i18n.changeLanguage(i18n.language === 'en' ? 'vi' : 'en');
  };

  // Real-time validation
  useEffect(() => {
    if (step === 1) {
      const newErrors = {};
      
      // Email regex
      if (formData.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
        newErrors.email = 'Invalid email format';
      }
      
      // Password regex (at least 8 chars, 1 letter, 1 number)
      if (formData.password && !/^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$/.test(formData.password)) {
        newErrors.password = 'Min 8 chars, at least 1 letter and 1 number';
      }

      setErrors(newErrors);
    }
  }, [formData, step]);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    if (Object.keys(errors).length > 0) return;
    
    setServerError('');
    setSuccessMessage('');
    setLoading(true);
    
    try {
      const res = await api.post('/auth/signup', formData);
      setSuccessMessage(res.data.message || t('otp_sent'));
      setStep(2);
    } catch (err) {
      setServerError(err.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOtp = async (e) => {
    e.preventDefault();
    if (otp.length !== 6) return;
    
    setServerError('');
    setLoading(true);
    
    try {
      await api.post('/auth/verify-otp', { email: formData.email, otp });
      navigate('/login', { state: { message: 'Registration successful! Please login.' } });
    } catch (err) {
      setServerError(err.response?.data?.detail || 'OTP Verification failed');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-layout">
      <div className="glass-card animate-fade auth-container" style={{ maxWidth: '520px', padding: '48px', display: 'block', background: 'rgba(10, 10, 15, 0.4)' }}>
        
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

        {step === 1 && (
          <>
            <h2 style={{ marginBottom: '8px', fontSize: '28px', textAlign: 'center', fontWeight: '700' }}>{t('create_account')}</h2>
            <p style={{ color: 'var(--t2)', fontSize: '14px', textAlign: 'center', marginBottom: '32px' }}>
              {t('join_klink')} <span className="text-gradient">{t('klink_ai_video')}</span> {t('get_free_credits')}
            </p>
            
            {serverError && <div style={{ background: 'var(--cdim)', color: 'var(--cor)', padding: '14px', borderRadius: '12px', marginBottom: '24px', fontSize: '14px', border: '1px solid var(--cor)' }}>{serverError}</div>}

            <form onSubmit={handleRegister} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              <div>
                <label style={{ display: 'block', marginBottom: '8px', fontSize: '13px', color: 'var(--t2)', fontWeight: 500 }}>{t('full_name')}</label>
                <div className="modern-input-group">
                  <User size={18} />
                  <input 
                    type="text" name="full_name"
                    className="modern-input" 
                    placeholder={t('enter_full_name')} 
                    value={formData.full_name} onChange={handleChange} required 
                  />
                </div>
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: '8px', fontSize: '13px', color: 'var(--t2)', fontWeight: 500 }}>{t('email')}</label>
                <div className="modern-input-group">
                  <Mail size={18} />
                  <input 
                    type="email" name="email"
                    className={`modern-input ${errors.email ? 'error' : ''}`} 
                    placeholder={t('enter_email')} 
                    value={formData.email} onChange={handleChange} required 
                  />
                </div>
                {errors.email && <span className="error-text">{errors.email}</span>}
              </div>
              
              <div>
                <label style={{ display: 'block', marginBottom: '8px', fontSize: '13px', color: 'var(--t2)', fontWeight: 500 }}>{t('password')}</label>
                <div className="modern-input-group">
                  <Lock size={18} />
                  <input 
                    type="password" name="password"
                    className={`modern-input ${errors.password ? 'error' : ''}`} 
                    placeholder={t('enter_password')} 
                    value={formData.password} onChange={handleChange} required 
                  />
                </div>
                {errors.password && <span className="error-text">{errors.password}</span>}
              </div>

              <button 
                type="submit" 
                className="pill-btn" 
                style={{ marginTop: '12px', width: '100%' }} 
                disabled={loading || Object.keys(errors).length > 0}
              >
                <UserPlus size={18} /> {loading ? t('creating') : t('sign_up')}
              </button>
            </form>

            <p style={{ marginTop: '32px', textAlign: 'center', fontSize: '14px', color: 'var(--t2)' }}>
              {t('have_account')} <Link to="/login" style={{ color: 'var(--acc2)', textDecoration: 'none', fontWeight: 600 }}>{t('sign_in')}</Link>
            </p>
          </>
        )}

        {step === 2 && (
          <div className="animate-fade">
            <h2 style={{ marginBottom: '8px', fontSize: '28px', textAlign: 'center', fontWeight: '700' }}>{t('verify_otp')}</h2>
            <p style={{ color: 'var(--t2)', fontSize: '14px', textAlign: 'center', marginBottom: '32px' }}>
              {successMessage}
            </p>
            
            {serverError && <div style={{ background: 'var(--cdim)', color: 'var(--cor)', padding: '14px', borderRadius: '12px', marginBottom: '24px', fontSize: '14px', border: '1px solid var(--cor)' }}>{serverError}</div>}

            <form onSubmit={handleVerifyOtp} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              <div>
                <label style={{ display: 'block', marginBottom: '8px', fontSize: '13px', color: 'var(--t2)', fontWeight: 500 }}>OTP Code</label>
                <div className="modern-input-group" style={{ justifyContent: 'center' }}>
                  <Key size={18} style={{ position: 'absolute', left: '20px' }} />
                  <input 
                    type="text" 
                    className="modern-input" 
                    style={{ paddingLeft: '50px', letterSpacing: '8px', fontSize: '20px', textAlign: 'center', fontWeight: '600' }}
                    placeholder="123456" 
                    value={otp} onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))} required 
                  />
                </div>
              </div>

              <button 
                type="submit" 
                className="pill-btn" 
                style={{ marginTop: '12px', width: '100%' }} 
                disabled={loading || otp.length !== 6}
              >
                <Mail size={18} /> {loading ? t('verifying') : t('verify')}
              </button>
            </form>

            <button 
              onClick={() => setStep(1)} 
              className="btn-outline" 
              style={{ width: '100%', marginTop: '20px', border: 'none', color: 'var(--t2)' }}
            >
              Back to Registration
            </button>
          </div>
        )}

      </div>
    </div>
  );
}
