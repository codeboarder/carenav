// Built by Gregory Katz and Rick Weyenberg
// Code is as-is, open source

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Progress } from '@/components/ui/progress';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { X, ChevronLeft, ChevronRight } from 'lucide-react';
import { patientApi, type PatientCreate, type Patient } from '@/lib/api';

interface IntakeWizardProps {
  onComplete: (patient: Patient) => void;
  onClose: () => void;
}

const STEPS = [
  'Basic Info',
  'Location',
  'Current Status',
  'Care Needs',
  'Veteran Status',
  'Income',
  'Bank Accounts',
  'Investments',
  'Property',
  'Review',
];

export default function IntakeWizard({ onComplete, onClose }: IntakeWizardProps) {
  const [step, setStep] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState<PatientCreate>({
    first_name: '',
    last_name: '',
    date_of_birth: '',
    state: 'FL',
    zip_code: '',
    county: '',
    current_location: 'home',
    care_level_needed: 'AL',
    care_needs: {
      bathing: false,
      dressing: false,
      toileting: false,
      transferring: false,
      eating: false,
      continence: false,
      medication_management: false,
      dementia_diagnosis: false,
      wandering_risk: false,
      behavioral_issues: false,
      skilled_nursing: false,
      physical_therapy: false,
      wound_care: false,
      iv_therapy: false,
    },
    veteran_status: {
      is_veteran: false,
      is_spouse_of_veteran: false,
      veteran_deceased: false,
      wartime_service: false,
      dd214_available: false,
    },
    financials: {
      social_security: 0,
      pension: 0,
      va_pension: 0,
      other_income: 0,
      checking: 0,
      savings: 0,
      cds: 0,
      money_market: 0,
      ira: 0,
      four01k: 0,
      brokerage: 0,
      annuities: 0,
      stocks: 0,
      bonds: 0,
      owns_home: false,
      home_value: 0,
      home_mortgage: 0,
      intends_to_return: true,
      vehicle_1_value: 0,
      vehicle_2_value: 0,
      life_insurance_face: 0,
      life_insurance_cash: 0,
      credit_card_debt: 0,
      medical_debt: 0,
      other_debt: 0,
    },
  });

  const updateField = (field: string, value: unknown) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const updateNestedField = (parent: string, field: string, value: unknown) => {
    setFormData((prev) => ({
      ...prev,
      [parent]: { ...(prev[parent as keyof PatientCreate] as object), [field]: value },
    }));
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    try {
      const patient = await patientApi.create(formData);
      onComplete(patient);
    } catch (error) {
      console.error('Failed to create patient:', error);
      alert('Failed to create patient. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderStep = () => {
    switch (step) {
      case 0: // Basic Info
        return (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="first_name">First Name</Label>
                <Input
                  id="first_name"
                  value={formData.first_name}
                  onChange={(e) => updateField('first_name', e.target.value)}
                  className="bg-slate-700 border-slate-600"
                />
              </div>
              <div>
                <Label htmlFor="last_name">Last Name</Label>
                <Input
                  id="last_name"
                  value={formData.last_name}
                  onChange={(e) => updateField('last_name', e.target.value)}
                  className="bg-slate-700 border-slate-600"
                />
              </div>
            </div>
            <div>
              <Label htmlFor="dob">Date of Birth</Label>
              <Input
                id="dob"
                type="date"
                value={formData.date_of_birth}
                onChange={(e) => updateField('date_of_birth', e.target.value)}
                className="bg-slate-700 border-slate-600"
              />
            </div>
            <div>
              <Label htmlFor="phone">Phone Number</Label>
              <Input
                id="phone"
                type="tel"
                value={formData.phone || ''}
                onChange={(e) => updateField('phone', e.target.value)}
                className="bg-slate-700 border-slate-600"
              />
            </div>
          </div>
        );

      case 1: // Location
        return (
          <div className="space-y-4">
            <div>
              <Label htmlFor="address">Street Address</Label>
              <Input
                id="address"
                value={formData.address || ''}
                onChange={(e) => updateField('address', e.target.value)}
                className="bg-slate-700 border-slate-600"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="city">City</Label>
                <Input
                  id="city"
                  value={formData.city || ''}
                  onChange={(e) => updateField('city', e.target.value)}
                  className="bg-slate-700 border-slate-600"
                />
              </div>
              <div>
                <Label htmlFor="zip">ZIP Code</Label>
                <Input
                  id="zip"
                  value={formData.zip_code}
                  onChange={(e) => updateField('zip_code', e.target.value)}
                  className="bg-slate-700 border-slate-600"
                />
              </div>
            </div>
            <div>
              <Label htmlFor="county">County</Label>
              <Select value={formData.county} onValueChange={(v) => updateField('county', v)}>
                <SelectTrigger className="bg-slate-700 border-slate-600">
                  <SelectValue placeholder="Select county" />
                </SelectTrigger>
                <SelectContent>
                  {['Palm Beach', 'Broward', 'Miami-Dade', 'Orange', 'Hillsborough', 'Pinellas', 'Duval', 'Lee', 'Polk', 'Brevard'].map((c) => (
                    <SelectItem key={c} value={c}>{c}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        );

      case 2: // Current Status
        return (
          <div className="space-y-4">
            <div>
              <Label>Current Location</Label>
              <Select value={formData.current_location} onValueChange={(v) => updateField('current_location', v)}>
                <SelectTrigger className="bg-slate-700 border-slate-600">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="home">At Home</SelectItem>
                  <SelectItem value="hospital">In Hospital</SelectItem>
                  <SelectItem value="rehab">In Rehab Facility</SelectItem>
                  <SelectItem value="alf">In Assisted Living</SelectItem>
                  <SelectItem value="snf">In Nursing Home</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Care Level Needed</Label>
              <Select value={formData.care_level_needed} onValueChange={(v) => updateField('care_level_needed', v)}>
                <SelectTrigger className="bg-slate-700 border-slate-600">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="AL">Assisted Living (AL)</SelectItem>
                  <SelectItem value="MC">Memory Care (MC)</SelectItem>
                  <SelectItem value="SNF">Skilled Nursing (SNF)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="diagnosis">Primary Diagnosis</Label>
              <Input
                id="diagnosis"
                value={formData.diagnosis || ''}
                onChange={(e) => updateField('diagnosis', e.target.value)}
                placeholder="e.g., Dementia, Stroke, Parkinson's"
                className="bg-slate-700 border-slate-600"
              />
            </div>
            <div>
              <Label htmlFor="discharge">Expected Discharge Date (if applicable)</Label>
              <Input
                id="discharge"
                type="date"
                value={formData.discharge_date || ''}
                onChange={(e) => updateField('discharge_date', e.target.value)}
                className="bg-slate-700 border-slate-600"
              />
            </div>
          </div>
        );

      case 3: // Care Needs
        return (
          <div className="space-y-4">
            <p className="text-sm text-slate-400">Select all that apply:</p>
            <div className="grid grid-cols-2 gap-3">
              {[
                { key: 'bathing', label: 'Bathing' },
                { key: 'dressing', label: 'Dressing' },
                { key: 'toileting', label: 'Toileting' },
                { key: 'transferring', label: 'Transferring' },
                { key: 'eating', label: 'Eating' },
                { key: 'continence', label: 'Continence' },
                { key: 'medication_management', label: 'Medication Management' },
                { key: 'dementia_diagnosis', label: 'Dementia Diagnosis' },
                { key: 'wandering_risk', label: 'Wandering Risk' },
                { key: 'behavioral_issues', label: 'Behavioral Issues' },
                { key: 'skilled_nursing', label: 'Skilled Nursing' },
                { key: 'physical_therapy', label: 'Physical Therapy' },
              ].map(({ key, label }) => (
                <label key={key} className="flex items-center gap-2 p-2 bg-slate-700 rounded cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.care_needs?.[key as keyof typeof formData.care_needs] || false}
                    onChange={(e) => updateNestedField('care_needs', key, e.target.checked)}
                    className="rounded"
                  />
                  <span className="text-sm">{label}</span>
                </label>
              ))}
            </div>
          </div>
        );

      case 4: // Veteran Status
        return (
          <div className="space-y-4">
            <div className="space-y-3">
              <label className="flex items-center gap-2 p-3 bg-slate-700 rounded cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.veteran_status?.is_veteran || false}
                  onChange={(e) => updateNestedField('veteran_status', 'is_veteran', e.target.checked)}
                  className="rounded"
                />
                <span>Patient is a veteran</span>
              </label>
              <label className="flex items-center gap-2 p-3 bg-slate-700 rounded cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.veteran_status?.is_spouse_of_veteran || false}
                  onChange={(e) => updateNestedField('veteran_status', 'is_spouse_of_veteran', e.target.checked)}
                  className="rounded"
                />
                <span>Patient is spouse of a veteran</span>
              </label>
              {formData.veteran_status?.is_spouse_of_veteran && (
                <label className="flex items-center gap-2 p-3 bg-slate-700 rounded cursor-pointer ml-4">
                  <input
                    type="checkbox"
                    checked={formData.veteran_status?.veteran_deceased || false}
                    onChange={(e) => updateNestedField('veteran_status', 'veteran_deceased', e.target.checked)}
                    className="rounded"
                  />
                  <span>Veteran spouse is deceased</span>
                </label>
              )}
              {(formData.veteran_status?.is_veteran || formData.veteran_status?.is_spouse_of_veteran) && (
                <>
                  <label className="flex items-center gap-2 p-3 bg-slate-700 rounded cursor-pointer">
                    <input
                      type="checkbox"
                      checked={formData.veteran_status?.wartime_service || false}
                      onChange={(e) => updateNestedField('veteran_status', 'wartime_service', e.target.checked)}
                      className="rounded"
                    />
                    <span>Served during wartime (WWII, Korea, Vietnam, Gulf War)</span>
                  </label>
                  <label className="flex items-center gap-2 p-3 bg-slate-700 rounded cursor-pointer">
                    <input
                      type="checkbox"
                      checked={formData.veteran_status?.dd214_available || false}
                      onChange={(e) => updateNestedField('veteran_status', 'dd214_available', e.target.checked)}
                      className="rounded"
                    />
                    <span>DD-214 available</span>
                  </label>
                </>
              )}
            </div>
          </div>
        );

      case 5: // Income
        return (
          <div className="space-y-4">
            <p className="text-sm text-slate-400">Enter monthly income amounts:</p>
            <div className="space-y-3">
              <div>
                <Label htmlFor="ss">Social Security</Label>
                <Input
                  id="ss"
                  type="number"
                  value={formData.financials?.social_security || 0}
                  onChange={(e) => updateNestedField('financials', 'social_security', parseFloat(e.target.value) || 0)}
                  className="bg-slate-700 border-slate-600"
                />
              </div>
              <div>
                <Label htmlFor="pension">Pension</Label>
                <Input
                  id="pension"
                  type="number"
                  value={formData.financials?.pension || 0}
                  onChange={(e) => updateNestedField('financials', 'pension', parseFloat(e.target.value) || 0)}
                  className="bg-slate-700 border-slate-600"
                />
              </div>
              <div>
                <Label htmlFor="va_pension">VA Pension (if receiving)</Label>
                <Input
                  id="va_pension"
                  type="number"
                  value={formData.financials?.va_pension || 0}
                  onChange={(e) => updateNestedField('financials', 'va_pension', parseFloat(e.target.value) || 0)}
                  className="bg-slate-700 border-slate-600"
                />
              </div>
              <div>
                <Label htmlFor="other_income">Other Income</Label>
                <Input
                  id="other_income"
                  type="number"
                  value={formData.financials?.other_income || 0}
                  onChange={(e) => updateNestedField('financials', 'other_income', parseFloat(e.target.value) || 0)}
                  className="bg-slate-700 border-slate-600"
                />
              </div>
            </div>
          </div>
        );

      case 6: // Bank Accounts
        return (
          <div className="space-y-4">
            <p className="text-sm text-slate-400">Enter current balances:</p>
            <div className="space-y-3">
              <div>
                <Label htmlFor="checking">Checking Account</Label>
                <Input
                  id="checking"
                  type="number"
                  value={formData.financials?.checking || 0}
                  onChange={(e) => updateNestedField('financials', 'checking', parseFloat(e.target.value) || 0)}
                  className="bg-slate-700 border-slate-600"
                />
              </div>
              <div>
                <Label htmlFor="savings">Savings Account</Label>
                <Input
                  id="savings"
                  type="number"
                  value={formData.financials?.savings || 0}
                  onChange={(e) => updateNestedField('financials', 'savings', parseFloat(e.target.value) || 0)}
                  className="bg-slate-700 border-slate-600"
                />
              </div>
              <div>
                <Label htmlFor="cds">CDs</Label>
                <Input
                  id="cds"
                  type="number"
                  value={formData.financials?.cds || 0}
                  onChange={(e) => updateNestedField('financials', 'cds', parseFloat(e.target.value) || 0)}
                  className="bg-slate-700 border-slate-600"
                />
              </div>
              <div>
                <Label htmlFor="money_market">Money Market</Label>
                <Input
                  id="money_market"
                  type="number"
                  value={formData.financials?.money_market || 0}
                  onChange={(e) => updateNestedField('financials', 'money_market', parseFloat(e.target.value) || 0)}
                  className="bg-slate-700 border-slate-600"
                />
              </div>
            </div>
          </div>
        );

      case 7: // Investments
        return (
          <div className="space-y-4">
            <p className="text-sm text-slate-400">Enter current values:</p>
            <div className="space-y-3">
              <div>
                <Label htmlFor="ira">IRA</Label>
                <Input
                  id="ira"
                  type="number"
                  value={formData.financials?.ira || 0}
                  onChange={(e) => updateNestedField('financials', 'ira', parseFloat(e.target.value) || 0)}
                  className="bg-slate-700 border-slate-600"
                />
              </div>
              <div>
                <Label htmlFor="401k">401(k)</Label>
                <Input
                  id="401k"
                  type="number"
                  value={formData.financials?.four01k || 0}
                  onChange={(e) => updateNestedField('financials', 'four01k', parseFloat(e.target.value) || 0)}
                  className="bg-slate-700 border-slate-600"
                />
              </div>
              <div>
                <Label htmlFor="brokerage">Brokerage Account</Label>
                <Input
                  id="brokerage"
                  type="number"
                  value={formData.financials?.brokerage || 0}
                  onChange={(e) => updateNestedField('financials', 'brokerage', parseFloat(e.target.value) || 0)}
                  className="bg-slate-700 border-slate-600"
                />
              </div>
              <div>
                <Label htmlFor="annuities">Annuities</Label>
                <Input
                  id="annuities"
                  type="number"
                  value={formData.financials?.annuities || 0}
                  onChange={(e) => updateNestedField('financials', 'annuities', parseFloat(e.target.value) || 0)}
                  className="bg-slate-700 border-slate-600"
                />
              </div>
            </div>
          </div>
        );

      case 8: // Property
        return (
          <div className="space-y-4">
            <label className="flex items-center gap-2 p-3 bg-slate-700 rounded cursor-pointer">
              <input
                type="checkbox"
                checked={formData.financials?.owns_home || false}
                onChange={(e) => updateNestedField('financials', 'owns_home', e.target.checked)}
                className="rounded"
              />
              <span>Owns home</span>
            </label>
            {formData.financials?.owns_home && (
              <div className="space-y-3 ml-4">
                <div>
                  <Label htmlFor="home_value">Home Value</Label>
                  <Input
                    id="home_value"
                    type="number"
                    value={formData.financials?.home_value || 0}
                    onChange={(e) => updateNestedField('financials', 'home_value', parseFloat(e.target.value) || 0)}
                    className="bg-slate-700 border-slate-600"
                  />
                </div>
                <div>
                  <Label htmlFor="mortgage">Mortgage Balance</Label>
                  <Input
                    id="mortgage"
                    type="number"
                    value={formData.financials?.home_mortgage || 0}
                    onChange={(e) => updateNestedField('financials', 'home_mortgage', parseFloat(e.target.value) || 0)}
                    className="bg-slate-700 border-slate-600"
                  />
                </div>
              </div>
            )}
            <div>
              <Label htmlFor="vehicle1">Primary Vehicle Value</Label>
              <Input
                id="vehicle1"
                type="number"
                value={formData.financials?.vehicle_1_value || 0}
                onChange={(e) => updateNestedField('financials', 'vehicle_1_value', parseFloat(e.target.value) || 0)}
                className="bg-slate-700 border-slate-600"
              />
            </div>
            <div>
              <Label htmlFor="vehicle2">Second Vehicle Value (if any)</Label>
              <Input
                id="vehicle2"
                type="number"
                value={formData.financials?.vehicle_2_value || 0}
                onChange={(e) => updateNestedField('financials', 'vehicle_2_value', parseFloat(e.target.value) || 0)}
                className="bg-slate-700 border-slate-600"
              />
            </div>
          </div>
        );

      case 9: // Review
        const totalIncome = (formData.financials?.social_security || 0) + 
          (formData.financials?.pension || 0) + 
          (formData.financials?.va_pension || 0) + 
          (formData.financials?.other_income || 0);
        
        const countableAssets = (formData.financials?.checking || 0) +
          (formData.financials?.savings || 0) +
          (formData.financials?.cds || 0) +
          (formData.financials?.money_market || 0) +
          (formData.financials?.ira || 0) +
          (formData.financials?.four01k || 0) +
          (formData.financials?.brokerage || 0) +
          (formData.financials?.annuities || 0);

        return (
          <div className="space-y-4">
            <div className="bg-slate-700 p-4 rounded-lg">
              <h3 className="font-medium text-emerald-400 mb-2">Patient Information</h3>
              <p>{formData.first_name} {formData.last_name}</p>
              <p className="text-sm text-slate-400">{formData.city}, FL {formData.zip_code}</p>
              <p className="text-sm text-slate-400">{formData.county} County</p>
            </div>
            <div className="bg-slate-700 p-4 rounded-lg">
              <h3 className="font-medium text-emerald-400 mb-2">Care Needs</h3>
              <p>Level: {formData.care_level_needed}</p>
              <p className="text-sm text-slate-400">Current: {formData.current_location}</p>
            </div>
            <div className="bg-slate-700 p-4 rounded-lg">
              <h3 className="font-medium text-emerald-400 mb-2">Financial Summary</h3>
              <div className="flex justify-between">
                <span>Monthly Income:</span>
                <span>${totalIncome.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span>Countable Assets:</span>
                <span>${countableAssets.toLocaleString()}</span>
              </div>
              <div className="flex justify-between text-sm text-slate-400">
                <span>Medicaid Limit:</span>
                <span>$2,000</span>
              </div>
            </div>
            {(formData.veteran_status?.is_veteran || formData.veteran_status?.is_spouse_of_veteran) && (
              <div className="bg-slate-700 p-4 rounded-lg">
                <h3 className="font-medium text-emerald-400 mb-2">Veteran Status</h3>
                <p>{formData.veteran_status?.is_veteran ? 'Veteran' : 'Spouse of Veteran'}</p>
                {formData.veteran_status?.wartime_service && (
                  <p className="text-sm text-emerald-400">Wartime service - may qualify for VA A&A</p>
                )}
              </div>
            )}
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <Card className="w-full max-w-2xl bg-slate-800 border-slate-700 max-h-[90vh] overflow-hidden flex flex-col">
        <CardHeader className="flex-shrink-0">
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-emerald-400">Patient Intake</CardTitle>
              <CardDescription className="text-slate-400">
                Step {step + 1} of {STEPS.length}: {STEPS[step]}
              </CardDescription>
            </div>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="w-4 h-4" />
            </Button>
          </div>
          <Progress value={((step + 1) / STEPS.length) * 100} className="mt-4" />
        </CardHeader>
        <CardContent className="flex-1 overflow-y-auto">
          {renderStep()}
        </CardContent>
        <div className="flex justify-between p-6 border-t border-slate-700 flex-shrink-0">
                    <Button
                      variant="outline"
                      onClick={() => setStep((s) => s - 1)}
                      disabled={step === 0}
                      className="border-slate-600 text-white hover:text-white hover:bg-slate-700"
                    >
                      <ChevronLeft className="w-4 h-4 mr-2" />
                      Back
                    </Button>
          {step < STEPS.length - 1 ? (
            <Button onClick={() => setStep((s) => s + 1)} className="bg-emerald-600 hover:bg-emerald-700">
              Next
              <ChevronRight className="w-4 h-4 ml-2" />
            </Button>
          ) : (
            <Button onClick={handleSubmit} disabled={isSubmitting} className="bg-emerald-600 hover:bg-emerald-700">
              {isSubmitting ? 'Creating...' : 'Create Patient'}
            </Button>
          )}
        </div>
      </Card>
    </div>
  );
}
