import React, { useEffect } from 'react';
import io from 'socket.io-client';

const RealTimeUpdates = () => {
  useEffect(() => {
    const socket = io('http://localhost:5000');
    socket.on('loan_certified', data => alert(`Loan ${data.loan_id} certified! Tx: ${data.tx_id}`));
    return () => socket.disconnect();
  }, []);

  return <div>Listening for real-time updates...</div>;
};

export default RealTimeUpdates;
