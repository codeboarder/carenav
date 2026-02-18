/**
 * Assets Sale Pipeline Card (Ticket 8)
 * Shows assets with sale status and title tracking
 */
import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Progress } from '@/components/ui/progress';
import { Car, Home, Wallet, Gem, Package, AlertTriangle, Lock, CheckCircle2, Truck } from 'lucide-react';
import { assetsApi, type Asset } from '@/lib/api';

interface AssetsCardProps {
  patientId: number;
}

const ASSET_TYPE_ICONS: Record<string, typeof Car> = {
  vehicle: Car,
  property: Home,
  account: Wallet,
  jewelry: Gem,
  other: Package,
};

const SALE_STATUS_CONFIG: Record<string, { label: string; color: string; progress: number }> = {
  not_for_sale: { label: 'Not for Sale', color: 'bg-slate-600', progress: 0 },
  preparing: { label: 'Preparing', color: 'bg-blue-600', progress: 25 },
  listed: { label: 'Listed', color: 'bg-amber-600', progress: 50 },
  pending_sale: { label: 'Pending Sale', color: 'bg-purple-600', progress: 75 },
  sold: { label: 'Sold', color: 'bg-emerald-600', progress: 100 },
};

const TITLE_STATUS_CONFIG: Record<string, { label: string; icon: typeof CheckCircle2; color: string }> = {
  in_hand: { label: 'In Hand', icon: CheckCircle2, color: 'text-emerald-400' },
  ordered: { label: 'Ordered', icon: Truck, color: 'text-blue-400' },
  in_transit: { label: 'In Transit', icon: Truck, color: 'text-amber-400' },
  not_needed: { label: 'N/A', icon: CheckCircle2, color: 'text-slate-400' },
};

export default function AssetsCard({ patientId }: AssetsCardProps) {
  const [pipeline, setPipeline] = useState<Record<string, Asset[]>>({});
  const [pendingTitle, setPendingTitle] = useState<Asset[]>([]);
  const [totalEstimated, setTotalEstimated] = useState(0);
  const [totalSold, setTotalSold] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAssets();
  }, [patientId]);

  const loadAssets = async () => {
    try {
      const data = await assetsApi.getPipeline(patientId);
      setPipeline(data.pipeline);
      setPendingTitle(data.pending_title);
      setTotalEstimated(data.total_estimated_value);
      setTotalSold(data.total_sold_value);
    } catch (error) {
      console.error('Failed to load assets:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Card className="glass-card-hover">
        <CardHeader>
          <CardTitle className="text-teal-400">Assets</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-slate-400">Loading...</p>
        </CardContent>
      </Card>
    );
  }

  const allAssets = Object.values(pipeline).flat();
  const totalAssets = allAssets.length;

  return (
    <Card className="glass-card-hover">
      <CardHeader>
        <CardTitle className="text-teal-400 flex items-center gap-2">
          <Package className="w-5 h-5" />
          Asset Sale Pipeline
        </CardTitle>
        <CardDescription className="text-slate-400">
          {totalAssets} assets | Est. Value: ${totalEstimated.toLocaleString()}
        </CardDescription>
      </CardHeader>
      <CardContent>
        {/* Pending Title Warning */}
        {pendingTitle.length > 0 && (
          <div className="mb-4 p-3 bg-amber-900/20 border border-amber-600/50 rounded-lg">
            <div className="flex items-center gap-2 text-amber-400">
              <AlertTriangle className="w-4 h-4" />
              <span className="font-medium">Title Pending</span>
            </div>
            <p className="text-sm text-amber-300 mt-1">
              {pendingTitle.length} asset(s) waiting for title - sale blocked until received
            </p>
            <div className="mt-2 space-y-1">
              {pendingTitle.map(asset => (
                <div key={asset.id} className="flex items-center gap-2 text-sm text-amber-200">
                  <Lock className="w-3 h-3" />
                  <span>{asset.name}</span>
                  <Badge variant="outline" className="border-amber-500 text-amber-300">
                    {asset.title_status}
                  </Badge>
                </div>
              ))}
            </div>
          </div>
        )}

        <ScrollArea className="h-64">
          <div className="space-y-3">
            {allAssets.map(asset => {
              const AssetIcon = ASSET_TYPE_ICONS[asset.asset_type || 'other'] || Package;
              const saleConfig = SALE_STATUS_CONFIG[asset.sale_status] || SALE_STATUS_CONFIG.not_for_sale;
              const titleConfig = TITLE_STATUS_CONFIG[asset.title_status] || TITLE_STATUS_CONFIG.not_needed;
              const TitleIcon = titleConfig.icon;
              const isBlocked = (asset.title_status === 'ordered' || asset.title_status === 'in_transit') && 
                               asset.sale_status !== 'not_for_sale' && asset.sale_status !== 'sold';
              
              return (
                <div 
                  key={asset.id}
                  className={`p-3 rounded-lg border ${
                    isBlocked ? 'bg-amber-900/10 border-amber-600/30' : 'bg-slate-700/50 border-slate-600'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-2">
                      <AssetIcon className="w-5 h-5 text-slate-400 mt-0.5" />
                      <div>
                        <p className="font-medium text-white">{asset.name}</p>
                        <div className="flex items-center gap-2 mt-1">
                          <Badge variant="outline" className="border-slate-500 text-slate-300">
                            {asset.owner || 'unknown'}
                          </Badge>
                          {asset.title_status !== 'not_needed' && (
                            <span className={`flex items-center gap-1 text-xs ${titleConfig.color}`}>
                              <TitleIcon className="w-3 h-3" />
                              Title: {titleConfig.label}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-bold text-white">
                        ${(asset.estimated_value || 0).toLocaleString()}
                      </p>
                      <Badge className={saleConfig.color}>
                        {saleConfig.label}
                      </Badge>
                    </div>
                  </div>
                  
                  {/* Sale Progress */}
                  {asset.sale_status !== 'not_for_sale' && (
                    <div className="mt-2">
                      <Progress value={saleConfig.progress} className="h-1" />
                      {isBlocked && (
                        <p className="text-xs text-amber-400 mt-1 flex items-center gap-1">
                          <Lock className="w-3 h-3" />
                          Sale blocked - waiting for title
                        </p>
                      )}
                    </div>
                  )}
                  
                  {/* Insurance Reminder */}
                  {asset.linked_insurance && asset.sale_status !== 'sold' && (
                    <p className="text-xs text-blue-400 mt-2">
                      Cancel after sale: {asset.linked_insurance}
                    </p>
                  )}
                </div>
              );
            })}
            
            {totalAssets === 0 && (
              <p className="text-center text-slate-400 py-4">No assets tracked yet</p>
            )}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
