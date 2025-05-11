import { createGlobalStyle } from 'styled-components';

export const lightTheme = {
  background: 'rgba(255,255,255,0.85)',
  sidebar: 'rgba(240,240,245,0.93)',
  card: 'rgba(255,255,255,0.98)',
  text: '#222',
  shadow: '0 4px 32px rgba(60,60,90,0.15)',
  blur: 'blur(8px)',
};

export const darkTheme = {
  background: 'rgba(24,24,27,0.95)',
  sidebar: 'rgba(36,36,42,0.97)',
  card: 'rgba(28,28,32,0.97)',
  text: '#f3f3f3',
  shadow: '0 4px 32px rgba(0,0,0,0.35)',
  blur: 'blur(12px)',
};

export const GlobalStyle = createGlobalStyle`
  body {
    margin: 0;
    font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
    background: ${({ theme }) => theme.background};
    color: ${({ theme }) => theme.text};
    transition: background 0.2s, color 0.2s;
    -webkit-user-select: none;
    user-select: none;
    overflow: hidden;
  }
  *, *::before, *::after {
    box-sizing: border-box;
  }
`;
