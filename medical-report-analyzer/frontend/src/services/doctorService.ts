/**
 * src/services/doctorService.ts
 * Doctor API calls: search, profile, requests, patients.
 */
import api from './api'
import type { DoctorProfile, DoctorSearchResult, PatientRequestItem, PatientSummary } from '../types/doctor.types'
import type { ReportDetail, ReportListItem } from '../types/report.types'

export async function searchDoctor(doctorId: string): Promise<DoctorSearchResult> {
  const res = await api.get<DoctorSearchResult>('/doctors/search', { params: { doctor_id: doctorId } })
  return res.data
}

export async function getMyProfile(): Promise<DoctorProfile> {
  const res = await api.get<DoctorProfile>('/doctors/profile')
  return res.data
}

export async function getPendingRequests(): Promise<PatientRequestItem[]> {
  const res = await api.get<PatientRequestItem[]>('/doctors/requests')
  return res.data
}

export async function respondToRequest(requestId: string, accept: boolean): Promise<{ message: string; status: string }> {
  const res = await api.patch(`/doctors/requests/${requestId}/respond`, { accept })
  return res.data
}

export async function getMyPatients(): Promise<PatientSummary[]> {
  const res = await api.get<PatientSummary[]>('/doctors/patients')
  return res.data
}

export async function getPatientReports(patientId: string): Promise<ReportListItem[]> {
  const res = await api.get<ReportListItem[]>(`/doctors/patients/${patientId}/reports`)
  return res.data
}

export async function getPatientReport(patientId: string, reportId: string): Promise<ReportDetail> {
  const res = await api.get<ReportDetail>(`/doctors/patients/${patientId}/reports/${reportId}`)
  return res.data
}
