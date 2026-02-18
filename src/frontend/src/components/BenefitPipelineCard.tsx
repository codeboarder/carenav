/**
 * Benefit Application Pipeline Card (Ticket 5)
 * Shows benefit applications in pipeline stages
 */
import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Phone, FileText, Clock, CheckCircle2, Loader2, Search, AlertTriangle } from 'lucide-react';
import { benefitApplicationsApi, type BenefitApplication } from '@/lib/api';

interface BenefitPipelineCardProps {
  patientId: number;
}

const PIPELINE_STAGES = [
  { key: 'researching', label: 'Researching', icon: Search, color: 'bg-slate-600' },
  { key: 'preparing', label: 'Preparing', icon: FileText, color: 'bg-blue-600' },
  { key: 'submitted', label: 'Submitted', icon: Clock, color: 'bg-amber-600' },
  { key: 'processing', label: 'Processing', icon: Loader2, color: 'bg-purple-600' },
  { key: 'approved', label: 'Approved', icon: CheckCircle2, color: 'bg-emerald-600' },
];

export default function BenefitPipelineCard({ patientId }: BenefitPipelineCardProps) {
  const [pipeline, setPipeline] = useState<Record<string, BenefitApplication[]>>({});
  const [totalPotential, setTotalPotential] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPipeline();
  }, [patientId]);

  const loadPipeline = async () => {
    try {
      const data = await benefitApplicationsApi.getPipeline(patientId);
      setPipeline(data.pipeline);
      setTotalPotential(data.total_potential_monthly);
    } catch (error) {
      console.error('Failed to load benefit pipeline:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Card className="glass-card-hover">
        <CardHeader>
          <CardTitle className="text-teal-400">Benefits Pipeline</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-slate-400">Loading...</p>
        </CardContent>
      </Card>
    );
  }

  const totalApps = Object.values(pipeline).flat().length;

  return (
    <Card className="glass-card-hover">
      <CardHeader>
        <CardTitle className="text-teal-400 flex items-center gap-2">
          <FileText className="w-5 h-5" />
          Benefits Pipeline
        </CardTitle>
        <CardDescription className="text-slate-400">
          {totalApps} applications | Potential: ${totalPotential.toLocaleString()}/mo
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-80">
          <div className="space-y-4">
            {PIPELINE_STAGES.map(stage => {
              const apps = pipeline[stage.key] || [];
              if (apps.length === 0) return null;
              
              const StageIcon = stage.icon;
              
              return (
                <div key={stage.key}>
                  <div className="flex items-center gap-2 mb-2">
                    <StageIcon className={`w-4 h-4 ${stage.key === 'processing' ? 'animate-spin' : ''}`} />
                    <span className="font-medium text-white">{stage.label}</span>
                    <Badge className={stage.color}>{apps.length}</Badge>
                  </div>
                  
                  <div className="space-y-2 ml-6">
                    {apps.map(app => (
                      <div 
                        key={app.id}
                        className="p-3 bg-slate-700/50 rounded-lg border border-slate-600"
                      >
                        <div className="flex items-start justify-between">
                          <div>
                            <p className="font-medium text-white">
                              {app.display_name || app.benefit_type}
                            </p>
                            {app.monthly_amount && (
                              <p className="text-sm text-emerald-400">
                                ${app.monthly_amount.toLocaleString()}/mo potential
                              </p>
                            )}
                          </div>
                          {app.expected_weeks && stage.key === 'submitted' && (
                            <Badge variant="outline" className="border-slate-500 text-slate-300">
                              ~{app.expected_weeks} weeks
                            </Badge>
                          )}
                        </div>
                        
                        {app.missing_documents && (
                          <div className="mt-2 flex items-start gap-2 text-amber-400 text-sm">
                            <AlertTriangle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                            <span>Missing: {app.missing_documents}</span>
                          </div>
                        )}
                        
                        {app.contact_phone && (
                          <Button 
                            variant="ghost" 
                            size="sm" 
                            className="mt-2 text-teal-400 hover:text-teal-300 p-0 h-auto"
                            onClick={() => window.open(`tel:${app.contact_phone}`)}
                          >
                            <Phone className="w-3 h-3 mr-1" />
                            {app.contact_phone}
                          </Button>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
            
            {totalApps === 0 && (
              <p className="text-center text-slate-400 py-4">No benefit applications tracked yet</p>
            )}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
