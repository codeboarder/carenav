/**
 * Contacts Directory Card (Ticket 6)
 * Shows contacts grouped by category with tap-to-call
 */
import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Phone, Mail, Users, Building, Briefcase, Heart, Stethoscope, Shield } from 'lucide-react';
import { contactsApi, type Contact } from '@/lib/api';

interface ContactsCardProps {
  patientId: number;
}

const CATEGORY_CONFIG: Record<string, { icon: typeof Users; color: string; label: string }> = {
  facility: { icon: Building, color: 'bg-purple-600', label: 'Facilities' },
  legal: { icon: Briefcase, color: 'bg-blue-600', label: 'Legal' },
  government: { icon: Shield, color: 'bg-slate-600', label: 'Government' },
  insurance: { icon: Shield, color: 'bg-amber-600', label: 'Insurance' },
  family: { icon: Heart, color: 'bg-red-600', label: 'Family' },
  medical: { icon: Stethoscope, color: 'bg-emerald-600', label: 'Medical' },
  other: { icon: Users, color: 'bg-slate-500', label: 'Other' },
};

export default function ContactsCard({ patientId }: ContactsCardProps) {
  const [grouped, setGrouped] = useState<Record<string, Contact[]>>({});
  const [totalContacts, setTotalContacts] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadContacts();
  }, [patientId]);

  const loadContacts = async () => {
    try {
      const data = await contactsApi.getGrouped(patientId);
      setGrouped(data.grouped);
      setTotalContacts(data.total_contacts);
    } catch (error) {
      console.error('Failed to load contacts:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Card className="glass-card-hover">
        <CardHeader>
          <CardTitle className="text-teal-400">Contacts</CardTitle>
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
          <Users className="w-5 h-5" />
          Contact Directory
        </CardTitle>
        <CardDescription className="text-slate-400">
          {totalContacts} contacts
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-80">
          <div className="space-y-4">
            {Object.entries(grouped).map(([category, contacts]) => {
              const config = CATEGORY_CONFIG[category] || CATEGORY_CONFIG.other;
              const CategoryIcon = config.icon;
              
              return (
                <div key={category}>
                  <div className="flex items-center gap-2 mb-2">
                    <CategoryIcon className="w-4 h-4 text-slate-400" />
                    <span className="font-medium text-white">{config.label}</span>
                    <Badge className={config.color}>{contacts.length}</Badge>
                  </div>
                  
                  <div className="space-y-2 ml-6">
                    {contacts.map((contact: Contact) => (
                      <div 
                        key={contact.id}
                        className="p-3 bg-slate-700/50 rounded-lg border border-slate-600"
                      >
                        <div className="flex items-start justify-between">
                          <div>
                            <p className="font-medium text-white">{contact.name}</p>
                            {contact.organization && (
                              <p className="text-sm text-slate-400">{contact.organization}</p>
                            )}
                            {contact.role && (
                              <p className="text-xs text-slate-500">{contact.role}</p>
                            )}
                          </div>
                        </div>
                        
                        <div className="flex items-center gap-2 mt-2">
                          {contact.phone && (
                            <Button 
                              variant="ghost" 
                              size="sm" 
                              className="text-teal-400 hover:text-teal-300 p-0 h-auto"
                              onClick={() => window.open(`tel:${contact.phone}`)}
                            >
                              <Phone className="w-3 h-3 mr-1" />
                              {contact.phone}
                            </Button>
                          )}
                          {contact.email && (
                            <Button 
                              variant="ghost" 
                              size="sm" 
                              className="text-blue-400 hover:text-blue-300 p-0 h-auto"
                              onClick={() => window.open(`mailto:${contact.email}`)}
                            >
                              <Mail className="w-3 h-3 mr-1" />
                              Email
                            </Button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
            
            {totalContacts === 0 && (
              <p className="text-center text-slate-400 py-4">No contacts added yet</p>
            )}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
