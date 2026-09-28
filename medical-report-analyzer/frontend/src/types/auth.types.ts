/** src/types/auth.types.ts */
export type UserRole = 'patient' | 'doctor' | 'admin'

export interface AuthUser {
  id: string
  email: string
  full_name: string
  role: UserRole
}

export interface AuthContextType {
  user: AuthUser | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (token: string, user: AuthUser) => void
  logout: () => void
}

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  full_name: string
  email: string
  password: string
  role: UserRole
  // Doctor extras
  specialization?: string
  experience?: number
  hospital?: string
  latitude?: number
  longitude?: number
  // Patient extras
  age?: number
  gender?: string
  phone?: string
}

export interface TokenResponse {
  access_token: string
  token_type: 'bearer'
  user: AuthUser
}
