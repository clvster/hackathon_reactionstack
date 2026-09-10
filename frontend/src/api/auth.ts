import { useMutation } from '@tanstack/react-query';
import { client } from './client';

interface LoginPayload {
  username: string;
  password: string;
}

interface LoginResponse {
  access_token: string;
  token_type: string;
}

export function useLogin() {
  return useMutation({
    mutationFn: async (payload: LoginPayload) => {
      // Преобразуем payload в URLSearchParams для x-www-form-urlencoded
      const formData = new URLSearchParams();
      formData.append('username', payload.username);
      formData.append('password', payload.password);

      // Отправляем POST-запрос на эндпоинт /auth/login
      const { data } = await client.post<LoginResponse>('/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      localStorage.setItem('token', data.access_token);
      localStorage.setItem('token_type', data.token_type);
      return data;
    },
  });
}