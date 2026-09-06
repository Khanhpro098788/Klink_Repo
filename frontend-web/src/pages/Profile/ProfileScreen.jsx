import React, { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useLocation } from 'react-router-dom';
import { Save, User, Lock, Shield } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import UploadAvatar from '../../components/profile/UploadAvatar';
import api from '../../services/api';
import { updateUser } from '../../store/authSlice';

export default function ProfileScreen() {
  const { user } = useSelector(state => state.auth);
  const dispatch = useDispatch();
  const location = useLocation();
  const { t } = useTranslation();

  const [activeTab, setActiveTab] = useState('general');

  useEffect(() => {
    if (location.state?.tab) {
      setActiveTab(location.state.tab);
    }
  }, [location]);

  const [fullName, setFullName] = useState(user?.full_name || '');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  
  // Password change state
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [pwdLoading, setPwdLoading] = useState(false);
  const [pwdMessage, setPwdMessage] = useState('');

  const handleAvatarSuccess = (url) => {
    dispatch(updateUser({ avatar_url: url }));
  };

  const handleSaveProfile = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');
    try {
      const res = await api.patch('/auth/me', { full_name: fullName });
      dispatch(updateUser(res.data));
      setMessage(t('profile_updated'));
    } catch (err) {
      setMessage('Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();
    setPwdLoading(true);
    setPwdMessage('');
    try {
      await api.patch('/auth/me/password', { old_password: oldPassword, new_password: newPassword });
      setPwdMessage(t('password_changed'));
      setOldPassword('');
      setNewPassword('');
    } catch (err) {
      setPwdMessage(err.response?.data?.detail || 'Failed to change password');
    } finally {
      setPwdLoading(false);
    }
  };

  if (!user) return null;

  return (
    <div style={{ display: 'flex', gap: '32px', maxWidth: '1000px', margin: '40px auto', alignItems: 'flex-start' }}>
      
      {/* Sidebar Tabs */}
      <div className="glass-panel" style={{ width: '260px', padding: '16px 12px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
        <h3 style={{ padding: '0 12px', fontSize: '12px', textTransform: 'uppercase', color: 'var(--t3)', letterSpacing: '1px', marginBottom: '8px' }}>
          {t('settings')}
        </h3>
        
        <button 
          onClick={() => setActiveTab('general')}
          style={{
            display: 'flex', alignItems: 'center', gap: '12px', padding: '12px 16px', borderRadius: '8px', border: 'none', cursor: 'pointer',
            background: activeTab === 'general' ? 'var(--adim)' : 'transparent',
            color: activeTab === 'general' ? 'var(--acc2)' : 'var(--t2)',
            transition: 'all 0.2s', textAlign: 'left', fontWeight: 500
          }}
        >
          <User size={18} />
          {t('profile')}
        </button>

        <button 
          onClick={() => setActiveTab('password')}
          style={{
            display: 'flex', alignItems: 'center', gap: '12px', padding: '12px 16px', borderRadius: '8px', border: 'none', cursor: 'pointer',
            background: activeTab === 'password' ? 'var(--adim)' : 'transparent',
            color: activeTab === 'password' ? 'var(--acc2)' : 'var(--t2)',
            transition: 'all 0.2s', textAlign: 'left', fontWeight: 500
          }}
        >
          <Shield size={18} />
          {t('change_password')}
        </button>
      </div>

      {/* Main Content Area */}
      <div style={{ flex: 1 }}>
        <h1 style={{ fontSize: '28px', marginBottom: '24px' }}>
          {activeTab === 'general' ? t('profile_settings') : t('change_password')}
        </h1>

        <div className="glass-panel animate-fade" style={{ padding: '32px' }}>
          
          {activeTab === 'general' && (
            <div style={{ display: 'flex', gap: '40px', alignItems: 'flex-start' }}>
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px' }}>
                <UploadAvatar currentAvatarUrl={user.avatar_url} onUploadSuccess={handleAvatarSuccess} />
                <span style={{ fontSize: '12px', color: 'var(--t2)' }}>{t('avatar')}</span>
              </div>
              
              <form onSubmit={handleSaveProfile} style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '20px' }}>
                <div>
                  <label style={{ display: 'block', marginBottom: '8px', fontSize: '13px', color: 'var(--t2)' }}>Username</label>
                  <input type="text" className="input-field" value={user.username} disabled style={{ opacity: 0.5, cursor: 'not-allowed' }} />
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '8px', fontSize: '13px', color: 'var(--t2)' }}>Email</label>
                  <input type="text" className="input-field" value={user.email} disabled style={{ opacity: 0.5, cursor: 'not-allowed' }} />
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '8px', fontSize: '13px', color: 'var(--text)' }}>{t('full_name')}</label>
                  <input type="text" className="input-field" value={fullName} onChange={(e) => setFullName(e.target.value)} />
                </div>
                
                {message && <div style={{ fontSize: '14px', color: message.includes('success') || message.includes('thành công') ? 'var(--grn)' : 'var(--cor)', padding: '12px', background: message.includes('success') || message.includes('thành công') ? 'var(--gdim)' : 'var(--cdim)', borderRadius: '8px' }}>{message}</div>}

                <div style={{ marginTop: '12px' }}>
                  <button type="submit" className="btn-primary" disabled={loading || fullName === user.full_name}>
                    <Save size={18} /> {loading ? t('updating') : t('update_profile')}
                  </button>
                </div>
              </form>
            </div>
          )}

          {activeTab === 'password' && (
            <form onSubmit={handleChangePassword} style={{ display: 'flex', flexDirection: 'column', gap: '20px', maxWidth: '480px' }}>
              <div>
                <label style={{ display: 'block', marginBottom: '8px', fontSize: '13px', color: 'var(--text)' }}>{t('old_password')}</label>
                <div style={{ position: 'relative' }}>
                  <Lock size={16} style={{ position: 'absolute', left: '16px', top: '14px', color: 'var(--t2)' }} />
                  <input type="password" className="input-field" style={{ paddingLeft: '44px' }} value={oldPassword} onChange={(e) => setOldPassword(e.target.value)} required />
                </div>
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '8px', fontSize: '13px', color: 'var(--text)' }}>{t('new_password')}</label>
                <div style={{ position: 'relative' }}>
                  <Lock size={16} style={{ position: 'absolute', left: '16px', top: '14px', color: 'var(--t2)' }} />
                  <input type="password" className="input-field" style={{ paddingLeft: '44px' }} value={newPassword} onChange={(e) => setNewPassword(e.target.value)} required minLength={6} />
                </div>
              </div>
              
              {pwdMessage && <div style={{ fontSize: '14px', color: pwdMessage.includes('success') || pwdMessage.includes('thành công') ? 'var(--grn)' : 'var(--cor)', padding: '12px', background: pwdMessage.includes('success') || pwdMessage.includes('thành công') ? 'var(--gdim)' : 'var(--cdim)', borderRadius: '8px' }}>{pwdMessage}</div>}

              <div style={{ marginTop: '12px' }}>
                <button type="submit" className="btn-primary" disabled={pwdLoading}>
                  <Shield size={18} /> {pwdLoading ? t('updating') : t('change_password')}
                </button>
              </div>
            </form>
          )}

        </div>
      </div>
    </div>
  );
}
