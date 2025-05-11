import React from 'react';
import styled from 'styled-components';

const SidebarContainer = styled.nav`
  width: 80px;
  background: ${({ theme }) => theme.sidebar};
  box-shadow: ${({ theme }) => theme.shadow};
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 0;
  border-radius: 0 20px 20px 0;
  backdrop-filter: ${({ theme }) => theme.blur};
  min-height: 100vh;
  z-index: 10;
`;

const NavButton = styled.button<{active?: boolean}>`
  background: ${({ active, theme }) => active ? theme.card : 'transparent'};
  border: none;
  outline: none;
  margin: 12px 0;
  padding: 14px;
  border-radius: 12px;
  color: ${({ theme }) => theme.text};
  box-shadow: ${({ active, theme }) => active ? theme.shadow : 'none'};
  cursor: pointer;
  transition: background 0.2s, box-shadow 0.2s;
  font-size: 20px;
  &:hover {
    background: ${({ theme }) => theme.card};
    box-shadow: ${({ theme }) => theme.shadow};
  }
`;

const ThemeToggle = styled.button`
  margin-top: auto;
  margin-bottom: 8px;
  background: none;
  border: none;
  color: ${({ theme }) => theme.text};
  cursor: pointer;
  font-size: 22px;
`;

interface SidebarProps {
  theme: 'light' | 'dark';
  setTheme: (theme: 'light' | 'dark') => void;
}

const Sidebar: React.FC<SidebarProps> = ({ theme, setTheme }) => {
  // Placeholder for navigation state
  const [active, setActive] = React.useState('dashboard');
  return (
    <SidebarContainer>
      <NavButton active={active === 'dashboard'} onClick={() => setActive('dashboard')} title="Dashboard">🏠</NavButton>
      <NavButton active={active === 'live'} onClick={() => setActive('live')} title="Live Meeting">🎤</NavButton>
      <NavButton active={active === 'past'} onClick={() => setActive('past')} title="Past Meetings">📅</NavButton>
      <NavButton active={active === 'settings'} onClick={() => setActive('settings')} title="Settings">⚙️</NavButton>
      <ThemeToggle onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')} title="Toggle Theme">
        {theme === 'dark' ? '🌞' : '🌙'}
      </ThemeToggle>
    </SidebarContainer>
  );
};

export default Sidebar;
