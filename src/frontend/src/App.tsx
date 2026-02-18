// Built by Gregory Katz and Rick Weyenberg
// Code is as-is, open source

/**
 * CareNav Florida - Main Application
 * Built with Rick Weyenberg and Greg Katz collaborating
 * Copyright (c) 2026 - MIT License
 */
import { useState, useEffect } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { 
  Home, ClipboardList, DollarSign, FileText, MapPin, MessageSquare, 
  Plus, CheckCircle2, AlertTriangle, Phone, User, LayoutDashboard, Lock,
  Building, Stethoscope, Shield
} from 'lucide-react';
import IntakeWizard from './components/IntakeWizard';
import ChatPanel from './components/ChatPanel';
import ExecutiveSummary from './components/ExecutiveSummary';
import DocumentsTab from './components/DocumentsTab';
import BillsCard from './components/BillsCard';
import IncomePhasesCard from './components/IncomePhasesCard';
import BenefitPipelineCard from './components/BenefitPipelineCard';
import ContactsCard from './components/ContactsCard';
import AssetsCard from './components/AssetsCard';
import { RecentWinsCard } from './components/RecentWinsCard';
import { HotListCard } from './components/HotListCard';
import { MedicalCard } from './components/MedicalCard';
import { InsuranceCard } from './components/InsuranceCard';
import { SelectedFacilityCard } from './components/SelectedFacilityCard';
import { TaskCreateForm } from './components/TaskCreateForm';
import type { Patient, Task, EligibilityResponse, FacilityResult } from './lib/api';
import { patientApi, taskApi, eligibilityApi, facilityApi } from './lib/api';

function App() {
  const [currentPatient, setCurrentPatient] = useState<Patient | null>(null);
  const [patients, setPatients] = useState<Patient[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [eligibility, setEligibility] = useState<EligibilityResponse | null>(null);
  const [facilities, setFacilities] = useState<FacilityResult[]>([]);
  const [showWizard, setShowWizard] = useState(false);
  const [showChat, setShowChat] = useState(false);
  const [activeTab, setActiveTab] = useState('executive');

  useEffect(() => {
    loadPatients();
  }, []);

  useEffect(() => {
    if (currentPatient) {
      loadPatientData(currentPatient.id);
    }
  }, [currentPatient]);

  const loadPatients = async () => {
    try {
      const data = await patientApi.list();
      setPatients(data);
      if (data.length > 0 && !currentPatient) {
        // Select the most recent patient (last in list) by default
        setCurrentPatient(data[data.length - 1]);
      }
    } catch (error) {
      console.error('Failed to load patients:', error);
    }
  };

  const loadPatientData = async (patientId: number) => {
    try {
      const [tasksData, eligData, facilitiesData] = await Promise.all([
        taskApi.list(patientId),
        eligibilityApi.check(patientId),
        facilityApi.search(currentPatient?.zip_code || '33401', currentPatient?.care_level_needed || 'AL'),
      ]);
      setTasks(tasksData);
      setEligibility(eligData);
      setFacilities(facilitiesData.facilities);
    } catch (error) {
      console.error('Failed to load patient data:', error);
    }
  };

  const handlePatientCreated = (patient: Patient) => {
    setPatients([...patients, patient]);
    setCurrentPatient(patient);
    setShowWizard(false);
  };

  const handleTaskComplete = async (taskId: number) => {
    try {
      await taskApi.updateStatus(taskId, 'completed');
      setTasks(tasks.map(t => t.id === taskId ? { ...t, status: 'completed' } : t));
    } catch (error) {
      console.error('Failed to update task:', error);
    }
  };

  const handleTaskNoteUpdate = async (taskId: number, note: string) => {
    try {
      await taskApi.updateNote(taskId, note);
      setTasks(tasks.map(t => t.id === taskId ? { ...t, notes: note } : t));
    } catch (error) {
      console.error('Failed to update task note:', error);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'bg-red-500';
      case 'high': return 'bg-orange-500';
      case 'medium': return 'bg-yellow-500';
      default: return 'bg-slate-500';
    }
  };

  return (
    <div className="min-h-screen text-slate-100">
      {/* Header */}
      <header className="glass-card border-b border-white/10 px-6 py-4 sticky top-0 z-50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h1 className="text-2xl font-bold text-teal-400 glow-text">CareNav Florida</h1>
            {patients.length > 0 && (
              <Select 
                value={currentPatient?.id?.toString()} 
                onValueChange={(value) => {
                  const patient = patients.find(p => p.id === parseInt(value));
                  if (patient) setCurrentPatient(patient);
                }}
              >
                <SelectTrigger className="w-[220px] glass-button text-slate-200">
                  <User className="w-4 h-4 mr-2" />
                  <SelectValue placeholder="Select patient" />
                </SelectTrigger>
                <SelectContent className="glass-card border-white/10">
                  {patients.map(patient => (
                    <SelectItem 
                      key={patient.id} 
                      value={patient.id.toString()}
                      className="text-slate-200 focus:bg-white/10"
                    >
                      {patient.first_name} {patient.last_name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}
          </div>
          <div className="flex items-center gap-3">
            <Button 
              variant="outline" 
              size="sm"
              onClick={() => setShowChat(!showChat)}
              className="glass-button text-slate-300"
            >
              <MessageSquare className="w-4 h-4 mr-2" />
              AI Assistant
            </Button>
            <Button 
              onClick={() => setShowWizard(true)}
              className="glass-button-accent text-white"
            >
              <Plus className="w-4 h-4 mr-2" />
              New Patient
            </Button>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Main Content */}
        <main className={`flex-1 p-6 ${showChat ? 'mr-96' : ''}`}>
          {!currentPatient ? (
            <div className="flex flex-col items-center justify-center h-96">
              <h2 className="text-xl text-slate-400 mb-4">No patients yet</h2>
              <Button onClick={() => setShowWizard(true)} className="bg-emerald-600 hover:bg-emerald-700">
                <Plus className="w-4 h-4 mr-2" />
                Add Your First Patient
              </Button>
            </div>
          ) : (
                        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
                          <TabsList className="glass-card p-1 gap-1">
                            <TabsTrigger value="executive" className="glass-tab data-[state=active]:glass-tab-active">
                              <LayoutDashboard className="w-4 h-4 mr-2" />
                              Executive
                            </TabsTrigger>
                            <TabsTrigger value="overview" className="glass-tab data-[state=active]:glass-tab-active">
                              <Home className="w-4 h-4 mr-2" />
                              Overview
                            </TabsTrigger>
                            <TabsTrigger value="todo" className="glass-tab data-[state=active]:glass-tab-active">
                              <ClipboardList className="w-4 h-4 mr-2" />
                              To-Do
                            </TabsTrigger>
                            <TabsTrigger value="money" className="glass-tab data-[state=active]:glass-tab-active">
                              <DollarSign className="w-4 h-4 mr-2" />
                              Money
                            </TabsTrigger>
                                                        <TabsTrigger value="docs" className="glass-tab data-[state=active]:glass-tab-active">
                                                          <FileText className="w-4 h-4 mr-2" />
                                                          Docs
                                                        </TabsTrigger>
                                                        <TabsTrigger value="places" className="glass-tab data-[state=active]:glass-tab-active">
                                                          <MapPin className="w-4 h-4 mr-2" />
                                                          Places
                                                        </TabsTrigger>
                                                        <TabsTrigger value="contacts" className="glass-tab data-[state=active]:glass-tab-active">
                                                          <User className="w-4 h-4 mr-2" />
                                                          Contacts
                                                        </TabsTrigger>
                                                        <TabsTrigger value="medical" className="glass-tab data-[state=active]:glass-tab-active">
                                                          <Stethoscope className="w-4 h-4 mr-2" />
                                                          Medical
                                                        </TabsTrigger>
                                                        <TabsTrigger value="insurance" className="glass-tab data-[state=active]:glass-tab-active">
                                                          <Shield className="w-4 h-4 mr-2" />
                                                          Insurance
                                                        </TabsTrigger>
                                                        <TabsTrigger value="facility" className="glass-tab data-[state=active]:glass-tab-active">
                                                          <Building className="w-4 h-4 mr-2" />
                                                          Facility
                                                        </TabsTrigger>
                                                      </TabsList>

                            {/* Executive Summary Tab */}
                            <TabsContent value="executive" className="mt-6">
                              <div className="space-y-6">
                                {/* Recent Wins and Hot List Row */}
                                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                  <RecentWinsCard patientId={currentPatient.id} />
                                  <HotListCard patientId={currentPatient.id} onTaskComplete={handleTaskComplete} />
                                </div>
                  
                                {/* Executive Summary */}
                                <ExecutiveSummary
                                  patient={currentPatient}
                                  tasks={tasks}
                                  eligibility={eligibility}
                                  onTaskComplete={handleTaskComplete}
                                  onTaskNoteUpdate={handleTaskNoteUpdate}
                                />
                              </div>
                            </TabsContent>

              {/* Overview Tab */}
                            <TabsContent value="overview" className="mt-6">
                              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                {/* Eligibility Summary */}
                                <Card className="glass-card-hover">
                                  <CardHeader>
                                    <CardTitle className="text-teal-400 glow-text">Eligibility Status</CardTitle>
                                    <CardDescription className="text-slate-400">Medicaid & VA Benefits</CardDescription>
                                  </CardHeader>
                    <CardContent>
                      {eligibility ? (
                        <div className="space-y-4">
                          <div className="flex items-center justify-between">
                            <span>Medicaid</span>
                            <Badge className={eligibility.medicaid.eligible ? 'bg-emerald-600' : 'bg-red-600'}>
                              {eligibility.medicaid.eligible ? 'Eligible' : `$${eligibility.medicaid.over_by.toLocaleString()} over`}
                            </Badge>
                          </div>
                          <div className="flex items-center justify-between">
                            <span>VA A&A</span>
                            <Badge className={eligibility.va_aa.eligible ? 'bg-emerald-600' : 'bg-slate-600'}>
                              {eligibility.va_aa.eligible ? `$${eligibility.va_aa.monthly_benefit}/mo` : 'Not Eligible'}
                            </Badge>
                          </div>
                          {eligibility.gift_penalty.has_penalty && (
                            <div className="flex items-center gap-2 text-amber-400">
                              <AlertTriangle className="w-4 h-4" />
                              <span className="text-sm">{eligibility.gift_penalty.months} month penalty</span>
                            </div>
                          )}
                        </div>
                      ) : (
                        <p className="text-slate-400">Loading...</p>
                      )}
                    </CardContent>
                  </Card>

                  {/* Tasks Summary */}
                  <Card className="glass-card-hover">
                    <CardHeader>
                      <CardTitle className="text-teal-400">Action Items</CardTitle>
                      <CardDescription className="text-slate-400">
                        {tasks.filter(t => t.status !== 'completed').length} pending
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        {tasks.filter(t => t.status !== 'completed').slice(0, 3).map(task => (
                          <div key={task.id} className="flex items-center gap-2 text-sm">
                            <div className={`w-2 h-2 rounded-full ${getPriorityColor(task.priority)}`} />
                            <span className="truncate">{task.title}</span>
                          </div>
                        ))}
                        {tasks.filter(t => t.status !== 'completed').length === 0 && (
                          <p className="text-slate-400 text-sm">No pending tasks</p>
                        )}
                      </div>
                    </CardContent>
                  </Card>

                  {/* Top Facility */}
                  <Card className="glass-card-hover">
                    <CardHeader>
                      <CardTitle className="text-teal-400">Top Facility Match</CardTitle>
                      <CardDescription className="text-slate-400">Based on your criteria</CardDescription>
                    </CardHeader>
                    <CardContent>
                      {facilities.length > 0 ? (
                        <div className="space-y-2">
                          <p className="font-medium">{facilities[0].name}</p>
                          <p className="text-sm text-slate-400">{facilities[0].address}</p>
                          <div className="flex items-center gap-2">
                            <Badge className="bg-emerald-600">{facilities[0].match_score} pts</Badge>
                            <span className="text-sm">${facilities[0].rate_low.toLocaleString()}/mo</span>
                          </div>
                        </div>
                      ) : (
                        <p className="text-slate-400">No facilities found</p>
                      )}
                    </CardContent>
                  </Card>

                  {/* Bills Card (Ticket 3) */}
                  <BillsCard patientId={currentPatient.id} />
                </div>
              </TabsContent>

                            {/* To-Do Tab */}
                            <TabsContent value="todo" className="mt-6">
                              <Card className="glass-card-hover">
                                <CardHeader className="flex flex-row items-center justify-between">
                                  <div>
                                    <CardTitle className="text-teal-400">Action Items</CardTitle>
                                    <CardDescription className="text-slate-400">Tasks to complete for care planning</CardDescription>
                                  </div>
                                  <TaskCreateForm 
                                    patientId={currentPatient.id} 
                                    onTaskCreated={() => loadPatientData(currentPatient.id)} 
                                  />
                                </CardHeader>
                  <CardContent>
                    <ScrollArea className="h-96">
                      <div className="space-y-3">
                        {tasks.map(task => {
                          const isBlocked = task.blocked_by_task && task.status !== 'completed';
                          return (
                          <div 
                            key={task.id} 
                            className={`flex items-center justify-between p-3 rounded-lg border ${
                              task.status === 'completed' 
                                ? 'bg-slate-700/50 border-slate-600' 
                                : isBlocked
                                ? 'bg-amber-900/20 border-amber-600/50'
                                : 'bg-slate-700 border-slate-600'
                            }`}
                          >
                            <div className="flex items-center gap-3">
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleTaskComplete(task.id)}
                                disabled={task.status === 'completed' || isBlocked}
                                className="p-1"
                                title={isBlocked ? `Blocked by: ${task.blocked_by_task}` : undefined}
                              >
                                {isBlocked ? (
                                  <Lock className="w-5 h-5 text-amber-400" />
                                ) : (
                                  <CheckCircle2 className={`w-5 h-5 ${
                                    task.status === 'completed' ? 'text-teal-400' : 'text-slate-500'
                                  }`} />
                                )}
                              </Button>
                              <div>
                                <p className={task.status === 'completed' ? 'line-through text-slate-500' : ''}>
                                  {task.title}
                                </p>
                                {task.description && (
                                  <p className="text-sm text-slate-400">{task.description}</p>
                                )}
                                {isBlocked && (
                                  <p className="text-xs text-amber-400 mt-1">Blocked by: {task.blocked_by_task}</p>
                                )}
                                {task.assignee && (
                                  <p className="text-xs text-blue-400 mt-1">
                                    Assigned to: {task.assignee}
                                    {task.assignee_phone && (
                                      <Button 
                                        variant="ghost" 
                                        size="sm" 
                                        className="text-teal-400 hover:text-teal-300 p-0 h-auto ml-2"
                                        onClick={() => window.open(`tel:${task.assignee_phone}`)}
                                      >
                                        <Phone className="w-3 h-3 mr-1" />
                                        {task.assignee_phone}
                                      </Button>
                                    )}
                                  </p>
                                )}
                              </div>
                            </div>
                            <div className="flex items-center gap-2">
                              {task.phone && (
                                <Button 
                                  variant="ghost" 
                                  size="sm" 
                                  className="text-teal-400 hover:text-teal-300"
                                  onClick={() => window.open(`tel:${task.phone}`)}
                                >
                                  <Phone className="w-4 h-4" />
                                </Button>
                              )}
                              <Badge className={getPriorityColor(task.priority)}>{task.priority}</Badge>
                            </div>
                          </div>
                        )})}
                        {tasks.length === 0 && (
                          <p className="text-center text-slate-400 py-8">No tasks yet. Chat with the AI assistant to get started.</p>
                        )}
                      </div>
                    </ScrollArea>
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Money Tab */}
              <TabsContent value="money" className="mt-6">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <Card className="glass-card-hover">
                    <CardHeader>
                      <CardTitle className="text-teal-400">Medicaid Eligibility</CardTitle>
                    </CardHeader>
                    <CardContent>
                      {eligibility ? (
                        <div className="space-y-4">
                          <div className="flex justify-between">
                            <span className="text-slate-400">Countable Assets</span>
                            <span className="font-medium">${eligibility.medicaid.countable.toLocaleString()}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-slate-400">Asset Limit</span>
                            <span className="font-medium">$2,000</span>
                          </div>
                          <Separator className="bg-slate-700" />
                          <div className="flex justify-between">
                            <span className="text-slate-400">Over Limit By</span>
                            <span className={`font-medium ${eligibility.medicaid.over_by > 0 ? 'text-red-400' : 'text-teal-400'}`}>
                              ${eligibility.medicaid.over_by.toLocaleString()}
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-slate-400">Monthly Income</span>
                            <span className="font-medium">${eligibility.medicaid.total_income.toLocaleString()}</span>
                          </div>
                          <p className="text-sm text-slate-400 mt-4">{eligibility.medicaid.explanation}</p>
                        </div>
                      ) : (
                        <p className="text-slate-400">Loading...</p>
                      )}
                    </CardContent>
                  </Card>

                  <Card className="glass-card-hover">
                    <CardHeader>
                      <CardTitle className="text-teal-400">VA Aid & Attendance</CardTitle>
                    </CardHeader>
                    <CardContent>
                      {eligibility ? (
                        <div className="space-y-4">
                          <div className="flex justify-between">
                            <span className="text-slate-400">Status</span>
                            <Badge className={eligibility.va_aa.eligible ? 'bg-emerald-600' : 'bg-slate-600'}>
                              {eligibility.va_aa.eligible ? 'Eligible' : 'Not Eligible'}
                            </Badge>
                          </div>
                          {eligibility.va_aa.eligible && (
                            <>
                              <div className="flex justify-between">
                                <span className="text-slate-400">Benefit Type</span>
                                <span className="font-medium capitalize">{eligibility.va_aa.type.replace('_', ' ')}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-slate-400">Monthly Benefit</span>
                                <span className="font-medium text-teal-400">${eligibility.va_aa.monthly_benefit.toLocaleString()}</span>
                              </div>
                            </>
                          )}
                          <p className="text-sm text-slate-400 mt-4">{eligibility.va_aa.explanation}</p>
                        </div>
                      ) : (
                        <p className="text-slate-400">Loading...</p>
                      )}
                    </CardContent>
                  </Card>
                  {/* Income Phases (Ticket 4) */}
                  <IncomePhasesCard patientId={currentPatient.id} />

                  {/* Benefit Applications Pipeline (Ticket 5) */}
                  <BenefitPipelineCard patientId={currentPatient.id} />

                  {/* Assets Sale Pipeline (Ticket 8) */}
                  <AssetsCard patientId={currentPatient.id} />
                </div>
              </TabsContent>
              {/* Docs Tab */}
              <TabsContent value="docs" className="mt-6">
                {currentPatient && (
                  <DocumentsTab 
                    patientId={currentPatient.id} 
                    patientName={`${currentPatient.first_name} ${currentPatient.last_name}`}
                  />
                )}
              </TabsContent>

              {/* Places Tab */}
              <TabsContent value="places" className="mt-6">
                <Card className="glass-card-hover">
                  <CardHeader>
                    <CardTitle className="text-teal-400">Facility Matches</CardTitle>
                    <CardDescription className="text-slate-400">
                      Sorted by match score based on your criteria
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ScrollArea className="h-96">
                      <div className="space-y-4">
                        {facilities.map((facility, i) => (
                          <div key={i} className="p-4 bg-slate-700 rounded-lg border border-slate-600">
                            <div className="flex items-start justify-between">
                              <div>
                                <h3 className="font-medium text-lg">{facility.name}</h3>
                                <p className="text-sm text-slate-400">{facility.address}</p>
                                <p className="text-sm text-slate-400">{facility.phone}</p>
                              </div>
                              <Badge className="bg-emerald-600">{facility.match_score} pts</Badge>
                            </div>
                            <div className="mt-3 flex flex-wrap gap-2">
                              <Badge variant="outline" className="border-slate-500">
                                ${facility.rate_low.toLocaleString()}-${facility.rate_high.toLocaleString()}/mo
                              </Badge>
                              {facility.accepts_medicaid && (
                                <Badge className="bg-blue-600">
                                  Medicaid{facility.medicaid_day_one ? ' Day 1' : ''}
                                </Badge>
                              )}
                              {facility.memory_care && (
                                <Badge className="bg-purple-600">Memory Care</Badge>
                              )}
                              <Badge variant="outline" className="border-slate-500">
                                {facility.distance_miles.toFixed(1)} mi
                              </Badge>
                            </div>
                            <div className="mt-3 text-sm">
                              <span className={facility.affordability.affordable ? 'text-teal-400' : 'text-amber-400'}>
                                {facility.affordability.affordable 
                                  ? `Within budget (+$${Math.abs(facility.affordability.gap_or_surplus).toLocaleString()}/mo surplus)`
                                  : `$${facility.affordability.monthly_shortfall.toLocaleString()}/mo shortfall`
                                }
                              </span>
                            </div>
                          </div>
                        ))}
                        {facilities.length === 0 && (
                          <p className="text-center text-slate-400 py-8">No facilities found. Complete the intake wizard to search.</p>
                        )}
                      </div>
                    </ScrollArea>
                  </CardContent>
                </Card>
              </TabsContent>

                          {/* Contacts Tab (Ticket 6) */}
                          <TabsContent value="contacts" className="mt-6">
                            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                              <ContactsCard patientId={currentPatient.id} />
                            </div>
                          </TabsContent>

                          {/* Medical Tab */}
                          <TabsContent value="medical" className="mt-6">
                            <MedicalCard patientId={currentPatient.id} />
                          </TabsContent>

                          {/* Insurance Tab */}
                          <TabsContent value="insurance" className="mt-6">
                            <InsuranceCard patientId={currentPatient.id} />
                          </TabsContent>

                          {/* Facility Tab (Selected Facility) */}
                          <TabsContent value="facility" className="mt-6">
                            <SelectedFacilityCard patientId={currentPatient.id} />
                          </TabsContent>
                        </Tabs>
          )}
        </main>

        {/* Chat Panel */}
        {showChat && (
          <aside className="fixed right-0 top-0 h-full w-96 bg-slate-800 border-l border-slate-700 flex flex-col">
            <div className="p-4 border-b border-slate-700 flex items-center justify-between">
              <h2 className="font-semibold text-teal-400">AI Assistant</h2>
              <Button variant="ghost" size="sm" onClick={() => setShowChat(false)}>
                &times;
              </Button>
            </div>
            <ChatPanel patientId={currentPatient?.id} />
          </aside>
        )}
      </div>

      {/* Intake Wizard Modal */}
      {showWizard && (
        <IntakeWizard 
          onComplete={handlePatientCreated} 
          onClose={() => setShowWizard(false)} 
        />
      )}
    </div>
  );
}

export default App;
