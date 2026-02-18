/**
 * API client for CareNav Florida backend
 */

// Parse the API URL to extract credentials if present
const rawApiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
let API_URL = rawApiUrl;
let authHeader: string | null = null;

// Check if URL contains credentials (user:pass@host format)
try {
  const url = new URL(rawApiUrl);
  if (url.username && url.password) {
    // Extract credentials and create Basic Auth header
    authHeader = 'Basic ' + btoa(`${url.username}:${url.password}`);
    // Remove credentials from URL
    url.username = '';
    url.password = '';
    API_URL = url.toString().replace(/\/$/, ''); // Remove trailing slash
  }
} catch {
  // If URL parsing fails, use as-is
  API_URL = rawApiUrl;
}

export interface Patient {
  id: number;
  first_name: string;
  last_name: string;
  date_of_birth: string;
  zip_code: string;
  county: string;
  current_location: string;
  care_level_needed: string;
  created_at: string;
}

export interface CareNeeds {
  bathing: boolean;
  dressing: boolean;
  toileting: boolean;
  transferring: boolean;
  eating: boolean;
  continence: boolean;
  medication_management: boolean;
  dementia_diagnosis: boolean;
  wandering_risk: boolean;
  behavioral_issues: boolean;
  skilled_nursing: boolean;
  physical_therapy: boolean;
  wound_care: boolean;
  iv_therapy: boolean;
}

export interface VeteranStatus {
  is_veteran: boolean;
  is_spouse_of_veteran: boolean;
  veteran_deceased: boolean;
  branch?: string;
  service_start?: string;
  service_end?: string;
  wartime_service: boolean;
  discharge_type?: string;
  dd214_available: boolean;
}

export interface Financials {
  social_security: number;
  pension: number;
  va_pension: number;
  other_income: number;
  checking: number;
  savings: number;
  cds: number;
  money_market: number;
  ira: number;
  four01k: number;
  brokerage: number;
  annuities: number;
  stocks: number;
  bonds: number;
  owns_home: boolean;
  home_value: number;
  home_mortgage: number;
  intends_to_return: boolean;
  vehicle_1_value: number;
  vehicle_2_value: number;
  life_insurance_face: number;
  life_insurance_cash: number;
  credit_card_debt: number;
  medical_debt: number;
  other_debt: number;
}

export interface Gift {
  gift_date: string;
  recipient: string;
  amount: number;
  description?: string;
  potentially_exempt: boolean;
}

export interface PatientCreate {
  first_name: string;
  last_name: string;
  date_of_birth: string;
  ssn_last_four?: string;
  address?: string;
  city?: string;
  state: string;
  zip_code: string;
  county: string;
  phone?: string;
  current_location: string;
  diagnosis?: string;
  discharge_date?: string;
  care_level_needed: string;
  care_needs?: CareNeeds;
  veteran_status?: VeteranStatus;
  financials?: Financials;
  gifts?: Gift[];
}

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

export interface ActionItem {
  action: string;
  priority: string;
  phone?: string;
  deadline?: string;
}

export interface ChatResponse {
  message: string;
  action_items: ActionItem[];
  warnings: string[];
  confidence: number;
}

export interface MedicaidResult {
  eligible: boolean;
  countable: number;
  over_by: number;
  asset_eligible: boolean;
  income_eligible: boolean;
  total_income: number;
  explanation: string;
}

export interface VAResult {
  eligible: boolean;
  type: string;
  monthly_benefit: number;
  explanation: string;
}

export interface GiftPenaltyResult {
  has_penalty: boolean;
  amount: number;
  months: number;
  mitigation: string;
}

export interface EligibilityResponse {
  medicaid: MedicaidResult;
  va_aa: VAResult;
  gift_penalty: GiftPenaltyResult;
  confidence: number;
}

export interface AffordabilityInfo {
  monthly_rate: number;
  patient_income: number;
  va_benefit: number;
  total_income: number;
  gap_or_surplus: number;
  affordable: boolean;
  needs_asset_draw: boolean;
  monthly_shortfall: number;
}

export interface FacilityResult {
  name: string;
  address: string;
  phone: string;
  license_type: string;
  capacity: number;
  beds_available?: number;
  rate_low: number;
  rate_high: number;
  accepts_medicaid: boolean;
  medicaid_day_one: boolean;
  memory_care: boolean;
  rating: number;
  distance_miles: number;
  match_score: number;
  affordability: AffordabilityInfo;
}

export interface Task {
  id: number;
  title: string;
  description?: string;
  category: string;
  priority: string;
  status: string;
  due_date?: string;
  phone?: string;
  notes?: string;
  created_at: string;
  // Ticket 2: Dependencies and Assignees
  depends_on?: number;
  blocked_by_task?: string;
  assignee?: string;
  assignee_phone?: string;
}

// API functions
async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  
  // Add auth header if credentials were extracted from URL
  if (authHeader) {
    headers['Authorization'] = authHeader;
  }
  
  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      ...headers,
      ...options?.headers,
    },
  });
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  return response.json();
}

// Patient API
export const patientApi = {
  create: (data: PatientCreate) => 
    fetchApi<Patient>('/api/patients/', { method: 'POST', body: JSON.stringify(data) }),
  
  get: (id: number) => 
    fetchApi<Patient>(`/api/patients/${id}`),
  
  list: () => 
    fetchApi<Patient[]>('/api/patients/'),
  
  getContext: (id: number) => 
    fetchApi<Record<string, unknown>>(`/api/patients/${id}/context`),
};

// Chat API
export const chatApi = {
  send: (message: string, patientId?: number, history?: ChatMessage[]) =>
    fetchApi<ChatResponse>('/api/chat/', {
      method: 'POST',
      body: JSON.stringify({
        message,
        patient_id: patientId,
        conversation_history: history,
      }),
    }),
  
  getHistory: (patientId: number, limit = 50) =>
    fetchApi<ChatMessage[]>(`/api/chat/history/${patientId}?limit=${limit}`),
};

// Eligibility API
export const eligibilityApi = {
  check: (patientId?: number, financials?: Financials, veteranStatus?: VeteranStatus, gifts?: Gift[]) =>
    fetchApi<EligibilityResponse>('/api/eligibility/check', {
      method: 'POST',
      body: JSON.stringify({
        patient_id: patientId,
        financials,
        veteran_status: veteranStatus,
        gifts,
      }),
    }),
  
  getSpendDownOptions: (amount: number) =>
    fetchApi<{ amount_to_spend: number; options: unknown[]; total_covered: number; warning: string }>(
      `/api/eligibility/spend-down/${amount}`
    ),
  
  checkDebtPayment: (debtType: string, debtHolder: string, jointAccount = false) =>
    fetchApi<{ guidance: string; explanation: string; legal_basis: string[]; risk_level: string; warnings: string[] }>(
      `/api/eligibility/debt-check?debt_type=${debtType}&debt_holder=${debtHolder}&joint_account=${jointAccount}`,
      { method: 'POST' }
    ),
};

// Facility API
export const facilityApi = {
  search: (zipCode: string, careLevel: string, radiusMiles = 20, medicaidRequired = true, patientIncome = 0, vaBenefit = 0) =>
    fetchApi<{ facilities: FacilityResult[]; search_criteria: Record<string, unknown>; total_found: number }>(
      '/api/facilities/search',
      {
        method: 'POST',
        body: JSON.stringify({
          zip_code: zipCode,
          care_level: careLevel,
          radius_miles: radiusMiles,
          medicaid_required: medicaidRequired,
          patient_income: patientIncome,
          va_benefit: vaBenefit,
        }),
      }
    ),
  
  get: (id: number) =>
    fetchApi<FacilityResult>(`/api/facilities/${id}`),
  
  saveMatch: (patientId: number, facilityId: number, matchScore: number, notes?: string) =>
    fetchApi<{ id: number; status: string }>(
      `/api/facilities/match/${patientId}/${facilityId}?match_score=${matchScore}${notes ? `&notes=${notes}` : ''}`,
      { method: 'POST' }
    ),
  
  getMatches: (patientId: number) =>
    fetchApi<unknown[]>(`/api/facilities/matches/${patientId}`),
};

// Task API
export const taskApi = {
  create: (patientId: number, data: { title: string; description?: string; category?: string; priority?: string; due_date?: string; phone?: string }) =>
    fetchApi<Task>(`/api/tasks/?patient_id=${patientId}`, { method: 'POST', body: JSON.stringify(data) }),
  
  list: (patientId: number, status?: string) =>
    fetchApi<Task[]>(`/api/tasks/${patientId}${status ? `?status=${status}` : ''}`),
  
  updateStatus: (taskId: number, status: string) =>
    fetchApi<{ id: number; status: string }>(`/api/tasks/${taskId}/status?status=${status}`, { method: 'PATCH' }),
  
  updateNote: (taskId: number, note: string) =>
    fetchApi<{ id: number; notes: string }>(`/api/tasks/${taskId}/note`, { method: 'PATCH', body: JSON.stringify({ note }) }),
  
  delete: (taskId: number) =>
    fetchApi<{ deleted: boolean }>(`/api/tasks/${taskId}`, { method: 'DELETE' }),
};

// Document interface
export interface Document {
  id: number;
  patient_id: number;
  name: string;
  category: string | null;
  doc_type: string | null;
  status: string;
  content: string | null;
  extracted_data: Record<string, unknown> | null;
  ai_analysis: string | null;
  notes: string | null;
  // Ticket 7: Document Location + Procurement
  physical_location?: string;
  procurement_status?: string;
  ordered_from?: string;
  expected_delivery?: string;
  copies_needed?: number;
  copies_on_hand?: number;
  needed_for?: string;
}

// Documents API
export const documentsApi = {
  list: (patientId: number) =>
    fetchApi<Document[]>(`/api/documents/${patientId}/`),
  
  generateDemo: (patientId: number) =>
    fetchApi<{ message: string; count: number }>(`/api/documents/${patientId}/generate-demo/`, { method: 'POST' }),
};

// Ticket 3: Bill interface
export interface Bill {
  id: number;
  vendor: string;
  amount: number;
  due_date: string | null;
  status: string;
  amount_paid: number;
  category: string | null;
  contact_name: string | null;
  contact_phone: string | null;
  payment_link: string | null;
  recurring: boolean;
  notes: string | null;
  created_at: string;
}

// Ticket 4: Income Phase interface
export interface IncomePhase {
  id: number;
  phase_name: string;
  monthly_amount: number;
  source: string | null;
  status: string;
  estimated_start: string | null;
  notes: string | null;
  created_at: string;
}

// Ticket 5: Benefit Application interface
export interface BenefitApplication {
  id: number;
  benefit_type: string;
  display_name: string | null;
  status: string;
  monthly_amount: number | null;
  submitted_date: string | null;
  expected_weeks: number | null;
  missing_documents: string | null;
  contact_phone: string | null;
  notes: string | null;
  created_at: string;
}

// Ticket 6: Contact interface
export interface Contact {
  id: number;
  name: string;
  organization: string | null;
  role: string | null;
  phone: string | null;
  email: string | null;
  category: string | null;
  notes: string | null;
  created_at: string;
}

// Ticket 8: Asset interface
export interface Asset {
  id: number;
  name: string;
  asset_type: string | null;
  owner: string | null;
  estimated_value: number | null;
  title_status: string;
  sale_status: string;
  sale_channel: string | null;
  actual_sale_price: number | null;
  sale_date: string | null;
  linked_insurance: string | null;
  notes: string | null;
  created_at: string;
}

// Bills API (Ticket 3)
export const billsApi = {
  list: (patientId: number) =>
    fetchApi<Bill[]>(`/api/bills/${patientId}`),
  
  getSummary: (patientId: number) =>
    fetchApi<{ bills: Bill[]; total_due: number; next_due_date: string | null; overdue_count: number; total_bills: number }>(`/api/bills/${patientId}/summary`),
};

// Income Phases API (Ticket 4)
export const incomePhasesApi = {
  list: (patientId: number) =>
    fetchApi<IncomePhase[]>(`/api/income-phases/${patientId}`),
  
  getTimeline: (patientId: number) =>
    fetchApi<{ phases: IncomePhase[]; current_income: number; projected_income: number; total_phases: number }>(`/api/income-phases/${patientId}/timeline`),
};

// Benefit Applications API (Ticket 5)
export const benefitApplicationsApi = {
  list: (patientId: number) =>
    fetchApi<BenefitApplication[]>(`/api/benefit-applications/${patientId}`),
  
  getPipeline: (patientId: number) =>
    fetchApi<{ pipeline: Record<string, BenefitApplication[]>; total_potential_monthly: number; total_applications: number }>(`/api/benefit-applications/${patientId}/pipeline`),
};

// Contacts API (Ticket 6)
export const contactsApi = {
  list: (patientId: number) =>
    fetchApi<Contact[]>(`/api/contacts/${patientId}`),
  
  getGrouped: (patientId: number) =>
    fetchApi<{ grouped: Record<string, Contact[]>; total_contacts: number }>(`/api/contacts/${patientId}/grouped`),
};

// Assets API (Ticket 8)
export const assetsApi = {
  list: (patientId: number) =>
    fetchApi<Asset[]>(`/api/assets/${patientId}`),
  
  getPipeline: (patientId: number) =>
    fetchApi<{ pipeline: Record<string, Asset[]>; total_estimated_value: number; total_sold_value: number; pending_title: Asset[]; total_assets: number }>(`/api/assets/${patientId}/pipeline`),
};

// NEW: Medical Info interfaces
export interface MedicalInfo {
  id: number;
  patient_id: number;
  medicare_id: string | null;
  medicaid_id: string | null;
  physician_name: string | null;
  physician_phone: string | null;
  blood_pressure: string | null;
  pulse: number | null;
  temperature: number | null;
  respiration: number | null;
  vitals_date: string | null;
  allergies: string | null;
  diet: string | null;
  code_status: string | null;
}

export interface Diagnosis {
  id: number;
  patient_id: number;
  name: string;
  icd_code: string | null;
  diagnosis_date: string | null;
  is_primary: boolean;
  notes: string | null;
}

export interface Medication {
  id: number;
  patient_id: number;
  name: string;
  dosage: string | null;
  frequency: string | null;
  route: string | null;
  purpose: string | null;
  prescriber: string | null;
  start_date: string | null;
  notes: string | null;
}

export interface FullMedicalResponse {
  info: MedicalInfo | null;
  diagnoses: Diagnosis[];
  medications: Medication[];
}

// NEW: Insurance interface
export interface Insurance {
  id: number;
  patient_id: number;
  insurance_type: string | null;
  carrier: string | null;
  policy_number: string | null;
  group_number: string | null;
  subscriber_name: string | null;
  subscriber_id: string | null;
  effective_date: string | null;
  termination_date: string | null;
  phone: string | null;
  status: string;
  notes: string | null;
}

// NEW: Selected Facility interface
export interface SelectedFacility {
  id: number;
  patient_id: number;
  name: string;
  address: string | null;
  apt_number: string | null;
  phone: string | null;
  fax: string | null;
  admissions_contact: string | null;
  community_rep: string | null;
  keys_date: string | null;
  move_in_date: string | null;
  base_rent: number | null;
  vet_discount_pct: number | null;
  care_level: string | null;
  care_level_cost: number | null;
  total_monthly: number | null;
  deposit_amount: number | null;
  deposit_paid: boolean;
  community_fee: number | null;
  status: string;
  notes: string | null;
}

// NEW: Win interface
export interface Win {
  id: number;
  patient_id: number;
  title: string;
  description: string | null;
  amount: number | null;
  amount_type: string | null;
  win_date: string | null;
  category: string | null;
}

// Medical API
export const medicalApi = {
  get: (patientId: number) =>
    fetchApi<FullMedicalResponse>(`/api/medical/${patientId}`),
};

// Insurance API
export const insuranceApi = {
  list: (patientId: number) =>
    fetchApi<Insurance[]>(`/api/insurance/${patientId}`),
};

// Selected Facility API
export const selectedFacilityApi = {
  get: (patientId: number) =>
    fetchApi<SelectedFacility | null>(`/api/selected-facility/${patientId}`),
};

// Wins API
export const winsApi = {
  list: (patientId: number) =>
    fetchApi<Win[]>(`/api/wins/${patientId}`),
};

// Document Parsing API
export interface ParsedDataResponse {
  success: boolean;
  document_type: string;
  extracted_data: Record<string, unknown>;
  records_created: string[];
  unstructured_data: Record<string, unknown> | null;
}

export const documentParseApi = {
  parse: (patientId: number, content: string, documentType?: string) =>
    fetchApi<ParsedDataResponse>('/api/documents/parse/', {
      method: 'POST',
      body: JSON.stringify({
        patient_id: patientId,
        content,
        document_type: documentType,
      }),
    }),
};
