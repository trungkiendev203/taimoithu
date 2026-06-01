import React, { useEffect } from 'react';

export default function Toast({ message, type = 'error', onClose }) {
  useEffect(() => {
    if (message) {
      const timer = setTimeout(() => {
        onClose();
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [message, onClose]);

  if (!message) return null;

  return (
    <div className={`toast-container toast-${type}`}>
      <p>{message}</p>
      <button className="toast-close" onClick={onClose}>✕</button>
    </div>
  );
}
