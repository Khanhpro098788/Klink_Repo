import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  user: null,
  token: localStorage.getItem('access_token') || null,
  isAuthenticated: !!localStorage.getItem('access_token'),
  status: 'idle', // 'idle' | 'loading' | 'succeeded' | 'failed'
};

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setCredentials: (state, action) => {
      const { user, access_token } = action.payload;
      state.user = user;
      if (access_token) {
        state.token = access_token;
        state.isAuthenticated = true;
        localStorage.setItem('access_token', access_token);
      }
    },
    updateUser: (state, action) => {
      state.user = { ...state.user, ...action.payload };
    },
    logout: (state) => {
      state.user = null;
      state.token = null;
      state.isAuthenticated = false;
      localStorage.removeItem('access_token');
    },
  },
});

export const { setCredentials, updateUser, logout } = authSlice.actions;
export default authSlice.reducer;
