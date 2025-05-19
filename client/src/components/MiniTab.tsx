import React from 'react';
import styled from 'styled-components';

const MiniTabContainer = styled.div`
  position: fixed;
  right: 28px;
  bottom: 28px;
  z-index: 1100;
  background: ${({ theme }) => theme.card};
  box-shadow: ${({ theme }) => theme.shadow};
  border-radius: 14px;
  padding: 10px 8px;
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 10px;
  opacity: 0.97;
  backdrop-filter: ${({ theme }) => theme.blur};
  cursor: grab;
  min-width: 140px;
`;

const MiniTabButton = styled.button`
  background: none;
  border: none;
  color: ${({ theme }) => theme.text};
  font-size: 1.2rem;
  border-radius: 8px;
  padding: 6px;
  margin: 0 1px;
  box-shadow: none;
  transition: background 0.16s, box-shadow 0.16s;
  cursor: pointer;
  &:hover {
    background: ${({ theme }) => theme.sidebar};
    box-shadow: ${({ theme }) => theme.shadow};
  }
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  color: ${({ theme }) => theme.text};
  font-size: 1rem;
  margin-left: 6px;
  cursor: pointer;
`;

interface MiniTabProps {
  onChat: () => void;
  onSummary: () => void;
  onNotes: () => void;
  onClose: () => void;
  showChat: boolean;
  showSummary: boolean;
  showNotes: boolean;
}

const MiniTab: React.FC<MiniTabProps> = ({ onChat, onSummary, onNotes, onClose, showChat, showSummary, showNotes }) => {
  // Simple drag logic (for demo, not persistent)
  const ref = React.useRef<HTMLDivElement>(null);
  React.useEffect(() => {
    const el = ref.current;
    if (!el) return;
    let isDown = false, offsetX = 0, offsetY = 0;
    const onMouseDown = (e: MouseEvent) => {
      isDown = true;
      offsetX = e.clientX - el.getBoundingClientRect().left;
      offsetY = e.clientY - el.getBoundingClientRect().top;
      document.addEventListener('mousemove', onMouseMove);
      document.addEventListener('mouseup', onMouseUp);
    };
    const onMouseMove = (e: MouseEvent) => {
      if (!isDown) return;
      el.style.left = `${e.clientX - offsetX}px`;
      el.style.top = `${e.clientY - offsetY}px`;
      el.style.right = 'unset';
      el.style.bottom = 'unset';
    };
    const onMouseUp = () => {
      isDown = false;
      document.removeEventListener('mousemove', onMouseMove);
      document.removeEventListener('mouseup', onMouseUp);
    };
    el.addEventListener('mousedown', onMouseDown);
    return () => {
      el.removeEventListener('mousedown', onMouseDown);
    };
  }, []);

  return (
    <MiniTabContainer ref={ref} style={{pointerEvents: 'all'}}>
      <MiniTabButton onClick={onChat} title="AI Assistant Chat" style={{background: showChat ? '#6366f1' : undefined, color: showChat ? '#fff' : undefined}}>🧠</MiniTabButton>
      <MiniTabButton onClick={onSummary} title="Summary Viewer" style={{background: showSummary ? '#60a5fa' : undefined, color: showSummary ? '#fff' : undefined}}>📋</MiniTabButton>
      <MiniTabButton onClick={onNotes} title="Notes Pad" style={{background: showNotes ? '#f59e42' : undefined, color: showNotes ? '#fff' : undefined}}>📝</MiniTabButton>
      <CloseButton onClick={onClose} title="Close MiniTab">✖️</CloseButton>
    </MiniTabContainer>
  );
};

export default MiniTab;
