// Built by Gregory Katz and Rick Weyenberg
// Code is as-is, open source

/**
 * Insurance Card - Displays all insurance policies (Medicare, Medicaid, private)
 */
import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Shield, Phone, Clock, CheckCircle2, AlertCircle } from 'lucide-react';
import { insuranceApi, Insurance } from '@/lib/api';

interface InsuranceCardProps {
  patientId: number;
}

const typeLabels: Record<string, string> = {
  medicare: 'Medicare',
  medicaid: 'Medicaid',
  supplemental: 'Supplemental',
  private: 'Private',
};

const typeColors: Record<string, string> = {
  medicare: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
  medicaid: 'bg-green-500/20 text-green-300 border-green-500/30',
  supplemental: 'bg-purple-500/20 text-purple-300 border-purple-500/30',
  private: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
};

const statusColors: Record<string, { bg: string; icon: React.ReactNode }> = {
  active: { bg: 'text-green-400', icon: <CheckCircle2 className="h-4 w-4" /> },
  pending: { bg: 'text-yellow-400', icon: <Clock className="h-4 w-4" /> },
  terminated: { bg: 'text-red-400', icon: <AlertCircle className="h-4 w-4" /> },
};

export function InsuranceCard({ patientId }: InsuranceCardProps) {
  const [policies, setPolicies] = useState<Insurance[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await insuranceApi.list(patientId);
        setPolicies(data);
      } catch (error) {
        console.error('Failed to fetch insurance:', error);
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
            <Shield className="h-5 w-5 text-teal-400" />
            Insurance Coverage
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-white/60 text-sm">Loading...</p>
        </CardContent>
      </Card>
    );
  }

  if (policies.length === 0) {
    return (
      <Card className="bg-white/5 border-white/10">
        <CardHeader>
          <CardTitle className="text-lg text-white flex items-center gap-2">
            <Shield className="h-5 w-5 text-teal-400" />
            Insurance Coverage
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-white/60 text-sm">No insurance policies recorded</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="bg-white/5 border-white/10">
      <CardHeader className="pb-2">
        <CardTitle className="text-lg text-white flex items-center gap-2">
          <Shield className="h-5 w-5 text-teal-400" />
          Insurance Coverage
          <Badge variant="outline" className="ml-auto bg-teal-500/20 text-teal-300 border-teal-500/30">
            {policies.length} policies
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[400px] pr-4">
          <div className="space-y-4">
            {policies.map((policy) => {
              const statusInfo = statusColors[policy.status] || statusColors.active;
              return (
                <div
                  key={policy.id}
                  className="p-4 rounded-lg bg-white/5 border border-white/10"
                >
                  {/* Header */}
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <Badge 
                        variant="outline" 
                        className={typeColors[policy.insurance_type || 'private']}
                      >
                        {typeLabels[policy.insurance_type || 'private'] || policy.insurance_type}
                      </Badge>
                      <span className={`flex items-center gap-1 ${statusInfo.bg}`}>
                        {statusInfo.icon}
                        <span className="text-xs capitalize">{policy.status}</span>
                      </span>
                    </div>
                  </div>

                  {/* Carrier */}
                  <p className="text-white font-medium text-lg mb-2">{policy.carrier}</p>

                  {/* Details Grid */}
                  <div className="grid grid-cols-2 gap-3 text-sm">
                    {policy.policy_number && (
                      <div>
                        <p className="text-white/50 text-xs">Policy #</p>
                        <p className="text-white font-mono">{policy.policy_number}</p>
                      </div>
                    )}
                    {policy.group_number && (
                      <div>
                        <p className="text-white/50 text-xs">Group #</p>
                        <p className="text-white font-mono">{policy.group_number}</p>
                      </div>
                    )}
                    {policy.subscriber_name && (
                      <div>
                        <p className="text-white/50 text-xs">Subscriber</p>
                        <p className="text-white">{policy.subscriber_name}</p>
                      </div>
                    )}
                    {policy.effective_date && (
                      <div>
                        <p className="text-white/50 text-xs">Effective</p>
                        <p className="text-white">{new Date(policy.effective_date).toLocaleDateString()}</p>
                      </div>
                    )}
                  </div>

                  {/* Phone */}
                  {policy.phone && (
                    <button
                      onClick={() => handleCall(policy.phone!)}
                      className="mt-3 flex items-center gap-2 text-teal-400 hover:text-teal-300 text-sm"
                    >
                      <Phone className="h-4 w-4" />
                      {policy.phone}
                    </button>
                  )}

                  {/* Notes */}
                  {policy.notes && (
                    <p className="mt-3 text-white/60 text-xs border-t border-white/10 pt-2">
                      {policy.notes}
                    </p>
                  )}
                </div>
              );
            })}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
