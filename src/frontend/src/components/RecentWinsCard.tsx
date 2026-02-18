/**
 * Recent Wins Card - Celebrates accomplishments for the caregiving family
 */
import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Trophy, DollarSign, FileText, Building, Scale } from 'lucide-react';
import { winsApi, Win } from '@/lib/api';

interface RecentWinsCardProps {
  patientId: number;
}

const categoryIcons: Record<string, React.ReactNode> = {
  financial: <DollarSign className="h-4 w-4" />,
  document: <FileText className="h-4 w-4" />,
  facility: <Building className="h-4 w-4" />,
  legal: <Scale className="h-4 w-4" />,
};

const categoryColors: Record<string, string> = {
  financial: 'bg-green-500/20 text-green-300 border-green-500/30',
  document: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
  facility: 'bg-purple-500/20 text-purple-300 border-purple-500/30',
  legal: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
};

export function RecentWinsCard({ patientId }: RecentWinsCardProps) {
  const [wins, setWins] = useState<Win[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchWins = async () => {
      try {
        const data = await winsApi.list(patientId);
        setWins(data);
      } catch (error) {
        console.error('Failed to fetch wins:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchWins();
  }, [patientId]);

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const formatAmount = (amount: number | null, type: string | null) => {
    if (!amount) return null;
    const formatted = new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0,
    }).format(amount);
    if (type === 'monthly') return `${formatted}/mo`;
    if (type === 'one_time') return formatted;
    return formatted;
  };

  if (loading) {
    return (
      <Card className="bg-white/5 border-white/10">
        <CardHeader className="pb-2">
          <CardTitle className="text-lg text-white flex items-center gap-2">
            <Trophy className="h-5 w-5 text-yellow-400" />
            Recent Wins
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-white/60 text-sm">Loading...</p>
        </CardContent>
      </Card>
    );
  }

  if (wins.length === 0) {
    return (
      <Card className="bg-white/5 border-white/10">
        <CardHeader className="pb-2">
          <CardTitle className="text-lg text-white flex items-center gap-2">
            <Trophy className="h-5 w-5 text-yellow-400" />
            Recent Wins
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-white/60 text-sm">No wins recorded yet</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="bg-gradient-to-br from-yellow-500/10 to-green-500/10 border-yellow-500/20">
      <CardHeader className="pb-2">
        <CardTitle className="text-lg text-white flex items-center gap-2">
          <Trophy className="h-5 w-5 text-yellow-400" />
          Recent Wins
          <Badge variant="outline" className="ml-auto bg-yellow-500/20 text-yellow-300 border-yellow-500/30">
            {wins.length} accomplishments
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[200px] pr-4">
          <div className="space-y-3">
            {wins.map((win) => (
              <div
                key={win.id}
                className="p-3 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition-colors"
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <div className={`p-1.5 rounded ${categoryColors[win.category || 'financial'] || 'bg-white/10'}`}>
                      {categoryIcons[win.category || 'financial'] || <Trophy className="h-4 w-4" />}
                    </div>
                    <div>
                      <p className="text-white font-medium text-sm">{win.title}</p>
                      {win.description && (
                        <p className="text-white/60 text-xs mt-0.5 line-clamp-2">{win.description}</p>
                      )}
                    </div>
                  </div>
                  <div className="text-right shrink-0">
                    {win.amount && (
                      <p className="text-green-400 font-semibold text-sm">
                        {formatAmount(win.amount, win.amount_type)}
                      </p>
                    )}
                    <p className="text-white/40 text-xs">{formatDate(win.win_date)}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
