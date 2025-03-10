import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Métricas personalizadas
const errorRate = new Rate('errors');
const messageProcessingTime = new Trend('message_processing_time');

export const options = {
  scenarios: {
    chat_load: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '2m', target: 20 },  // Carga normal
        { duration: '5m', target: 20 },  // Mantener carga normal
        { duration: '2m', target: 50 },  // Carga media
        { duration: '5m', target: 50 },  // Mantener carga media
        { duration: '2m', target: 100 }, // Carga alta
        { duration: '5m', target: 100 }, // Mantener carga alta
        { duration: '2m', target: 0 },   // Ramp down
      ],
    },
  },
  thresholds: {
    http_req_duration: ['p(95)<1000'],    // 95% de las peticiones deben completarse en menos de 1s
    message_processing_time: ['p(95)<2000'], // Procesamiento de mensajes en menos de 2s
    errors: ['rate<0.05'],                // Tasa de error menor al 5%
  },
};

const BASE_URL = 'http://localhost:8000';
let authToken = '';

// Función de ayuda para generar datos aleatorios
function generateRandomString(length) {
  return Math.random().toString(36).substring(2, length + 2);
}

// Inicialización: Crear usuario y obtener token
export function setup() {
  const username = `user_${generateRandomString(8)}`;
  const password = `Test123!${generateRandomString(4)}`;

  // Registrar usuario
  const registerPayload = JSON.stringify({
    email: `${username}@test.com`,
    username: username,
    password: password,
  });

  http.post(`${BASE_URL}/users/`, registerPayload, {
    headers: { 'Content-Type': 'application/json' },
  });

  // Login
  const loginData = new FormData();
  loginData.append('username', username);
  loginData.append('password', password);

  const loginRes = http.post(`${BASE_URL}/token`, loginData);
  return {
    token: loginRes.json('access_token'),
    username: username,
  };
}

export default function(data) {
  const token = data.token;
  const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`,
  };

  // Crear un nuevo chat
  const chatPayload = JSON.stringify({
    title: `Performance Test Chat ${generateRandomString(8)}`,
  });

  const chatRes = http.post(`${BASE_URL}/chats/`, chatPayload, { headers });
  check(chatRes, {
    'chat creado correctamente': (r) => r.status === 200,
  });

  const chatId = chatRes.json('id');

  // Enviar varios mensajes
  for (let i = 0; i < 3; i++) {
    const messagePayload = JSON.stringify({
      content: `Test message ${i}: ${generateRandomString(16)}`,
      role: 'user',
    });

    const start = new Date();
    const messageRes = http.post(
      `${BASE_URL}/chats/${chatId}/messages/`,
      messagePayload,
      { headers }
    );
    const end = new Date();

    check(messageRes, {
      'mensaje enviado correctamente': (r) => r.status === 200,
      'respuesta del asistente recibida': (r) => r.json('assistant_message') !== undefined,
    });

    messageProcessingTime.add(end - start);
    errorRate.add(messageRes.status !== 200);

    sleep(1);
  }

  // Obtener historial de mensajes
  const historyRes = http.get(
    `${BASE_URL}/chats/${chatId}/messages/`,
    { headers }
  );

  check(historyRes, {
    'historial obtenido correctamente': (r) => r.status === 200,
    'historial contiene mensajes': (r) => r.json().length > 0,
  });

  sleep(2);
} 