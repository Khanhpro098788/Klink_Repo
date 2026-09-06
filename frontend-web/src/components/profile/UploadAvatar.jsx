import React, { useState } from 'react';
import { Camera, Loader2 } from 'lucide-react';
import api from '../../services/api';

export default function UploadAvatar({ currentAvatarUrl, onUploadSuccess }) {
  const [uploading, setUploading] = useState(false);

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // For real implementation:
    // 1. Get signature from /assets/upload-signature
    // 2. Upload to cloudinary
    // Here we'll simulate the process and just set a mock URL
    
    setUploading(true);
    try {
      // Simulate network delay
      await new Promise(resolve => setTimeout(resolve, 1500));
      const mockUrl = `https://api.dicebear.com/7.x/avataaars/svg?seed=${Math.random()}`;
      
      // Update backend via PATCH /me
      await api.patch('/auth/me', { avatar_url: mockUrl });
      onUploadSuccess(mockUrl);
    } catch (err) {
      console.error(err);
      alert('Upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div style={{ position: 'relative', width: '100px', height: '100px', borderRadius: '50%', overflow: 'hidden', background: 'var(--bg3)', border: '2px solid var(--border)' }}>
      {currentAvatarUrl ? (
        <img src={currentAvatarUrl} alt="avatar" style={{ width: '100%', height: '100%', objectFit: 'cover', opacity: uploading ? 0.5 : 1 }} />
      ) : (
        <div style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Camera size={32} color="var(--t2)" />
        </div>
      )}

      {uploading && (
        <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'rgba(0,0,0,0.5)' }}>
          <Loader2 className="animate-spin" size={24} color="#fff" />
        </div>
      )}

      <input 
        type="file" 
        accept="image/*"
        onChange={handleFileChange}
        style={{ position: 'absolute', inset: 0, opacity: 0, cursor: 'pointer' }}
        disabled={uploading}
      />
    </div>
  );
}
