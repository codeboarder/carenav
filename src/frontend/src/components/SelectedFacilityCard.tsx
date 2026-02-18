/**
 * Selected Facility Card - Detailed view of the chosen facility (like Barr. tab)
 */
import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Building, Phone, MapPin, Calendar, DollarSign, User, FileText } from 'lucide-react';
import { selectedFacilityApi, SelectedFacility } from '@/lib/api';

interface SelectedFacilityCardProps {
  patientId: number;
}

export function SelectedFacilityCard({ patientId }: SelectedFacilityCardProps) {
  const [facility, setFacility] = useState<SelectedFacility | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await selectedFacilityApi.get(patientId);
        setFacility(data);
      } catch (error) {
        console.error('Failed to fetch selected facility:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [patientId]);

  const handleCall = (phone: string) => {
    window.open(`tel:${phone}`, '_self');
  };

  const formatCurrency = (amount: number | null) => {
    if (!amount) return 'N/A';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return 'TBD';
    return new Date(dateStr).toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
    });
  };

  const formatDateTime = (dateStr: string | null) => {
    if (!dateStr) return 'TBD';
    return new Date(dateStr).toLocaleString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
    });
  };

  if (loading) {
    return (
      <Card className="bg-white/5 border-white/10">
        <CardHeader>
          <CardTitle className="text-lg text-white flex items-center gap-2">
            <Building className="h-5 w-5 text-teal-400" />
            Selected Facility
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-white/60 text-sm">Loading...</p>
        </CardContent>
      </Card>
    );
  }

  if (!facility) {
    return (
      <Card className="bg-white/5 border-white/10">
        <CardHeader>
          <CardTitle className="text-lg text-white flex items-center gap-2">
            <Building className="h-5 w-5 text-teal-400" />
            Selected Facility
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-white/60 text-sm">No facility selected yet</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="bg-white/5 border-white/10">
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between">
          <CardTitle className="text-lg text-white flex items-center gap-2">
            <Building className="h-5 w-5 text-teal-400" />
            {facility.name}
          </CardTitle>
          <Badge 
            variant="outline" 
            className={
              facility.status === 'moved_in' 
                ? 'bg-green-500/20 text-green-300 border-green-500/30'
                : facility.status === 'confirmed'
                ? 'bg-blue-500/20 text-blue-300 border-blue-500/30'
                : 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30'
            }
          >
            {facility.status === 'moved_in' ? 'Moved In' : facility.status === 'confirmed' ? 'Confirmed' : 'Selected'}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Address & Contact */}
        <div className="p-3 rounded-lg bg-white/5 border border-white/10">
          <div className="flex items-start gap-2 mb-2">
            <MapPin className="h-4 w-4 text-white/50 mt-0.5 shrink-0" />
            <div>
              <p className="text-white">{facility.address}</p>
              {facility.apt_number && (
                <p className="text-teal-400 font-medium">Unit: {facility.apt_number}</p>
              )}
            </div>
          </div>
          <div className="flex flex-wrap gap-4 mt-3">
            {facility.phone && (
              <button
                onClick={() => handleCall(facility.phone!)}
                className="flex items-center gap-1 text-teal-400 hover:text-teal-300 text-sm"
              >
                <Phone className="h-4 w-4" />
                {facility.phone}
              </button>
            )}
            {facility.fax && (
              <span className="flex items-center gap-1 text-white/60 text-sm">
                <FileText className="h-4 w-4" />
                Fax: {facility.fax}
              </span>
            )}
          </div>
        </div>

        {/* Contacts */}
        <div className="p-3 rounded-lg bg-white/5 border border-white/10">
          <p className="text-white/50 text-xs mb-2 flex items-center gap-1">
            <User className="h-3 w-3" /> Contacts
          </p>
          <div className="grid grid-cols-2 gap-2">
            {facility.admissions_contact && (
              <div>
                <p className="text-white/50 text-xs">Admissions</p>
                <p className="text-white text-sm">{facility.admissions_contact}</p>
              </div>
            )}
            {facility.community_rep && (
              <div>
                <p className="text-white/50 text-xs">Community Rep</p>
                <p className="text-white text-sm">{facility.community_rep}</p>
              </div>
            )}
          </div>
        </div>

        {/* Key Dates */}
        <div className="p-3 rounded-lg bg-teal-500/10 border border-teal-500/20">
          <p className="text-white/50 text-xs mb-2 flex items-center gap-1">
            <Calendar className="h-3 w-3" /> Key Dates
          </p>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <p className="text-white/50 text-xs">Keys</p>
              <p className="text-white font-medium">{formatDateTime(facility.keys_date)}</p>
            </div>
            <div>
              <p className="text-white/50 text-xs">Move-In</p>
              <p className="text-white font-medium">{formatDate(facility.move_in_date)}</p>
            </div>
          </div>
        </div>

        {/* Monthly Costs */}
        <div className="p-3 rounded-lg bg-white/5 border border-white/10">
          <p className="text-white/50 text-xs mb-2 flex items-center gap-1">
            <DollarSign className="h-3 w-3" /> Monthly Cost Breakdown
          </p>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-white/70">Base Rent</span>
              <span className="text-white">{formatCurrency(facility.base_rent)}</span>
            </div>
            {facility.vet_discount_pct && facility.vet_discount_pct > 0 && (
              <div className="flex justify-between text-sm">
                <span className="text-green-400">Veteran Discount ({facility.vet_discount_pct}%)</span>
                <span className="text-green-400">
                  -{formatCurrency((facility.base_rent || 0) * (facility.vet_discount_pct / 100))}
                </span>
              </div>
            )}
            {facility.care_level && (
              <div className="flex justify-between text-sm">
                <span className="text-white/70">{facility.care_level}</span>
                <span className="text-white">{formatCurrency(facility.care_level_cost)}</span>
              </div>
            )}
            <div className="flex justify-between text-sm pt-2 border-t border-white/10">
              <span className="text-white font-medium">Total Monthly</span>
              <span className="text-teal-400 font-bold text-lg">{formatCurrency(facility.total_monthly)}</span>
            </div>
          </div>
        </div>

        {/* One-Time Fees */}
        <div className="p-3 rounded-lg bg-white/5 border border-white/10">
          <p className="text-white/50 text-xs mb-2">One-Time Fees</p>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <p className="text-white/50 text-xs">Deposit</p>
              <div className="flex items-center gap-2">
                <span className="text-white font-medium">{formatCurrency(facility.deposit_amount)}</span>
                <Badge 
                  variant="outline" 
                  className={facility.deposit_paid 
                    ? 'bg-green-500/20 text-green-300 border-green-500/30' 
                    : 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30'
                  }
                >
                  {facility.deposit_paid ? 'Paid' : 'Due'}
                </Badge>
              </div>
            </div>
            <div>
              <p className="text-white/50 text-xs">Community Fee</p>
              <span className="text-white font-medium">{formatCurrency(facility.community_fee)}</span>
            </div>
          </div>
        </div>

        {/* Notes */}
        {facility.notes && (
          <div className="p-3 rounded-lg bg-white/5 border border-white/10">
            <p className="text-white/50 text-xs mb-1">Notes</p>
            <p className="text-white/80 text-sm">{facility.notes}</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
