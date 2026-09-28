/** src/types/patient.types.ts */
export interface PatientProfile {
  user_id: string
  full_name: string
  email: string
  age?: number
  gender?: string
  blood_group?: string
  phone?: string
  address?: string
  emergency_contact?: string
}

export interface DoctorRequestStatus {
  request_id: string
  doctor_user_id: string
  doctor_id: string
  doctor_name: string
  doctor_specialization: string
  status: 'pending' | 'accepted' | 'rejected'
  requested_at: string
  responded_at?: string
}
