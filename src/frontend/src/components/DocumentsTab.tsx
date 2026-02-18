import { useState, useEffect } from 'react';
import { Card, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { FileText, AlertTriangle, CheckCircle2, DollarSign, Heart, Shield, Home, User, Calendar, Eye } from 'lucide-react';
import { documentsApi, type Document } from '@/lib/api';

// Generate realistic dates based on document type
const getDocumentDate = (doc: Document): string => {
  const docType = doc.doc_type || '';
  const name = doc.name?.toLowerCase() || '';
  
  // Bank statements - monthly dates going back
  if (name.includes('january 2025')) return 'Jan 31, 2025';
  if (name.includes('february 2025')) return 'Feb 28, 2025';
  if (name.includes('march 2025')) return 'Mar 31, 2025';
  if (name.includes('april 2025')) return 'Apr 30, 2025';
  if (name.includes('may 2025')) return 'May 31, 2025';
  if (name.includes('june 2025')) return 'Jun 30, 2025';
  if (name.includes('july 2025')) return 'Jul 31, 2025';
  if (name.includes('august 2025')) return 'Aug 31, 2025';
  if (name.includes('september 2025')) return 'Sep 30, 2025';
  if (name.includes('october 2025')) return 'Oct 31, 2025';
  if (name.includes('november 2025')) return 'Nov 30, 2025';
  if (name.includes('december 2025')) return 'Dec 31, 2025';
  if (name.includes('january 2024')) return 'Jan 31, 2024';
  if (name.includes('december 2024')) return 'Dec 31, 2024';
  
  // Medical records by year
  if (name.includes('2023') || docType.includes('2023')) return 'Dec 15, 2023';
  if (name.includes('2024') || docType.includes('2024')) return 'Aug 20, 2024';
  if (name.includes('2025') || docType.includes('2025')) return 'Jan 10, 2025';
  if (name.includes('2026') || docType.includes('2026')) return 'Jan 28, 2026';
  
  // Specific document types
  if (docType === 'dd214') return 'Mar 15, 1970';
  if (docType === 'death_certificate') return 'Mar 18, 2020';
  if (docType === 'marriage_certificate') return 'Jun 14, 1964';
  if (docType === 'birth_certificate') return 'Sep 3, 1942';
  if (docType === 'state_id') return 'Nov 22, 2023';
  if (docType === 'poa_healthcare' || docType === 'poa_financial') return 'Oct 5, 2024';
  if (docType === 'advance_directive') return 'Oct 5, 2024';
  if (docType === 'hipaa_authorization') return 'Oct 5, 2024';
  if (docType === 'discharge_summary') return 'Jan 28, 2026';
  if (docType === 'nursing_assessment') return 'Jan 29, 2026';
  if (docType === 'pt_evaluation') return 'Jan 30, 2026';
  if (docType === 'ot_evaluation') return 'Jan 30, 2026';
  if (docType === 'va_form_21_2680') return 'Jan 31, 2026';
  if (docType === 'ssa_statement') return 'Jan 2026';
  if (docType === 'asset_inventory') return 'Feb 1, 2026';
  
  // AI analysis reports - recent
  if (doc.category === 'ai_analysis') return 'Feb 4, 2026';
  
  // Default to recent date
  return 'Feb 2026';
};

interface DocumentsTabProps {
  patientId: number;
  patientName: string;
}

const getCategoryIcon = (category: string | null) => {
  switch (category) {
    case 'bank':
    case 'financial':
      return <DollarSign className="w-5 h-5 text-emerald-400" />;
    case 'medical':
      return <Heart className="w-5 h-5 text-red-400" />;
    case 'veteran':
      return <Shield className="w-5 h-5 text-blue-400" />;
    case 'legal':
      return <FileText className="w-5 h-5 text-purple-400" />;
    case 'property':
      return <Home className="w-5 h-5 text-amber-400" />;
    case 'identity':
    case 'income':
      return <User className="w-5 h-5 text-cyan-400" />;
    case 'ai_analysis':
      return <AlertTriangle className="w-5 h-5 text-teal-400" />;
    case 'insurance':
      return <Shield className="w-5 h-5 text-indigo-400" />;
    default:
      return <FileText className="w-5 h-5 text-slate-400" />;
  }
};

const getCategoryColor = (category: string | null) => {
  switch (category) {
    case 'bank':
    case 'financial':
      return 'border-emerald-500/30';
    case 'medical':
      return 'border-red-500/30';
    case 'veteran':
      return 'border-blue-500/30';
    case 'legal':
      return 'border-purple-500/30';
    case 'ai_analysis':
      return 'border-teal-500/30';
    case 'insurance':
      return 'border-indigo-500/30';
    default:
      return 'border-slate-500/30';
  }
};

const formatContent = (content: string | null) => {
  if (!content) return null;
  return content.split('\n').map((line, i) => {
    if (line.startsWith('===') || line.startsWith('---')) {
      return <Separator key={i} className="my-2 bg-slate-600" />;
    }
    if (line.startsWith('**') && line.endsWith('**')) {
      return <p key={i} className="font-semibold text-teal-400 mt-3 mb-1">{line.replace(/\*\*/g, '')}</p>;
    }
    if (line.startsWith('- ') || line.startsWith('• ')) {
      return <li key={i} className="ml-4 text-slate-300">{line.substring(2)}</li>;
    }
    if (line.trim() === '') {
      return <br key={i} />;
    }
    return <p key={i} className="text-slate-300 leading-relaxed">{line}</p>;
  });
};

export default function DocumentsTab({ patientId, patientName }: DocumentsTabProps) {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedDoc, setSelectedDoc] = useState<Document | null>(null);

  useEffect(() => {
    loadDocuments();
  }, [patientId]);

  const loadDocuments = async () => {
    try {
      setLoading(true);
      setError(null);
      const docs = await documentsApi.list(patientId);
      setDocuments(docs);
    } catch (err) {
      console.error('Failed to load documents:', err);
      setError('Failed to load documents. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const groupedDocs = documents.reduce((acc, doc) => {
    const category = doc.category || 'other';
    if (!acc[category]) {
      acc[category] = [];
    }
    acc[category].push(doc);
    return acc;
  }, {} as Record<string, Document[]>);

  const categoryOrder = ['ai_analysis', 'medical', 'bank', 'financial', 'identity', 'income', 'veteran', 'legal', 'insurance', 'property', 'other'];
  const sortedCategories = Object.keys(groupedDocs).sort((a, b) => {
    return categoryOrder.indexOf(a) - categoryOrder.indexOf(b);
  });

  const categoryLabels: Record<string, string> = {
    ai_analysis: 'AI Analysis Reports',
    medical: 'Medical Records',
    bank: 'Bank Statements',
    financial: 'Financial Documents',
    identity: 'Identity Documents',
    income: 'Income Documents',
    veteran: 'Veteran Documents',
    legal: 'Legal Documents',
    insurance: 'Insurance Documents',
    property: 'Property Documents',
    other: 'Other Documents',
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-slate-400">Loading documents...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-red-400">{error}</div>
      </div>
    );
  }

  if (documents.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64 space-y-4">
        <FileText className="w-16 h-16 text-slate-500" />
        <p className="text-slate-400">No documents found for {patientName}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-teal-400">Documents for {patientName}</h2>
          <p className="text-slate-400 text-sm">{documents.length} documents available</p>
        </div>
        <Badge className="bg-teal-600">{documents.length} Total</Badge>
      </div>

      {sortedCategories.map(category => (
        <div key={category} className="space-y-4">
          <div className="flex items-center gap-2">
            {getCategoryIcon(category)}
            <h3 className="text-lg font-medium text-slate-200">{categoryLabels[category] || category}</h3>
            <Badge variant="outline" className="text-slate-400 border-slate-600">
              {groupedDocs[category].length}
            </Badge>
          </div>

          <div className="grid gap-3">
            {groupedDocs[category].map(doc => (
              <Card 
                key={doc.id} 
                className={`glass-card-hover cursor-pointer ${getCategoryColor(doc.category)} transition-all hover:scale-[1.01]`}
                onClick={() => setSelectedDoc(doc)}
              >
                <CardHeader className="py-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      {getCategoryIcon(doc.category)}
                      <div>
                        <CardTitle className="text-teal-400 text-base">{doc.name}</CardTitle>
                        <CardDescription className="text-slate-400 text-sm">
                          {doc.doc_type?.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        </CardDescription>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="flex items-center gap-1 text-slate-400 text-sm">
                        <Calendar className="w-4 h-4" />
                        <span>{getDocumentDate(doc)}</span>
                      </div>
                      <button className="flex items-center gap-1 px-2 py-1 rounded bg-blue-600/30 hover:bg-blue-600/50 text-blue-300 text-sm transition-colors">
                        <Eye className="w-4 h-4" />
                        View
                      </button>
                    </div>
                  </div>
                </CardHeader>
              </Card>
            ))}
          </div>
        </div>
      ))}

      {/* Document Detail Modal */}
      <Dialog open={selectedDoc !== null} onOpenChange={() => setSelectedDoc(null)}>
        <DialogContent className="max-w-4xl max-h-[90vh] bg-slate-800 border-slate-600 text-white overflow-hidden">
          {selectedDoc && (
            <>
              <DialogHeader className="border-b border-slate-600 pb-4">
                <div className="flex items-center gap-3">
                  {getCategoryIcon(selectedDoc.category)}
                  <div>
                    <DialogTitle className="text-xl text-teal-400">{selectedDoc.name}</DialogTitle>
                    <div className="flex items-center gap-4 mt-1 text-sm text-slate-400">
                      <span>{selectedDoc.doc_type?.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</span>
                      <span className="flex items-center gap-1">
                        <Calendar className="w-4 h-4" />
                        {getDocumentDate(selectedDoc)}
                      </span>
                    </div>
                  </div>
                </div>
              </DialogHeader>
              
              <ScrollArea className="max-h-[70vh] pr-4">
                <div className="space-y-4 py-4">
                  {/* Document Content */}
                  {selectedDoc.content && (
                    <div className="p-4 bg-slate-700/50 rounded-lg border border-slate-600">
                      <h4 className="font-semibold text-teal-400 mb-3 text-lg">Document Content</h4>
                      <div className="text-sm space-y-1">
                        {formatContent(selectedDoc.content)}
                      </div>
                    </div>
                  )}

                  {/* Extracted Data */}
                  {selectedDoc.extracted_data && Object.keys(selectedDoc.extracted_data).length > 0 && (
                    <div className="p-4 bg-slate-700/50 rounded-lg border border-slate-600">
                      <h4 className="font-semibold text-teal-400 mb-3 text-lg">Extracted Data</h4>
                      <div className="grid grid-cols-2 gap-3 text-sm">
                        {Object.entries(selectedDoc.extracted_data).map(([key, value]) => (
                          <div key={key} className="flex justify-between p-2 bg-slate-800/50 rounded">
                            <span className="text-slate-400">{key.replace(/_/g, ' ')}:</span>
                            <span className="text-slate-200 font-medium">
                              {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* AI Analysis */}
                  {selectedDoc.ai_analysis && (
                    <div className="p-4 bg-teal-900/30 border border-teal-700 rounded-lg">
                      <div className="flex items-center gap-2 mb-3">
                        <CheckCircle2 className="w-5 h-5 text-teal-400" />
                        <h4 className="font-semibold text-teal-400 text-lg">AI Analysis</h4>
                      </div>
                      <p className="text-sm text-slate-300 leading-relaxed">{selectedDoc.ai_analysis}</p>
                    </div>
                  )}
                </div>
              </ScrollArea>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
