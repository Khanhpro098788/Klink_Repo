import React, { useState, useRef, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Link, useNavigate } from 'react-router-dom';
import { LogOut, User, Coins, Globe, Settings, Lock, ChevronDown } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { logout } from '../../store/authSlice';
import api from '../../services/api';

export default function Header() {
  const { user } = useSelector(state => state.auth);
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { t, i18n } = useTranslation();
  
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setDropdownOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [dropdownRef]);

  const handleLogout = async () => {
    try {
      await api.post('/auth/signout');
    } catch (e) {
      console.error('Signout failed', e);
    }
    dispatch(logout());
    navigate('/login');
  };

  const toggleLanguage = () => {
    i18n.changeLanguage(i18n.language === 'en' ? 'vi' : 'en');
    setDropdownOpen(false);
  };

  if (!user) return null;

  return (
    <header className="glass-nav" style={{ padding: '16px 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', position: 'sticky', top: 0, zIndex: 100 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <Link to="/" style={{ textDecoration: 'none' }}>
          <h2 style={{ fontSize: '20px', fontWeight: 700, margin: 0 }}>
            <span className="text-gradient">Klink AI</span>
          </h2>
        </Link>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
        {/* Credit Balance */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'var(--bg3)', padding: '6px 12px', borderRadius: '20px', border: '1px solid var(--border)' }}>
          <Coins size={16} color="var(--amb)" />
          <span style={{ fontWeight: 600, fontSize: '14px', color: 'var(--amb)' }}>{user.credit_balance}</span>
        </div>

        {/* User Info & Dropdown */}
        <div style={{ position: 'relative' }} ref={dropdownRef}>
          <button 
            onClick={() => setDropdownOpen(!dropdownOpen)}
            style={{ 
              display: 'flex', alignItems: 'center', gap: '10px', background: 'transparent', 
              border: 'none', cursor: 'pointer', color: 'var(--text)', padding: 0 
            }}
          >
            <div style={{ width: '36px', height: '36px', borderRadius: '50%', background: 'var(--bg3)', overflow: 'hidden', display: 'flex', alignItems: 'center', justifyContent: 'center', border: '1px solid var(--border)' }}>
              {user.avatar_url ? (
                <img src={user.avatar_url} alt="avatar" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
              ) : (
                <User size={18} color="var(--t2)" />
              )}
            </div>
            <span style={{ fontWeight: 500, fontSize: '14px' }}>{user.full_name || user.username}</span>
            <ChevronDown size={14} style={{ color: 'var(--t2)', transition: 'transform 0.2s', transform: dropdownOpen ? 'rotate(180deg)' : 'rotate(0)' }} />
          </button>

          {/* Dropdown Menu */}
          {dropdownOpen && (
            <div className="glass-panel animate-fade" style={{ 
              position: 'absolute', top: 'calc(100% + 12px)', right: 0, 
              width: '240px', padding: '8px', display: 'flex', flexDirection: 'column', gap: '4px',
              boxShadow: '0 10px 30px rgba(0,0,0,0.3)', border: '1px solid rgba(255,255,255,0.1)'
            }}>
              
              <Link to="/profile" onClick={() => setDropdownOpen(false)} style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '10px 12px', textDecoration: 'none', color: 'var(--t1)', borderRadius: '6px', transition: 'background 0.2s' }} className="dropdown-item">
                <User size={16} />
                <span style={{ fontSize: '14px', fontWeight: 500 }}>{t('profile')}</span>
              </Link>
              
              <Link to="/profile" state={{ tab: 'password' }} onClick={() => setDropdownOpen(false)} style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '10px 12px', textDecoration: 'none', color: 'var(--t1)', borderRadius: '6px', transition: 'background 0.2s' }} className="dropdown-item">
                <Lock size={16} />
                <span style={{ fontSize: '14px', fontWeight: 500 }}>{t('change_password')}</span>
              </Link>

              <div style={{ height: '1px', background: 'var(--border)', margin: '4px 0' }}></div>

              <button onClick={toggleLanguage} style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '10px 12px', textDecoration: 'none', color: 'var(--t1)', borderRadius: '6px', background: 'transparent', border: 'none', width: '100%', cursor: 'pointer', textAlign: 'left', transition: 'background 0.2s' }} className="dropdown-item">
                <Globe size={16} />
                <span style={{ fontSize: '14px', fontWeight: 500 }}>{t('language')}: {i18n.language === 'en' ? 'English' : 'Tiếng Việt'}</span>
              </button>

              <div style={{ height: '1px', background: 'var(--border)', margin: '4px 0' }}></div>

              <button onClick={handleLogout} style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '10px 12px', textDecoration: 'none', color: 'var(--cor)', borderRadius: '6px', background: 'transparent', border: 'none', width: '100%', cursor: 'pointer', textAlign: 'left', transition: 'background 0.2s' }} className="dropdown-item">
                <LogOut size={16} />
                <span style={{ fontSize: '14px', fontWeight: 500 }}>{t('logout')}</span>
              </button>

            </div>
          )}
        </div>
      </div>
    </header>
  );
}
