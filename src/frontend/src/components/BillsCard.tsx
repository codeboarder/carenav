/**
 * Bills Dashboard Card (Ticket 3)
 * Shows bills due summary with tap-to-call
 */
import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Phone, AlertTriangle, Calendar, DollarSign } from 'lucide-react';
import { billsApi, type Bill } from '@/lib/api';

interface BillsCardProps {
  patientId: number;
}

export default function BillsCard({ patientId }: BillsCardProps) {
  const [bills, setBills] = useState<Bill[]>([]);
  const [summary, setSummary] = useState<{
    total_due: number;
    next_due_date: string | null;
    overdue_count: number;
    total_bills: number;
  } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadBills();
  }, [patientId]);

  const loadBills = async () => {
    try {
      const data = await billsApi.getSummary(patientId);
      setBills(data.bills);
      setSummary({
        total_due: data.total_due,
        next_due_date: data.next_due_date,
        overdue_count: data.overdue_count,
        total_bills: data.total_bills,
      });
    } catch (error) {
      console.error('Failed to load bills:', error);
    } finally {
      setLoading(false);
    }
  };

  const getCategoryColor = (category: string | null) => {
    switch (category) {
      case 'facility': return 'bg-purple-600';
      case 'funeral': return 'bg-slate-600';
      case 'utility': return 'bg-blue-600';
      case 'medical': return 'bg-red-600';
      case 'lot_rent': return 'bg-amber-600';
      default: return 'bg-slate-500';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'paid': return 'bg-emerald-600';
      case 'partial': return 'bg-amber-600';
      case 'overdue': return 'bg-red-600';
      default: return 'bg-slate-500';
    }
  };

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return 'No date';
    return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const getDaysUntilDue = (dateStr: string | null) => {
    if (!dateStr) return null;
    const due = new Date(dateStr);
    const today = new Date();
    const diff = Math.ceil((due.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
    return diff;
  };

  if (loading) {
    return (
      <Card className="glass-card-hover">
        <CardHeader>
          <CardTitle className="text-teal-400">Bills Due</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-slate-400">Loading...</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="glass-card-hover">
      <CardHeader>
        <CardTitle className="text-teal-400 flex items-center gap-2">
          <DollarSign className="w-5 h-5" />
          Bills Due
        </CardTitle>
        <CardDescription className="text-slate-400">
          {summary?.total_bills || 0} bills tracked
        </CardDescription>
      </CardHeader>
      <CardContent>
        {/* Summary Stats */}
        <div className="grid grid-cols-3 gap-4 mb-4">
          <div className="text-center p-2 bg-slate-700/50 rounded-lg">
            <p className="text-2xl font-bold text-white">${summary?.total_due?.toLocaleString() || 0}</p>
            <p className="text-xs text-slate-400">Total Due</p>
          </div>
          <div className="text-center p-2 bg-slate-700/50 rounded-lg">
            <p className="text-2xl font-bold text-white">{formatDate(summary?.next_due_date || null)}</p>
            <p className="text-xs text-slate-400">Next Due</p>
          </div>
          <div className="text-center p-2 bg-slate-700/50 rounded-lg">
            <p className={`text-2xl font-bold ${(summary?.overdue_count || 0) > 0 ? 'text-red-400' : 'text-emerald-400'}`}>
              {summary?.overdue_count || 0}
            </p>
            <p className="text-xs text-slate-400">Overdue</p>
          </div>
        </div>

        {/* Bills List */}
        <ScrollArea className="h-64">
          <div className="space-y-2">
            {bills.map(bill => {
              const daysUntil = getDaysUntilDue(bill.due_date);
              const isOverdue = daysUntil !== null && daysUntil < 0;
              const isDueSoon = daysUntil !== null && daysUntil <= 7 && daysUntil >= 0;
              
              return (
                <div 
                  key={bill.id} 
                  className={`p-3 rounded-lg border ${
                    isOverdue ? 'bg-red-900/20 border-red-600/50' : 
                    isDueSoon ? 'bg-amber-900/20 border-amber-600/50' : 
                    'bg-slate-700/50 border-slate-600'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-white">{bill.vendor}</span>
                        <Badge className={getCategoryColor(bill.category)} variant="secondary">
                          {bill.category || 'other'}
                        </Badge>
                      </div>
                      <div className="flex items-center gap-2 mt-1 text-sm text-slate-400">
                        <Calendar className="w-3 h-3" />
                        <span>Due {formatDate(bill.due_date)}</span>
                        {isOverdue && (
                          <span className="text-red-400 flex items-center gap-1">
                            <AlertTriangle className="w-3 h-3" />
                            {Math.abs(daysUntil!)} days overdue
                          </span>
                        )}
                        {isDueSoon && !isOverdue && (
                          <span className="text-amber-400">
                            {daysUntil === 0 ? 'Due today!' : `${daysUntil} days left`}
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-bold text-white">${bill.amount.toLocaleString()}</p>
                      <Badge className={getStatusColor(bill.status)} variant="secondary">
                        {bill.status}
                      </Badge>
                    </div>
                  </div>
                  {bill.contact_phone && (
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      className="mt-2 text-teal-400 hover:text-teal-300"
                      onClick={() => window.open(`tel:${bill.contact_phone}`)}
                    >
                      <Phone className="w-3 h-3 mr-1" />
                      {bill.contact_name || bill.contact_phone}
                    </Button>
                  )}
                </div>
              );
            })}
            {bills.length === 0 && (
              <p className="text-center text-slate-400 py-4">No bills tracked yet</p>
            )}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
