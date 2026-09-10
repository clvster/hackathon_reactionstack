import axios from 'axios';

export const client = axios.create({
<<<<<<< HEAD

  baseURL: 'http://127.0.0.1:8000',

=======
  baseURL: 'http://localhost:8000/api/v1',
>>>>>>> origin/dev
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