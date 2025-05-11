import React from 'react';
import styled from 'styled-components';

const OverlayPanel = styled.div`
  position: absolute;
  top: 160px;
  right: 200px;
  width: 350px;
  height: 380px;
  background: ${({ theme }) => theme.card};
  box-shadow: ${({ theme }) => theme.shadow};
  border-radius: 22px;
  padding: 18px 16px;
  display: flex;
  flex-direction: column;
  backdrop-filter: ${({ theme }) => theme.blur};
  opacity: 0.98;
  z-index: 1200;
  pointer-events: all;
`;
const CloseBtn = styled.button`
  align-self: flex-end;
  background: none;
  border: none;
  color: ${({ theme }) => theme.text};
  font-size: 1.3rem;
  cursor: pointer;
`;
const Title = styled.h3`
  margin: 0 0 8px 0;
  font-size: 1.2rem;
`;
const NotesArea = styled.textarea`
  flex: 1;
  background: ${({ theme }) => theme.sidebar};
  border-radius: 12px;
  margin: 10px 0;
  padding: 10px;
  border: none;
  resize: none;
  font-size: 1rem;
  color: ${({ theme }) => theme.text};
`;

interface NotesOverlayProps {
  onClose: () => void;
}

const NotesOverlay: React.FC<NotesOverlayProps> = ({ onClose }) => (
  <OverlayPanel>
    <CloseBtn onClick={onClose}>✖️</CloseBtn>
    <Title>Notes Pad</Title>
    <NotesArea placeholder="Type your notes here..." />
  </OverlayPanel>
);

export default NotesOverlay;
