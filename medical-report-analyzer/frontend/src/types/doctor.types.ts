/** src/types/doctor.types.ts */
export interface DoctorProfile {
  id: string
  user_id: string
  doctor_id: string
  full_name: string
  email: string
  specialization: string
  experience: number
  hospital?: string
  phone?: string
  bio?: string
  latitude?: number
  longitude?: number
}

export interface DoctorSearchResult {
  user_id: string
  doctor_id: string
  full_name: string
  specialization: string
  experience: number
  hospital?: string
  latitude?: number
  longitude?: number
}

export interface NearbyDoctorResult extends DoctorSearchResult {
  distance_km: number
}

export interface DoctorProfileUpdate {
  specialization?: string
  experience?: number
  hospital?: string
  phone?: string
  bio?: string
  latitude?: number
  longitude?: number
}

export interface PatientRequestItem {
  request_id: string
  patient_id: string
  patient_name: string
  patient_email: string
  status: 'pending' | 'accepted' | 'rejected'
  requested_at: string
}

export interface PatientSummary {
  user_id: string
  full_name: string
  email: string
  age?: number
  gender?: string
  report_count: number
}
