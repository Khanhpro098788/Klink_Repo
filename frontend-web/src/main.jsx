import React from 'react';
import ReactDOM from 'react-dom/client';
import { Provider } from 'react-redux';
import { store } from './store';
import App from './App';
import './index.css';
import './i18n';

import { GoogleOAuthProvider } from '@react-oauth/google';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <GoogleOAuthProvider clientId="361539172913-nksh7dk9s7bj2e39jnvtp4077hna3n5c.apps.googleusercontent.com">
      <Provider store={store}>
        <App />
      </Provider>
    </GoogleOAuthProvider>
  </React.StrictMode>
);
