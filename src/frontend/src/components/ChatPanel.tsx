// Built by Gregory Katz and Rick Weyenberg
// Code is as-is, open source

import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { Send, Loader2, AlertTriangle, DollarSign, Shield, CheckCircle, Info, FileText, Building } from 'lucide-react';
import { chatApi, type ChatMessage, type ChatResponse } from '@/lib/api';

interface ChatPanelProps {
  patientId?: number;
}

interface ParsedSection {
  type: 'medicaid' | 'va' | 'action' | 'warning' | 'info' | 'facility' | 'general';
  title: string;
  content: string;
}

function parseAIResponse(message: string): ParsedSection[] {
  const sections: ParsedSection[] = [];
  const lines = message.split('\n');
  let currentSection: ParsedSection | null = null;
  let currentContent: string[] = [];

  const flushSection = () => {
    if (currentSection && currentContent.length > 0) {
      currentSection.content = currentContent.join('\n').trim();
      if (currentSection.content) {
        sections.push(currentSection);
      }
    }
    currentContent = [];
  };

  for (const line of lines) {
    const lowerLine = line.toLowerCase();
    
    if (lowerLine.includes('medicaid') && (lowerLine.includes(':') || line.startsWith('**'))) {
      flushSection();
      currentSection = { type: 'medicaid', title: 'Medicaid Status', content: '' };
      currentContent.push(line.replace(/^\*\*|\*\*$/g, '').replace(/^#+\s*/, ''));
    } else if ((lowerLine.includes('va ') || lowerLine.includes('veteran')) && (lowerLine.includes(':') || line.startsWith('**'))) {
      flushSection();
      currentSection = { type: 'va', title: 'VA Benefits', content: '' };
      currentContent.push(line.replace(/^\*\*|\*\*$/g, '').replace(/^#+\s*/, ''));
    } else if ((lowerLine.includes('important') || lowerLine.includes('warning') || lowerLine.includes('do not')) && !currentSection) {
      flushSection();
      currentSection = { type: 'warning', title: 'Important Notice', content: '' };
      currentContent.push(line.replace(/^\*\*|\*\*$/g, '').replace(/^#+\s*/, ''));
    } else if ((lowerLine.includes('action') || lowerLine.includes('next step') || lowerLine.includes('to do')) && (lowerLine.includes(':') || line.startsWith('**'))) {
      flushSection();
      currentSection = { type: 'action', title: 'Action Items', content: '' };
      currentContent.push(line.replace(/^\*\*|\*\*$/g, '').replace(/^#+\s*/, ''));
    } else if ((lowerLine.includes('facility') || lowerLine.includes('facilities')) && (lowerLine.includes(':') || line.startsWith('**'))) {
      flushSection();
      currentSection = { type: 'facility', title: 'Facility Information', content: '' };
      currentContent.push(line.replace(/^\*\*|\*\*$/g, '').replace(/^#+\s*/, ''));
    } else if (currentSection) {
      currentContent.push(line);
    } else {
      if (!currentSection) {
        currentSection = { type: 'general', title: '', content: '' };
      }
      currentContent.push(line);
    }
  }
  
  flushSection();
  
  if (sections.length === 0) {
    sections.push({ type: 'general', title: '', content: message });
  }
  
  return sections;
}

function ResponseSection({ section }: { section: ParsedSection }) {
  const getIcon = () => {
    switch (section.type) {
      case 'medicaid': return <DollarSign className="w-4 h-4" />;
      case 'va': return <Shield className="w-4 h-4" />;
      case 'action': return <CheckCircle className="w-4 h-4" />;
      case 'warning': return <AlertTriangle className="w-4 h-4" />;
      case 'facility': return <Building className="w-4 h-4" />;
      case 'info': return <Info className="w-4 h-4" />;
      default: return <FileText className="w-4 h-4" />;
    }
  };

  const getColorClass = () => {
    switch (section.type) {
      case 'medicaid': return 'ai-response-medicaid';
      case 'va': return 'ai-response-va';
      case 'action': return 'ai-response-action';
      case 'warning': return 'ai-response-warning';
      case 'facility': return 'ai-response-medicaid';
      default: return '';
    }
  };

  const getHeaderColor = () => {
    switch (section.type) {
      case 'medicaid': return 'text-[#0075FF]';
      case 'va': return 'text-[#01B574]';
      case 'action': return 'text-[#00D4FF]';
      case 'warning': return 'text-[#FFB547]';
      case 'facility': return 'text-[#0075FF]';
      default: return 'text-white';
    }
  };

  if (section.type === 'general' && !section.title) {
    return (
      <div className="text-white whitespace-pre-wrap leading-relaxed">
        {section.content}
      </div>
    );
  }

  return (
    <div className={`ai-response-section ${getColorClass()}`}>
      {section.title && (
        <div className={`ai-response-section-header ${getHeaderColor()}`}>
          {getIcon()}
          <span>{section.title}</span>
        </div>
      )}
      <div className="text-white/90 whitespace-pre-wrap text-sm leading-relaxed">
        {section.content}
      </div>
    </div>
  );
}

export default function ChatPanel({ patientId }: ChatPanelProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: 'assistant',
      content: "Hello! I'm your CareNav assistant. I can help you understand Medicaid eligibility, VA benefits, find suitable facilities, and guide you through the care planning process. What would you like to know?",
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [lastResponse, setLastResponse] = useState<ChatResponse | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: ChatMessage = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await chatApi.send(
        input,
        patientId,
        messages.filter((m) => m.role !== 'system')
      );

      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.message,
      };
      setMessages((prev) => [...prev, assistantMessage]);
      setLastResponse(response);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: "I'm sorry, I encountered an error processing your request. Please try again.",
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-full">
      <ScrollArea className="flex-1 p-4" ref={scrollRef}>
        <div className="space-y-4">
          {messages.map((message, i) => (
            <div
              key={i}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {message.role === 'user' ? (
                <div className="max-w-[85%] rounded-2xl px-4 py-3 bg-gradient-to-r from-[#0075FF] to-[#0056CC] text-white shadow-lg shadow-blue-500/20">
                  <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                </div>
              ) : (
                <div className="max-w-[90%] rounded-2xl p-4 bg-[#111C44] border border-white/10">
                  {parseAIResponse(message.content).map((section, idx) => (
                    <ResponseSection key={idx} section={section} />
                  ))}
                </div>
              )}
            </div>
          ))}

          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-slate-700 rounded-lg p-3">
                <Loader2 className="w-4 h-4 animate-spin text-emerald-400" />
              </div>
            </div>
          )}

          {lastResponse && lastResponse.warnings.length > 0 && (
            <div className="ai-response-section ai-response-warning">
              <div className="ai-response-section-header text-[#FFB547]">
                <AlertTriangle className="w-4 h-4" />
                <span>Important Notice</span>
              </div>
              {lastResponse.warnings.map((warning, i) => (
                <p key={i} className="text-sm text-white/90">{warning}</p>
              ))}
            </div>
          )}

          {lastResponse && lastResponse.action_items.length > 0 && (
            <div className="ai-response-section ai-response-action">
              <div className="ai-response-section-header text-[#00D4FF]">
                <CheckCircle className="w-4 h-4" />
                <span>Action Items</span>
              </div>
              <div className="space-y-2">
                {lastResponse.action_items.map((item, i) => (
                  <div key={i} className="flex items-center gap-2 text-sm">
                    <Badge className={
                      item.priority === 'urgent' ? 'bg-[#E31A1A]/20 text-[#E31A1A] border border-[#E31A1A]/30' :
                      item.priority === 'this_week' ? 'bg-[#FFB547]/20 text-[#FFB547] border border-[#FFB547]/30' : 'bg-[#0075FF]/20 text-[#0075FF] border border-[#0075FF]/30'
                    }>
                      {item.priority}
                    </Badge>
                    <span className="text-white">{item.action}</span>
                    {item.phone && (
                      <a href={`tel:${item.phone}`} className="text-[#00D4FF] hover:underline">
                        {item.phone}
                      </a>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {lastResponse && (
            <div className="text-xs text-[#A0AEC0] text-right mt-2">
              Confidence: {lastResponse.confidence}%
            </div>
          )}
        </div>
      </ScrollArea>

      <div className="p-4 border-t border-white/10">
        <div className="flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about Medicaid, VA benefits, facilities..."
            className="bg-[#111C44] border-white/10 text-white placeholder:text-[#A0AEC0] rounded-xl"
            disabled={isLoading}
          />
          <Button
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
            className="bg-gradient-to-r from-[#0075FF] to-[#0056CC] hover:shadow-lg hover:shadow-blue-500/30 rounded-xl px-4"
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin text-white" />
            ) : (
              <Send className="w-4 h-4 text-white" />
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}
