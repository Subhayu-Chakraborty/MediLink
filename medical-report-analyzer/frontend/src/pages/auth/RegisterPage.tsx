/**
 * src/pages/auth/RegisterPage.tsx
 * Registration form with role-conditional fields.
 */
import { useState, type FC } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import AuthLayout from '../../layouts/AuthLayout'
import { useAuth } from '../../hooks/useAuth'
import { register as apiRegister } from '../../services/authService'
import LoadingSpinner from '../../components/common/LoadingSpinner'

const schema = z.object({
  full_name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Enter a valid email'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
  role: z.enum(['patient', 'doctor']),
  specialization: z.string().optional(),
  experience: z.coerce.number().optional(),
  hospital: z.string().optional(),
  age: z.coerce.number().optional(),
  gender: z.string().optional(),
}).refine(d => d.role !== 'doctor' || (d.specialization && d.specialization.length > 0), {
  message: 'Specialization is required for doctors',
  path: ['specialization'],
})

type FormData = z.infer<typeof schema>

const RegisterPage: FC = () => {
  const { login: authLogin } = useAuth()
  const navigate = useNavigate()
  const [serverError, setServerError] = useState('')

  const { register, handleSubmit, watch, formState: { errors, isSubmitting } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { role: 'patient' },
  })

  const role = watch('role')

  const onSubmit = async (data: FormData) => {
    setServerError('')
    try {
      const res = await apiRegister(data)
      authLogin(res.access_token, res.user)
      navigate(res.user.role === 'doctor' ? '/doctor/dashboard' : '/patient/dashboard')
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setServerError(msg || 'Registration failed. Please try again.')
    }
  }

  return (
    <AuthLayout title="Create an account" subtitle="Join MedReport AI today">
      <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
        {serverError && (
          <div className="alert-error">
            <svg className="w-4 h-4 shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd"/>
            </svg>
            {serverError}
          </div>
        )}

        {/* Role selector */}
        <div className="form-group">
          <label className="form-label">I am a</label>
          <div className="grid grid-cols-2 gap-2">
            {(['patient', 'doctor'] as const).map(r => (
              <label key={r}
                className={`flex items-center justify-center gap-2 p-3 rounded-lg border-2 cursor-pointer transition-all
                  ${role === r ? 'border-blue-500 bg-blue-50 text-blue-700' : 'border-slate-200 hover:border-slate-300'}`}>
                <input type="radio" value={r} {...register('role')} className="sr-only" />
                <span className="font-medium capitalize">{r}</span>
              </label>
            ))}
          </div>
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="full_name">Full name</label>
          <input id="full_name" type="text" className="form-input" placeholder="Dr. Jane Smith"
            {...register('full_name')} />
          {errors.full_name && <p className="form-error">{errors.full_name.message}</p>}
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="reg-email">Email address</label>
          <input id="reg-email" type="email" className="form-input" placeholder="you@example.com"
            {...register('email')} autoComplete="email" />
          {errors.email && <p className="form-error">{errors.email.message}</p>}
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="reg-password">Password</label>
          <input id="reg-password" type="password" className="form-input" placeholder="Min. 6 characters"
            {...register('password')} autoComplete="new-password" />
          {errors.password && <p className="form-error">{errors.password.message}</p>}
        </div>

        {/* Doctor-only fields */}
        {role === 'doctor' && (
          <>
            <div className="divider" />
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Doctor Information</p>
            <div className="form-group">
              <label className="form-label" htmlFor="specialization">Specialization *</label>
              <input id="specialization" type="text" className="form-input" placeholder="e.g. Cardiology"
                {...register('specialization')} />
              {errors.specialization && <p className="form-error">{errors.specialization.message}</p>}
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="form-group">
                <label className="form-label" htmlFor="experience">Years of experience</label>
                <input id="experience" type="number" min="0" className="form-input"
                  {...register('experience')} />
              </div>
              <div className="form-group">
                <label className="form-label" htmlFor="hospital">Hospital / Clinic</label>
                <input id="hospital" type="text" className="form-input" placeholder="Optional"
                  {...register('hospital')} />
              </div>
            </div>
          </>
        )}

        {/* Patient-only fields */}
        {role === 'patient' && (
          <>
            <div className="divider" />
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Optional Details</p>
            <div className="grid grid-cols-2 gap-3">
              <div className="form-group">
                <label className="form-label" htmlFor="age">Age</label>
                <input id="age" type="number" min="0" className="form-input"
                  {...register('age')} />
              </div>
              <div className="form-group">
                <label className="form-label" htmlFor="gender">Gender</label>
                <select id="gender" className="form-select" {...register('gender')}>
                  <option value="">Select</option>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="other">Other</option>
                </select>
              </div>
            </div>
          </>
        )}

        <button type="submit" className="btn-primary w-full mt-2" disabled={isSubmitting}>
          {isSubmitting ? <LoadingSpinner size="sm" /> : 'Create Account'}
        </button>

        <p className="text-center text-sm text-slate-500">
          Already have an account?{' '}
          <Link to="/login" className="text-blue-600 font-medium hover:underline">Sign in</Link>
        </p>
      </form>
    </AuthLayout>
  )
}

export default RegisterPage
