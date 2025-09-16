import axios from 'axios';
import { io } from 'socket.io-client';

const BASE_URL = 'http://localhost:4000';

export const fetchChatReply = async (sessionId, message) => {
  const response = await axios.post(`${BASE_URL}/api/chat`, { sessionId, message });
  return response.data;
};

export const fetchSessionHistory = async (sessionId) => {
  const response = await axios.get(`${BASE_URL}/api/session/${sessionId}/history`);
  return response.data.history;
};

export const resetSession = async (sessionId) => {
  const response = await axios.post(`${BASE_URL}/api/session/${sessionId}/reset`);
  return response.data;
};

// WebSocket connection
export const socket = io(BASE_URL);
