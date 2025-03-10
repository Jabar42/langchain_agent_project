import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// Métricas personalizadas
const errorRate = new Rate('errors');

// Configuración de las pruebas
export const options = {
  stages: [
    { duration: '1m', target: 50 },  // Ramp up a 50 usuarios en 1 minuto
    { duration: '3m', target: 50 },  // Mantener 50 usuarios por 3 minutos
    { duration: '1m', target: 100 }, // Ramp up a 100 usuarios en 1 minuto
    { duration: '3m', target: 100 }, // Mantener 100 usuarios por 3 minutos
    { duration: '1m', target: 0 },   // Ramp down a 0 usuarios en 1 minuto
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% de las peticiones deben completarse en menos de 500ms
    errors: ['rate<0.1'],            // La tasa de error debe ser menor al 10%
  },
};

const BASE_URL = 'http://localhost:8000';
let authToken = '';

// Función de ayuda para generar datos aleatorios
function generateRandomString(length) {
  return Math.random().toString(36).substring(2, length + 2);
}

// Escenario: Registro de usuario
export function registerUser() {
  const payload = JSON.stringify({
    email: `test_${generateRandomString(8)}@test.com`,
    username: `user_${generateRandomString(8)}`,
    password: `Test123!${generateRandomString(4)}`,
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  const res = http.post(`${BASE_URL}/users/`, payload, params);
  check(res, {
    'registro exitoso': (r) => r.status === 200,
  });
  errorRate.add(res.status !== 200);
  sleep(1);
}

// Escenario: Login
export function login() {
  const username = `user_${generateRandomString(8)}`;
  const password = `Test123!${generateRandomString(4)}`;

  // Primero registramos el usuario
  const registerPayload = JSON.stringify({
    email: `${username}@test.com`,
    username: username,
    password: password,
  });

  http.post(`${BASE_URL}/users/`, registerPayload, {
    headers: { 'Content-Type': 'application/json' },
  });

  // Luego intentamos el login
  const loginData = new FormData();
  loginData.append('username', username);
  loginData.append('password', password);

  const res = http.post(`${BASE_URL}/token`, loginData);
  check(res, {
    'login exitoso': (r) => r.status === 200,
    'token recibido': (r) => r.json('access_token') !== undefined,
  });

  if (res.status === 200) {
    authToken = res.json('access_token');
  }

  errorRate.add(res.status !== 200);
  sleep(1);
}

// Escenario: Crear chat
export function createChat() {
  if (!authToken) {
    login();
  }

  const payload = JSON.stringify({
    title: `Chat ${generateRandomString(8)}`,
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${authToken}`,
    },
  };

  const res = http.post(`${BASE_URL}/chats/`, payload, params);
  check(res, {
    'chat creado': (r) => r.status === 200,
  });
  errorRate.add(res.status !== 200);
  sleep(1);

  return res.json('id');
}

// Escenario: Enviar mensaje
export function sendMessage() {
  if (!authToken) {
    login();
  }

  const chatId = createChat();
  const payload = JSON.stringify({
    content: `Mensaje de prueba ${generateRandomString(16)}`,
    role: 'user',
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${authToken}`,
    },
  };

  const res = http.post(`${BASE_URL}/chats/${chatId}/messages/`, payload, params);
  check(res, {
    'mensaje enviado': (r) => r.status === 200,
    'respuesta recibida': (r) => r.json('assistant_message') !== undefined,
  });
  errorRate.add(res.status !== 200);
  sleep(1);
}

// Escenario por defecto que ejecuta una mezcla de todas las operaciones
export default function() {
  const scenarios = [registerUser, login, createChat, sendMessage];
  const randomScenario = scenarios[Math.floor(Math.random() * scenarios.length)];
  randomScenario();
} 