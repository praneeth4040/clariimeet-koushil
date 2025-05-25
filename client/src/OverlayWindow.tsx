import React from 'react';
import styled from 'styled-components';
import MiniTab from './components/MiniTab.tsx';

const OverlayContainer = styled.div`
  width: 340px;
  height: 80px;
  position: fixed;
  top: 24px;
  right: 24px;
  background: rgba(36,36,42,0.97);
  border-radius: 18px;
  box-shadow: 0 4px 32px rgba(0,0,0,0.35);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 24px;
  z-index: 9999;
  color: #fff;
  font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
  backdrop-filter: blur(8px);
`;
const Title = styled.div`
  font-size: 1.2rem;
  font-weight: 600;
`;
const CloseBtn = styled.button`
  background: none;
  border: none;
  color: #fff;
  font-size: 1.3rem;
  cursor: pointer;
  margin-left: 12px;
`;

const OverlayWindow: React.FC = () => {
  // You can add state here if you want to control overlays from the overlay window
  return (
    <MiniTab
      onChat={() => {}}
      onSummary={() => {}}
      onNotes={() => {}}
      onClose={() => {
        window.electron?.ipcRenderer?.send('hide-overlay');
      }}
      showChat={false}
      showSummary={false}
      showNotes={false}
    />
  );
};

export default OverlayWindow;
