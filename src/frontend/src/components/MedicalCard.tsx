/**
 * Medical Card - Displays diagnoses, medications, vitals, allergies
 */
import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Stethoscope, Pill, AlertTriangle, Heart, Phone, 
  Thermometer, Activity, User
} from 'lucide-react';
import { medicalApi, FullMedicalResponse, Diagnosis, Medication } from '@/lib/api';

interface MedicalCardProps {
  patientId: number;
  patientName?: string;
  patientDob?: string;
}

export function MedicalCard({ patientId, patientName, patientDob }: MedicalCardProps) {
  const [data, setData] = useState<FullMedicalResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await medicalApi.get(patientId);
        setData(response);
      } catch (error) {
        console.error('Failed to fetch medical info:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [patientId]);

  const handleCall = (phone: string) => {
    window.open(`tel:${phone}`, '_self');
  };

  if (loading) {
    return (
      <Card className="bg-white/5 border-white/10">
        <CardHeader>
          <CardTitle className="text-lg text-white flex items-center gap-2">
            <Stethoscope className="h-5 w-5 text-teal-400" />
            Medical Information
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-white/60 text-sm">Loading...</p>
        </CardContent>
      </Card>
    );
  }

  const info = data?.info;
  const diagnoses = data?.diagnoses || [];
  const medications = data?.medications || [];

  return (
    <Card className="bg-white/5 border-white/10">
      <CardHeader className="pb-2">
        <CardTitle className="text-lg text-white flex items-center gap-2">
          <Stethoscope className="h-5 w-5 text-teal-400" />
          Medical Information
        </CardTitle>
      </CardHeader>
      <CardContent>
        {/* Patient Header */}
        <div className="p-3 rounded-lg bg-teal-500/10 border border-teal-500/20 mb-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-white/50 text-xs">Patient</p>
              <p className="text-white font-medium">{patientName || 'N/A'}</p>
            </div>
            <div>
              <p className="text-white/50 text-xs">DOB</p>
              <p className="text-white font-medium">{patientDob || 'N/A'}</p>
            </div>
            <div>
              <p className="text-white/50 text-xs">Medicare ID</p>
              <p className="text-white font-medium">{info?.medicare_id || 'N/A'}</p>
            </div>
            <div>
              <p className="text-white/50 text-xs">Medicaid ID</p>
              <p className="text-white font-medium">{info?.medicaid_id || 'Pending'}</p>
            </div>
          </div>
        </div>

        {/* Physician */}
        {info?.physician_name && (
          <div className="p-3 rounded-lg bg-white/5 border border-white/10 mb-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <User className="h-4 w-4 text-white/50" />
                <div>
                  <p className="text-white/50 text-xs">Primary Physician</p>
                  <p className="text-white font-medium">{info.physician_name}</p>
                </div>
              </div>
              {info.physician_phone && (
                <button
                  onClick={() => handleCall(info.physician_phone!)}
                  className="flex items-center gap-1 text-teal-400 hover:text-teal-300 text-sm"
                >
                  <Phone className="h-4 w-4" />
                  {info.physician_phone}
                </button>
              )}
            </div>
          </div>
        )}

        <Tabs defaultValue="diagnoses" className="w-full">
          <TabsList className="grid w-full grid-cols-4 bg-white/5">
            <TabsTrigger value="diagnoses" className="text-white data-[state=active]:bg-teal-500">
              Diagnoses
            </TabsTrigger>
            <TabsTrigger value="medications" className="text-white data-[state=active]:bg-teal-500">
              Meds
            </TabsTrigger>
            <TabsTrigger value="vitals" className="text-white data-[state=active]:bg-teal-500">
              Vitals
            </TabsTrigger>
            <TabsTrigger value="care" className="text-white data-[state=active]:bg-teal-500">
              Care
            </TabsTrigger>
          </TabsList>

          {/* Diagnoses Tab */}
          <TabsContent value="diagnoses" className="mt-4">
            <ScrollArea className="h-[300px]">
              <div className="space-y-2">
                {diagnoses.length === 0 ? (
                  <p className="text-white/60 text-sm text-center py-4">No diagnoses recorded</p>
                ) : (
                  diagnoses.map((dx: Diagnosis) => (
                    <div
                      key={dx.id}
                      className="p-3 rounded-lg bg-white/5 border border-white/10"
                    >
                      <div className="flex items-start justify-between">
                        <div>
                          <div className="flex items-center gap-2">
                            <p className="text-white font-medium">{dx.name}</p>
                            {dx.is_primary && (
                              <Badge className="bg-red-500/20 text-red-300 border-red-500/30">
                                Primary
                              </Badge>
                            )}
                          </div>
                          {dx.icd_code && (
                            <p className="text-white/50 text-xs mt-1">ICD-10: {dx.icd_code}</p>
                          )}
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </ScrollArea>
          </TabsContent>

          {/* Medications Tab */}
          <TabsContent value="medications" className="mt-4">
            <ScrollArea className="h-[300px]">
              <div className="space-y-2">
                {medications.length === 0 ? (
                  <p className="text-white/60 text-sm text-center py-4">No medications recorded</p>
                ) : (
                  medications.map((med: Medication) => (
                    <div
                      key={med.id}
                      className="p-3 rounded-lg bg-white/5 border border-white/10"
                    >
                      <div className="flex items-start gap-2">
                        <Pill className="h-4 w-4 text-purple-400 mt-0.5 shrink-0" />
                        <div className="flex-1">
                          <p className="text-white font-medium">{med.name}</p>
                          <div className="flex flex-wrap gap-2 mt-1">
                            {med.dosage && (
                              <span className="text-white/60 text-xs">{med.dosage}</span>
                            )}
                            {med.frequency && (
                              <span className="text-white/60 text-xs">| {med.frequency}</span>
                            )}
                            {med.route && (
                              <span className="text-white/60 text-xs">| {med.route}</span>
                            )}
                          </div>
                          {med.purpose && (
                            <p className="text-teal-400 text-xs mt-1">For: {med.purpose}</p>
                          )}
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </ScrollArea>
          </TabsContent>

          {/* Vitals Tab */}
          <TabsContent value="vitals" className="mt-4">
            <div className="grid grid-cols-2 gap-3">
              <div className="p-3 rounded-lg bg-white/5 border border-white/10">
                <div className="flex items-center gap-2 mb-1">
                  <Heart className="h-4 w-4 text-red-400" />
                  <p className="text-white/50 text-xs">Blood Pressure</p>
                </div>
                <p className="text-white font-medium text-lg">{info?.blood_pressure || 'N/A'}</p>
              </div>
              <div className="p-3 rounded-lg bg-white/5 border border-white/10">
                <div className="flex items-center gap-2 mb-1">
                  <Activity className="h-4 w-4 text-pink-400" />
                  <p className="text-white/50 text-xs">Pulse</p>
                </div>
                <p className="text-white font-medium text-lg">{info?.pulse ? `${info.pulse} bpm` : 'N/A'}</p>
              </div>
              <div className="p-3 rounded-lg bg-white/5 border border-white/10">
                <div className="flex items-center gap-2 mb-1">
                  <Thermometer className="h-4 w-4 text-orange-400" />
                  <p className="text-white/50 text-xs">Temperature</p>
                </div>
                <p className="text-white font-medium text-lg">{info?.temperature ? `${info.temperature}°F` : 'N/A'}</p>
              </div>
              <div className="p-3 rounded-lg bg-white/5 border border-white/10">
                <div className="flex items-center gap-2 mb-1">
                  <Activity className="h-4 w-4 text-blue-400" />
                  <p className="text-white/50 text-xs">Respiration</p>
                </div>
                <p className="text-white font-medium text-lg">{info?.respiration ? `${info.respiration}/min` : 'N/A'}</p>
              </div>
            </div>
            {info?.vitals_date && (
              <p className="text-white/40 text-xs mt-2 text-center">
                Last updated: {new Date(info.vitals_date).toLocaleDateString()}
              </p>
            )}
          </TabsContent>

          {/* Care Tab */}
          <TabsContent value="care" className="mt-4">
            <div className="space-y-3">
              {/* Allergies */}
              <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20">
                <div className="flex items-center gap-2 mb-2">
                  <AlertTriangle className="h-4 w-4 text-red-400" />
                  <p className="text-red-300 font-medium text-sm">Allergies</p>
                </div>
                <p className="text-white">{info?.allergies || 'None documented'}</p>
              </div>

              {/* Diet */}
              <div className="p-3 rounded-lg bg-white/5 border border-white/10">
                <p className="text-white/50 text-xs mb-1">Diet</p>
                <p className="text-white font-medium">{info?.diet || 'Regular'}</p>
              </div>

              {/* Code Status */}
              <div className="p-3 rounded-lg bg-white/5 border border-white/10">
                <p className="text-white/50 text-xs mb-1">Code Status</p>
                <Badge 
                  className={
                    info?.code_status === 'FULL CODE' 
                      ? 'bg-green-500/20 text-green-300 border-green-500/30'
                      : 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30'
                  }
                >
                  {info?.code_status || 'Not specified'}
                </Badge>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}
