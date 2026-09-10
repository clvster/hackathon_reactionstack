import { useMutation } from '@tanstack/react-query';
import { client } from './client';

interface LoginPayload {
  username: string;
  password: string;
}

interface LoginResponse {
  access_token: string;
}

export function useLogin() {
  return useMutation({
    mutationFn: async (payload: LoginPayload) => {

      const { data } = await client.post<LoginResponse>('/auth/login', payload);
      
      localStorage.setItem('token', data.access_token);

      return data;

    },
  });
}