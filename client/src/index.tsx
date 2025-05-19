import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import OverlayWindow from './OverlayWindow.tsx';
import ReactDOM from 'react-dom/client';
import MainApp from './MainApp.tsx';
import { Provider } from 'react-redux';
import { mainStore } from './MainStore.ts';
import { ThemeProvider } from 'styled-components';
import { GlobalStyle, lightTheme, darkTheme } from './styles/themeNew.ts';

const root = ReactDOM.createRoot(document.getElementById('root') as HTMLElement);
root.render(
  <BrowserRouter>
    <Routes>
      <Route path="/" element={
        <Provider store={mainStore}>
          <MainApp />
        </Provider>
      } />
      <Route path="/overlay" element={<OverlayWindow />} />
    </Routes>
  </BrowserRouter>
);
