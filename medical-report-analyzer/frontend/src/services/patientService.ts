/**
 * src/services/patientService.ts
 * Patient API calls: profile, doctor requests.
 */
import api from './api'
import type { PatientProfile, DoctorRequestStatus } from '../types/patient.types'

export async function getMyProfile(): Promise<PatientProfile> {
  const res = await api.get<PatientProfile>('/patients/profile')
  return res.data
}

export async function updateMyProfile(data: Partial<PatientProfile>): Promise<PatientProfile> {
  const res = await api.patch<PatientProfile>('/patients/profile', data)
  return res.data
}

export async function sendDoctorRequest(doctorId: string): Promise<{ message: string; request_id: string; status: string }> {
  const res = await api.post('/patients/doctor-requests', { doctor_id: doctorId })
  return res.data
}

export async function getMyDoctorRequests(): Promise<DoctorRequestStatus[]> {
  const res = await api.get<DoctorRequestStatus[]>('/patients/doctor-requests')
  return res.data
}
