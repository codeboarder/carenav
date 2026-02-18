// Built by Gregory Katz and Rick Weyenberg
// Code is as-is, open source

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import { Textarea } from '@/components/ui/textarea';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Progress } from '@/components/ui/progress';
import { 
  AlertTriangle, CheckCircle2, Clock, Phone, Calendar, 
  FileText, DollarSign, Building2, Scale, Heart, ChevronDown, ChevronUp,
  MapPin, ClipboardCheck, Home, Shield, Stethoscope
} from 'lucide-react';
import type { Patient, Task, EligibilityResponse } from '@/lib/api';

// Progress Roadmap Steps
const ROADMAP_STEPS = [
  { id: 1, name: 'Initial Assessment', description: 'Gather patient info, medical records, financial data', icon: ClipboardCheck, category: 'assessment' },
  { id: 2, name: 'Medical Evaluation', description: 'MMSE, ADL assessment, physician orders', icon: Stethoscope, category: 'medical' },
  { id: 3, name: 'Financial Analysis', description: 'Asset inventory, income verification, spend-down plan', icon: DollarSign, category: 'financial' },
  { id: 4, name: 'Benefit Applications', description: 'Submit Medicaid and VA applications', icon: FileText, category: 'applications' },
  { id: 5, name: 'Facility Selection', description: 'Tour facilities, compare options, secure placement', icon: Building2, category: 'facility' },
  { id: 6, name: 'Legal Documents', description: 'POA, advance directive, HIPAA authorization', icon: Scale, category: 'legal' },
  { id: 7, name: 'Admission Prep', description: 'Gather items, complete checklist, schedule move', icon: Home, category: 'admission' },
  { id: 8, name: 'Benefits Approval', description: 'Medicaid and VA approval, coverage begins', icon: Shield, category: 'approval' },
];

interface ExecutiveSummaryProps {
  patient: Patient | null;
  tasks: Task[];
  eligibility: EligibilityResponse | null;
  onTaskComplete: (taskId: number) => void;
  onTaskNoteUpdate: (taskId: number, note: string) => void;
}

export default function ExecutiveSummary({ 
  patient, 
  tasks, 
  eligibility,
  onTaskComplete,
  onTaskNoteUpdate 
}: ExecutiveSummaryProps) {
  const [expandedTasks, setExpandedTasks] = useState<Set<number>>(new Set());
  const [taskNotes, setTaskNotes] = useState<Record<number, string>>({});

  if (!patient) {
    return (
      <div className="flex items-center justify-center h-96">
        <p className="text-xl text-slate-400">Select a patient to view their executive summary</p>
      </div>
    );
  }

  const urgentTasks = tasks.filter(t => t.priority === 'urgent' && t.status !== 'completed');
  const highTasks = tasks.filter(t => t.priority === 'high' && t.status !== 'completed');
  const thisWeekTasks = tasks.filter(t => t.status !== 'completed').slice(0, 7);
  const completedTasks = tasks.filter(t => t.status === 'completed');

  const toggleTaskExpand = (taskId: number) => {
    const newExpanded = new Set(expandedTasks);
    if (newExpanded.has(taskId)) {
      newExpanded.delete(taskId);
    } else {
      newExpanded.add(taskId);
    }
    setExpandedTasks(newExpanded);
  };

  const handleNoteChange = (taskId: number, note: string) => {
    setTaskNotes({ ...taskNotes, [taskId]: note });
  };

  const saveNote = (taskId: number) => {
    onTaskNoteUpdate(taskId, taskNotes[taskId] || '');
  };

  const getPriorityIcon= (priority: string) => {
    switch (priority) {
      case 'urgent': return <AlertTriangle className="w-5 h-5 text-red-400" />;
      case 'high': return <Clock className="w-5 h-5 text-orange-400" />;
      default: return <CheckCircle2 className="w-5 h-5 text-slate-400" />;
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'legal': return <Scale className="w-4 h-4" />;
      case 'financial': return <DollarSign className="w-4 h-4" />;
      case 'facility': return <Building2 className="w-4 h-4" />;
      case 'document': return <FileText className="w-4 h-4" />;
      case 'veteran': return <Heart className="w-4 h-4" />;
      default: return <CheckCircle2 className="w-4 h-4" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Status Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Current Status Card */}
        <Card className="glass-card-hover lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-2xl text-teal-400">
              {patient.first_name}'s Care Journey
            </CardTitle>
            <CardDescription className="text-lg text-slate-300">
              Executive Summary - Updated {new Date().toLocaleDateString()}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-6">
              {/* Left Column - Patient Info */}
              <div className="space-y-4">
                <div>
                  <p className="text-slate-400 text-lg">Current Location</p>
                  <p className="text-xl font-semibold capitalize text-slate-100">{patient.current_location || 'Not specified'}</p>
                </div>
                <div>
                  <p className="text-slate-400 text-lg">Care Level Needed</p>
                  <p className="text-xl font-semibold text-slate-100">
                    {patient.care_level_needed === 'MC' ? 'Memory Care' : 
                     patient.care_level_needed === 'SNF' ? 'Skilled Nursing' : 
                     patient.care_level_needed === 'AL' ? 'Assisted Living' : 'TBD'}
                  </p>
                </div>
                <div>
                  <p className="text-slate-400 text-lg">County</p>
                  <p className="text-xl font-semibold text-slate-100">{patient.county || 'Not specified'}</p>
                </div>
              </div>
              
              {/* Right Column - Key Metrics */}
              <div className="space-y-4">
                <div className={`p-4 rounded-lg ${eligibility?.medicaid.eligible ? 'bg-emerald-500/20' : 'bg-red-500/20'}`}>
                  <p className="text-lg text-slate-300">Medicaid Status</p>
                  <p className={`text-xl font-bold ${eligibility?.medicaid.eligible ? 'text-teal-400' : 'text-red-400'}`}>
                    {eligibility?.medicaid.eligible ? 'ELIGIBLE' : `$${eligibility?.medicaid.over_by?.toLocaleString() || 0} Over Limit`}
                  </p>
                </div>
                <div className={`p-4 rounded-lg ${eligibility?.va_aa.eligible ? 'bg-emerald-500/20' : 'bg-slate-700'}`}>
                  <p className="text-lg text-slate-300">VA Benefits</p>
                  <p className={`text-xl font-bold ${eligibility?.va_aa.eligible ? 'text-teal-400' : 'text-slate-400'}`}>
                    {eligibility?.va_aa.eligible ? `$${eligibility.va_aa.monthly_benefit}/month` : 'Not Eligible'}
                  </p>
                </div>
                {eligibility?.gift_penalty.has_penalty && (
                  <div className="p-4 rounded-lg bg-amber-500/20">
                    <p className="text-lg text-slate-300">Gift Penalty</p>
                    <p className="text-xl font-bold text-amber-400">
                      {eligibility.gift_penalty.months} Month Wait
                    </p>
                  </div>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Quick Stats */}
        <Card className="glass-card-hover">
          <CardHeader>
            <CardTitle className="text-xl text-teal-400">Outstanding Items</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-red-500/20 rounded-lg">
              <div className="flex items-center gap-3">
                <AlertTriangle className="w-6 h-6 text-red-400" />
                <span className="text-lg font-medium text-slate-100">Urgent</span>
              </div>
              <span className="text-2xl font-bold text-red-400">{urgentTasks.length}</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-orange-500/20 rounded-lg">
              <div className="flex items-center gap-3">
                <Clock className="w-6 h-6 text-orange-400" />
                <span className="text-lg font-medium text-slate-100">High Priority</span>
              </div>
              <span className="text-2xl font-bold text-orange-400">{highTasks.length}</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-emerald-500/20 rounded-lg">
              <div className="flex items-center gap-3">
                <CheckCircle2 className="w-6 h-6 text-teal-400" />
                <span className="text-lg font-medium text-slate-100">Completed</span>
              </div>
              <span className="text-2xl font-bold text-teal-400">{completedTasks.length}</span>
            </div>
            <Separator className="bg-slate-700" />
            <div className="flex items-center justify-between">
              <span className="text-lg text-slate-400">Total Tasks</span>
              <span className="text-xl font-bold text-slate-100">{tasks.length}</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Progress Roadmap */}
      <Card className="glass-card-hover">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <MapPin className="w-6 h-6 text-teal-400" />
              <CardTitle className="text-xl text-teal-400">Care Journey Roadmap</CardTitle>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-slate-400">Progress:</span>
              <span className="text-2xl font-bold text-teal-400">
                {Math.round((completedTasks.length / Math.max(tasks.length, 1)) * 100)}%
              </span>
            </div>
          </div>
          <CardDescription className="text-slate-300">
            Track your progress through the care planning journey
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="mb-4">
            <Progress 
              value={(completedTasks.length / Math.max(tasks.length, 1)) * 100} 
              className="h-3 bg-slate-700"
            />
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {ROADMAP_STEPS.map((step, index) => {
              // Determine step status based on task categories (for future dynamic use)
              const _stepTasks = tasks.filter(t => t.category === step.category);
              const _completedStepTasks = _stepTasks.filter(t => t.status === 'completed');
              void _completedStepTasks; // Reserved for future dynamic status
              
              // For demo, mark first 4 steps as complete, 5th in progress
              const demoComplete = index < 4;
              const demoInProgress = index === 4;
              
              const StepIcon = step.icon;
              
              return (
                <div 
                  key={step.id}
                  className={`p-4 rounded-lg border transition-all ${
                    demoComplete 
                      ? 'bg-emerald-500/20 border-emerald-500/50' 
                      : demoInProgress
                        ? 'bg-blue-500/20 border-blue-500/50'
                        : 'bg-slate-700/50 border-slate-600'
                  }`}
                >
                  <div className="flex items-center gap-2 mb-2">
                    <div className={`p-2 rounded-full ${
                      demoComplete 
                        ? 'bg-emerald-500/30' 
                        : demoInProgress
                          ? 'bg-blue-500/30'
                          : 'bg-slate-600'
                    }`}>
                      {demoComplete ? (
                        <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                      ) : (
                        <StepIcon className={`w-5 h-5 ${demoInProgress ? 'text-blue-400' : 'text-slate-400'}`} />
                      )}
                    </div>
                    <span className={`text-sm font-medium ${
                      demoComplete 
                        ? 'text-emerald-400' 
                        : demoInProgress
                          ? 'text-blue-400'
                          : 'text-slate-400'
                    }`}>
                      Step {step.id}
                    </span>
                  </div>
                  <h4 className={`font-semibold mb-1 ${
                    demoComplete || demoInProgress ? 'text-slate-100' : 'text-slate-400'
                  }`}>
                    {step.name}
                  </h4>
                  <p className="text-xs text-slate-400">{step.description}</p>
                  {demoComplete && (
                    <Badge className="mt-2 bg-emerald-600 text-xs">Complete</Badge>
                  )}
                  {demoInProgress && (
                    <Badge className="mt-2 bg-blue-600 text-xs">In Progress</Badge>
                  )}
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Document Checklist */}
      <Card className="glass-card-hover">
        <CardHeader>
          <div className="flex items-center gap-3">
            <ClipboardCheck className="w-6 h-6 text-teal-400" />
            <CardTitle className="text-xl text-teal-400">Document Checklist</CardTitle>
          </div>
          <CardDescription className="text-slate-300">
            Required documents for Medicaid and VA applications
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[
              { name: 'Photo ID', status: 'collected', category: 'Identity' },
              { name: 'Social Security Card', status: 'collected', category: 'Identity' },
              { name: 'Birth Certificate', status: 'collected', category: 'Identity' },
              { name: 'Medicare Card', status: 'collected', category: 'Insurance' },
              { name: 'Bank Statements (24 mo)', status: 'collected', category: 'Financial' },
              { name: 'Asset Inventory', status: 'collected', category: 'Financial' },
              { name: 'DD-214 (Veteran)', status: 'collected', category: 'Veteran' },
              { name: 'Death Certificate', status: 'collected', category: 'Legal' },
              { name: 'Marriage Certificate', status: 'collected', category: 'Legal' },
              { name: 'POA - Healthcare', status: 'collected', category: 'Legal' },
              { name: 'POA - Financial', status: 'collected', category: 'Legal' },
              { name: 'Advance Directive', status: 'collected', category: 'Legal' },
              { name: 'HIPAA Authorization', status: 'collected', category: 'Legal' },
              { name: 'Hospital Discharge Summary', status: 'collected', category: 'Medical' },
              { name: 'Cognitive Assessment', status: 'collected', category: 'Medical' },
              { name: 'Physician Orders', status: 'collected', category: 'Medical' },
              { name: 'Medicaid Application', status: 'pending', category: 'Applications' },
              { name: 'VA Form 21-534EZ', status: 'pending', category: 'Applications' },
            ].map((doc, i) => (
              <div 
                key={i}
                className={`flex items-center gap-3 p-3 rounded-lg border ${
                  doc.status === 'collected' 
                    ? 'bg-emerald-500/10 border-emerald-500/30' 
                    : 'bg-amber-500/10 border-amber-500/30'
                }`}
              >
                {doc.status === 'collected' ? (
                  <CheckCircle2 className="w-5 h-5 text-emerald-400 flex-shrink-0" />
                ) : (
                  <Clock className="w-5 h-5 text-amber-400 flex-shrink-0" />
                )}
                <div className="flex-1 min-w-0">
                  <p className={`font-medium truncate ${
                    doc.status === 'collected' ? 'text-slate-100' : 'text-amber-300'
                  }`}>
                    {doc.name}
                  </p>
                  <p className="text-xs text-slate-400">{doc.category}</p>
                </div>
              </div>
            ))}
          </div>
          <div className="mt-4 flex items-center justify-between p-3 bg-slate-700/50 rounded-lg">
            <span className="text-slate-300">Documents Collected</span>
            <span className="text-xl font-bold text-teal-400">16 / 18</span>
          </div>
        </CardContent>
      </Card>

      {/* Application Status Tracker */}
      <Card className="glass-card-hover">
        <CardHeader>
          <div className="flex items-center gap-3">
            <Shield className="w-6 h-6 text-teal-400" />
            <CardTitle className="text-xl text-teal-400">Application Status Tracker</CardTitle>
          </div>
          <CardDescription className="text-slate-300">
            Track Medicaid and VA benefit application progress
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Medicaid Application */}
            <div className="p-4 rounded-lg border border-blue-500/30 bg-blue-500/10">
              <div className="flex items-center justify-between mb-4">
                <h4 className="text-lg font-semibold text-blue-400">Florida Medicaid ICP</h4>
                <Badge className="bg-blue-600">In Progress</Badge>
              </div>
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                  <span className="text-slate-300">Application Submitted</span>
                  <span className="text-xs text-slate-500 ml-auto">Feb 1, 2026</span>
                </div>
                <div className="flex items-center gap-3">
                  <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                  <span className="text-slate-300">Documents Received</span>
                  <span className="text-xs text-slate-500 ml-auto">Feb 2, 2026</span>
                </div>
                <div className="flex items-center gap-3">
                  <Clock className="w-5 h-5 text-blue-400 animate-pulse" />
                  <span className="text-blue-300">CARES Assessment Scheduled</span>
                  <span className="text-xs text-slate-500 ml-auto">Feb 10, 2026</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-5 h-5 rounded-full border-2 border-slate-500" />
                  <span className="text-slate-500">Financial Review</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-5 h-5 rounded-full border-2 border-slate-500" />
                  <span className="text-slate-500">Approval Decision</span>
                </div>
              </div>
              <div className="mt-4 pt-4 border-t border-slate-600">
                <div className="flex justify-between text-sm">
                  <span className="text-slate-400">Estimated Approval</span>
                  <span className="text-blue-400 font-medium">March 15-30, 2026</span>
                </div>
              </div>
            </div>

            {/* VA Application */}
            <div className="p-4 rounded-lg border border-purple-500/30 bg-purple-500/10">
              <div className="flex items-center justify-between mb-4">
                <h4 className="text-lg font-semibold text-purple-400">VA Survivors Pension (A&A)</h4>
                <Badge className="bg-purple-600">In Progress</Badge>
              </div>
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                  <span className="text-slate-300">Form 21-534EZ Submitted</span>
                  <span className="text-xs text-slate-500 ml-auto">Feb 1, 2026</span>
                </div>
                <div className="flex items-center gap-3">
                  <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                  <span className="text-slate-300">DD-214 Verified</span>
                  <span className="text-xs text-slate-500 ml-auto">Feb 3, 2026</span>
                </div>
                <div className="flex items-center gap-3">
                  <Clock className="w-5 h-5 text-purple-400 animate-pulse" />
                  <span className="text-purple-300">Medical Evidence Review</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-5 h-5 rounded-full border-2 border-slate-500" />
                  <span className="text-slate-500">Income Verification</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-5 h-5 rounded-full border-2 border-slate-500" />
                  <span className="text-slate-500">Benefit Award</span>
                </div>
              </div>
              <div className="mt-4 pt-4 border-t border-slate-600">
                <div className="flex justify-between text-sm">
                  <span className="text-slate-400">Estimated Approval</span>
                  <span className="text-purple-400 font-medium">April 1-15, 2026</span>
                </div>
                <div className="flex justify-between text-sm mt-1">
                  <span className="text-slate-400">Expected Benefit</span>
                  <span className="text-emerald-400 font-medium">$1,432/month</span>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* This Week's Activities */}
      <Card className="glass-card-hover">
        <CardHeader>
          <div className="flex items-center gap-3">
            <Calendar className="w-6 h-6 text-teal-400" />
            <CardTitle className="text-xl text-teal-400">This Week's Activities</CardTitle>
          </div>
          <CardDescription className="text-lg text-slate-300">
            Priority tasks to complete this week - check off and add notes
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-[400px] pr-4">
            <div className="space-y-3">
              {thisWeekTasks.map(task => (
                <div 
                  key={task.id} 
                  className={`p-4 rounded-lg border transition-all ${
                    task.status === 'completed' 
                      ? 'bg-slate-700/50 border-slate-600' 
                      : task.priority === 'urgent'
                        ? 'bg-red-500/10 border-red-500/30'
                        : task.priority === 'high'
                          ? 'bg-orange-500/10 border-orange-500/30'
                          : 'bg-slate-700 border-slate-600'
                  }`}
                >
                  <div className="flex items-start gap-4">
                    <Checkbox
                      checked={task.status === 'completed'}
                      onCheckedChange={() => onTaskComplete(task.id)}
                      className="mt-1 h-6 w-6"
                    />
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        {getPriorityIcon(task.priority)}
                        <h4 className={`text-lg font-medium ${task.status === 'completed' ? 'line-through text-slate-500' : 'text-slate-100'}`}>
                          {task.title}
                        </h4>
                        <Badge className={`${
                          task.priority === 'urgent' ? 'bg-red-500' :
                          task.priority === 'high' ? 'bg-orange-500' :
                          task.priority === 'medium' ? 'bg-yellow-500' : 'bg-slate-500'
                        }`}>
                          {task.priority}
                        </Badge>
                        {task.category && (
                          <Badge variant="outline" className="border-slate-500 flex items-center gap-1">
                            {getCategoryIcon(task.category)}
                            {task.category}
                          </Badge>
                        )}
                      </div>
                      
                      {task.description && (
                        <p className="text-slate-300 mb-3">{task.description}</p>
                      )}
                      
                      <div className="flex items-center gap-4 text-slate-400">
                        {task.phone && (
                          <a href={`tel:${task.phone}`} className="flex items-center gap-2 hover:text-teal-400 transition-colors">
                            <Phone className="w-4 h-4" />
                            <span className="text-lg">{task.phone}</span>
                          </a>
                        )}
                        {task.due_date && (
                          <span className="flex items-center gap-2">
                            <Calendar className="w-4 h-4" />
                            Due: {new Date(task.due_date).toLocaleDateString()}
                          </span>
                        )}
                      </div>
                      
                      {/* Expandable Notes Section */}
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => toggleTaskExpand(task.id)}
                        className="mt-3 text-slate-400 hover:text-teal-400"
                      >
                        {expandedTasks.has(task.id) ? (
                          <>
                            <ChevronUp className="w-4 h-4 mr-2" />
                            Hide Notes
                          </>
                        ) : (
                          <>
                            <ChevronDown className="w-4 h-4 mr-2" />
                            Add Notes
                          </>
                        )}
                      </Button>
                      
                      {expandedTasks.has(task.id) && (
                        <div className="mt-3 space-y-2">
                          <Textarea
                            placeholder="Add notes about this task (will be saved for AI context)..."
                            value={taskNotes[task.id] || ''}
                            onChange={(e) => handleNoteChange(task.id, e.target.value)}
                            className="bg-slate-900 border-slate-600 text-lg min-h-[100px]"
                          />
                          <Button 
                            size="sm" 
                            onClick={() => saveNote(task.id)}
                            className="bg-emerald-600 hover:bg-emerald-700"
                          >
                            Save Note
                          </Button>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
              
              {thisWeekTasks.length === 0 && (
                <div className="text-center py-8">
                  <CheckCircle2 className="w-12 h-12 text-teal-400 mx-auto mb-4" />
                  <p className="text-xl text-slate-400">All caught up! No pending tasks.</p>
                </div>
              )}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>

      {/* Key Contacts */}
      <Card className="glass-card-hover">
        <CardHeader>
          <div className="flex items-center gap-3">
            <Phone className="w-6 h-6 text-teal-400" />
            <CardTitle className="text-xl text-teal-400">Key Contacts</CardTitle>
          </div>
          <CardDescription className="text-lg text-slate-300">
            Important phone numbers for {patient.first_name}'s care
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[
              { name: 'VA Benefits Hotline', phone: '1-800-827-1000', category: 'veteran' },
              { name: 'Social Security Admin', phone: '1-800-772-1213', category: 'benefit' },
              { name: 'FL Medicaid Helpline', phone: '1-866-762-2237', category: 'benefit' },
              { name: 'FL Elder Helpline', phone: '1-800-963-5337', category: 'general' },
              { name: 'Medicare Helpline', phone: '1-800-633-4227', category: 'benefit' },
              { name: 'FL AHCA (Facility Info)', phone: '1-888-419-3456', category: 'facility' },
            ].map((contact, i) => (
              <a 
                key={i}
                href={`tel:${contact.phone}`}
                className="flex items-center gap-4 p-4 bg-slate-700 rounded-lg hover:bg-slate-600 transition-colors"
              >
                <div className="p-3 bg-emerald-500/20 rounded-full">
                  <Phone className="w-5 h-5 text-teal-400" />
                </div>
                <div>
                  <p className="font-medium text-lg text-slate-100">{contact.name}</p>
                  <p className="text-teal-400 text-lg">{contact.phone}</p>
                </div>
              </a>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
