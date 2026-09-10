import axios from 'axios';

export const client = axios.create({

  baseURL: 'https://dev.reactionstack.135.106.217.211.sslip.io/api',
  
});

client.interceptors.request.use((config) => {

  const token = localStorage.getItem('token');

  if (token) config.headers.Authorization = `Bearer ${token}`;

  return config;
});

client.interceptors.response.use(
  (response) => response,

  (error) => {

    if (error.response?.status === 401) {

      localStorage.removeItem('token');
      window.location.href = '/login';

    }

    return Promise.reject(error);
  }
);