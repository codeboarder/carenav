/**
 * Income Phases Timeline Card (Ticket 4)
 * Shows 3-phase income progression
 */
import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { TrendingUp, Clock, CheckCircle2, Loader2 } from 'lucide-react';
import { incomePhasesApi, type IncomePhase } from '@/lib/api';

interface IncomePhasesCardProps {
  patientId: number;
}

export default function IncomePhasesCard({ patientId }: IncomePhasesCardProps) {
  const [phases, setPhases] = useState<IncomePhase[]>([]);
  const [timeline, setTimeline] = useState<{
    current_income: number;
    projected_income: number;
    total_phases: number;
  } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPhases();
  }, [patientId]);

  const loadPhases = async () => {
    try {
      const data = await incomePhasesApi.getTimeline(patientId);
      setPhases(data.phases);
      setTimeline({
        current_income: data.current_income,
        projected_income: data.projected_income,
        total_phases: data.total_phases,
      });
    } catch (error) {
      console.error('Failed to load income phases:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'current':
      case 'active':
        return <CheckCircle2 className="w-4 h-4 text-emerald-400" />;
      case 'submitted':
        return <Loader2 className="w-4 h-4 text-amber-400 animate-spin" />;
      case 'preparing':
        return <Clock className="w-4 h-4 text-blue-400" />;
      default:
        return <Clock className="w-4 h-4 text-slate-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'current':
      case 'active':
        return 'bg-emerald-600';
      case 'submitted':
        return 'bg-amber-600';
      case 'preparing':
        return 'bg-blue-600';
      default:
        return 'bg-slate-600';
    }
  };

  if (loading) {
    return (
      <Card className="glass-card-hover">
        <CardHeader>
          <CardTitle className="text-teal-400">Income Timeline</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-slate-400">Loading...</p>
        </CardContent>
      </Card>
    );
  }

  const incomeGrowth = timeline ? 
    ((timeline.projected_income - timeline.current_income) / timeline.current_income * 100).toFixed(0) : 0;

  return (
    <Card className="glass-card-hover">
      <CardHeader>
        <CardTitle className="text-teal-400 flex items-center gap-2">
          <TrendingUp className="w-5 h-5" />
          Income Timeline
        </CardTitle>
        <CardDescription className="text-slate-400">
          {timeline?.total_phases || 0} phases tracked
        </CardDescription>
      </CardHeader>
      <CardContent>
        {/* Summary */}
        <div className="flex items-center justify-between mb-4 p-3 bg-slate-700/50 rounded-lg">
          <div>
            <p className="text-sm text-slate-400">Current</p>
            <p className="text-xl font-bold text-white">${timeline?.current_income?.toLocaleString() || 0}/mo</p>
          </div>
          <div className="text-center">
            <TrendingUp className="w-6 h-6 text-emerald-400 mx-auto" />
            <p className="text-sm text-emerald-400">+{incomeGrowth}%</p>
          </div>
          <div className="text-right">
            <p className="text-sm text-slate-400">Projected</p>
            <p className="text-xl font-bold text-emerald-400">${timeline?.projected_income?.toLocaleString() || 0}/mo</p>
          </div>
        </div>

        {/* Phases Timeline */}
        <div className="space-y-4">
          {phases.map((phase, index) => {
            const progressPercent = phase.status === 'current' || phase.status === 'active' ? 100 :
              phase.status === 'submitted' ? 60 :
              phase.status === 'preparing' ? 30 : 0;
            
            return (
              <div key={phase.id} className="relative">
                {/* Timeline connector */}
                {index < phases.length - 1 && (
                  <div className="absolute left-[11px] top-8 w-0.5 h-8 bg-slate-600" />
                )}
                
                <div className="flex items-start gap-3">
                  <div className="mt-1">
                    {getStatusIcon(phase.status)}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-white">{phase.phase_name}</span>
                      <span className="font-bold text-teal-400">${phase.monthly_amount.toLocaleString()}/mo</span>
                    </div>
                    <div className="flex items-center gap-2 mt-1">
                      <Badge className={getStatusColor(phase.status)} variant="secondary">
                        {phase.status}
                      </Badge>
                      {phase.estimated_start && (
                        <span className="text-xs text-slate-400">{phase.estimated_start}</span>
                      )}
                    </div>
                    {phase.source && (
                      <p className="text-xs text-slate-400 mt-1">{phase.source}</p>
                    )}
                    <Progress value={progressPercent} className="h-1 mt-2" />
                  </div>
                </div>
              </div>
            );
          })}
          {phases.length === 0 && (
            <p className="text-center text-slate-400 py-4">No income phases tracked yet</p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
