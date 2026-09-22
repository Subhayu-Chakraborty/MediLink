/**
 * src/services/authService.ts
 * Handles authentication API calls.
 */
import api from './api'
import type { LoginRequest, RegisterRequest, TokenResponse } from '../types/auth.types'

export async function login(payload: LoginRequest): Promise<TokenResponse> {
  const res = await api.post<TokenResponse>('/auth/login', payload)
  return res.data
}

export async function register(payload: RegisterRequest): Promise<TokenResponse> {
  const res = await api.post<TokenResponse>('/auth/register', payload)
  return res.data
}

export async function logout(): Promise<void> {
  await api.post('/auth/logout')
}

export async function getMe(): Promise<TokenResponse['user']> {
  const res = await api.get<TokenResponse['user']>('/auth/me')
  return res.data
}
