/**
 * Document Parse Form - Upload and parse documents with AI
 * Extracts structured data and stores in appropriate database tables
 */
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Upload, FileText, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import { documentParseApi, type ParsedDataResponse } from '@/lib/api';

interface DocumentParseFormProps {
  patientId: number;
  onDocumentParsed?: () => void;
}

export function DocumentParseForm({ patientId, onDocumentParsed }: DocumentParseFormProps) {
  const [open, setOpen] = useState(false);
  const [content, setContent] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<ParsedDataResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async () => {
    if (!content.trim()) return;
    
    setIsLoading(true);
    setError(null);
    setResult(null);
    
    try {
      const response = await documentParseApi.parse(patientId, content);
      setResult(response);
      if (response.success && onDocumentParsed) {
        onDocumentParsed();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to parse document');
    } finally {
      setIsLoading(false);
    }
  };

  const handleClose = () => {
    setOpen(false);
    setContent('');
    setResult(null);
    setError(null);
  };

  const getDocTypeColor = (docType: string) => {
    switch (docType) {
      case 'medical': return 'bg-red-500';
      case 'insurance': return 'bg-blue-500';
      case 'contact': return 'bg-green-500';
      case 'bill': return 'bg-yellow-500';
      case 'facility': return 'bg-purple-500';
      case 'win': return 'bg-teal-500';
      default: return 'bg-slate-500';
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button className="glass-button-accent text-white">
          <Upload className="w-4 h-4 mr-2" />
          Add Document
        </Button>
      </DialogTrigger>
      <DialogContent className="glass-card border-white/10 max-w-2xl">
        <DialogHeader>
          <DialogTitle className="text-teal-400 flex items-center gap-2">
            <FileText className="w-5 h-5" />
            Add Document with AI Parsing
          </DialogTitle>
        </DialogHeader>
        
        <div className="space-y-4">
          <div className="space-y-2">
            <Label className="text-slate-300">
              Paste document content (medical records, insurance cards, bills, contacts, etc.)
            </Label>
            <Textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Paste the document text here. The AI will automatically identify the document type and extract relevant data.

Examples:
- Medical records with diagnoses and medications
- Insurance card information
- Contact details for healthcare providers
- Bills and invoices
- Facility information"
              className="min-h-[200px] bg-slate-800/50 border-slate-600 text-slate-200 placeholder:text-slate-500"
              disabled={isLoading}
            />
          </div>

          {error && (
            <div className="flex items-center gap-2 p-3 bg-red-900/30 border border-red-500/50 rounded-lg">
              <AlertCircle className="w-5 h-5 text-red-400" />
              <span className="text-red-300">{error}</span>
            </div>
          )}

          {result && (
            <div className="space-y-3 p-4 bg-slate-800/50 rounded-lg border border-slate-600">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-teal-400" />
                <span className="text-teal-400 font-medium">Document Parsed Successfully</span>
              </div>
              
              <div className="flex items-center gap-2">
                <span className="text-slate-400">Document Type:</span>
                <Badge className={getDocTypeColor(result.document_type)}>
                  {result.document_type}
                </Badge>
              </div>

              {result.records_created.length > 0 && (
                <div className="space-y-2">
                  <span className="text-slate-400">Records Created:</span>
                  <ScrollArea className="h-32">
                    <div className="space-y-1">
                      {result.records_created.map((record, i) => (
                        <div key={i} className="flex items-center gap-2 text-sm">
                          <CheckCircle2 className="w-4 h-4 text-green-400" />
                          <span className="text-slate-300">{record}</span>
                        </div>
                      ))}
                    </div>
                  </ScrollArea>
                </div>
              )}

              {result.unstructured_data && (
                <div className="space-y-2">
                  <span className="text-slate-400">Stored as Unstructured Data:</span>
                  <pre className="text-xs text-slate-400 bg-slate-900/50 p-2 rounded overflow-auto max-h-32">
                    {JSON.stringify(result.unstructured_data, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          )}

          <div className="flex justify-end gap-3">
            <Button
              variant="outline"
              onClick={handleClose}
              className="glass-button text-slate-300"
            >
              {result ? 'Done' : 'Cancel'}
            </Button>
            {!result && (
              <Button
                onClick={handleSubmit}
                disabled={!content.trim() || isLoading}
                className="glass-button-accent text-white"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Parsing...
                  </>
                ) : (
                  <>
                    <Upload className="w-4 h-4 mr-2" />
                    Parse & Store
                  </>
                )}
              </Button>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
