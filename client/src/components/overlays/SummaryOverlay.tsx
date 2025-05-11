import React from 'react';
import styled from 'styled-components';

const OverlayPanel = styled.div`
  position: absolute;
  top: 120px;
  right: 160px;
  width: 320px;
  height: 320px;
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
const SummaryBox = styled.div`
  flex: 1;
  background: ${({ theme }) => theme.sidebar};
  border-radius: 12px;
  margin: 10px 0;
  padding: 10px;
  overflow-y: auto;
  color: ${({ theme }) => theme.text};
`;

interface SummaryOverlayProps {
  onClose: () => void;
}

const SummaryOverlay: React.FC<SummaryOverlayProps> = ({ onClose }) => (
  <OverlayPanel>
    <CloseBtn onClick={onClose}>✖️</CloseBtn>
    <Title>Live AI Meeting Summary</Title>
    <SummaryBox>
      <div style={{opacity:0.5}}>Summary will appear here...</div>
    </SummaryBox>
  </OverlayPanel>
);

export default SummaryOverlay;
