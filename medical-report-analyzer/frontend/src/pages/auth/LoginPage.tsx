/**
 * src/pages/auth/LoginPage.tsx
 * Full login form with validation and error handling.
 */
import { useState, type FC } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import AuthLayout from '../../layouts/AuthLayout'
import { useAuth } from '../../hooks/useAuth'
import { login } from '../../services/authService'
import LoadingSpinner from '../../components/common/LoadingSpinner'

const schema = z.object({
  email: z.string().email('Enter a valid email address'),
  password: z.string().min(1, 'Password is required'),
})
type FormData = z.infer<typeof schema>

const LoginPage: FC = () => {
  const { login: authLogin } = useAuth()
  const navigate = useNavigate()
  const [serverError, setServerError] = useState('')

  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<FormData>({
    resolver: zodResolver(schema),
  })

  const onSubmit = async (data: FormData) => {
    setServerError('')
    try {
      const res = await login(data)
      authLogin(res.access_token, res.user)
      navigate(res.user.role === 'doctor' ? '/doctor/dashboard' : '/patient/dashboard')
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setServerError(msg || 'Login failed. Please check your credentials.')
    }
  }

  return (
    <AuthLayout title="Welcome back" subtitle="Sign in to your account">
      <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
        {serverError && (
          <div className="alert-error">
            <svg className="w-4 h-4 shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd"/>
            </svg>
            {serverError}
          </div>
        )}

        <div className="form-group">
          <label className="form-label" htmlFor="email">Email address</label>
          <input id="email" type="email" className="form-input" placeholder="you@example.com"
            {...register('email')} autoComplete="email" />
          {errors.email && <p className="form-error">{errors.email.message}</p>}
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="password">Password</label>
          <input id="password" type="password" className="form-input" placeholder="••••••••"
            {...register('password')} autoComplete="current-password" />
          {errors.password && <p className="form-error">{errors.password.message}</p>}
        </div>

        <button type="submit" className="btn-primary w-full mt-2" disabled={isSubmitting}>
          {isSubmitting ? <LoadingSpinner size="sm" /> : 'Sign In'}
        </button>

        <p className="text-center text-sm text-slate-500">
          Don't have an account?{' '}
          <Link to="/register" className="text-blue-600 font-medium hover:underline">Create one</Link>
        </p>
      </form>
    </AuthLayout>
  )
}

export default LoginPage
