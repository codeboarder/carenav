/**
 * Hot List Card - Priority tasks that need immediate attention
 */
import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Flame, Phone, Clock, CheckCircle2, AlertTriangle } from 'lucide-react';
import { taskApi, Task } from '@/lib/api';

interface HotListCardProps {
  patientId: number;
  onTaskComplete?: () => void;
}

const priorityColors: Record<string, string> = {
  urgent: 'bg-red-500/20 text-red-300 border-red-500/30',
  high: 'bg-orange-500/20 text-orange-300 border-orange-500/30',
  medium: 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30',
  low: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
};

export function HotListCard({ patientId, onTaskComplete }: HotListCardProps) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('all');

  useEffect(() => {
    const fetchTasks = async () => {
      try {
        const data = await taskApi.list(patientId, 'pending');
        // Sort by priority and due date
        const sorted = data.sort((a, b) => {
          const priorityOrder: Record<string, number> = { urgent: 0, high: 1, medium: 2, low: 3 };
          const aPriority = priorityOrder[a.priority] ?? 4;
          const bPriority = priorityOrder[b.priority] ?? 4;
          if (aPriority !== bPriority) return aPriority - bPriority;
          if (a.due_date && b.due_date) return new Date(a.due_date).getTime() - new Date(b.due_date).getTime();
          return 0;
        });
        setTasks(sorted);
      } catch (error) {
        console.error('Failed to fetch tasks:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchTasks();
  }, [patientId]);

  const handleComplete = async (taskId: number) => {
    try {
      await taskApi.updateStatus(taskId, 'completed');
      setTasks(tasks.filter(t => t.id !== taskId));
      onTaskComplete?.();
    } catch (error) {
      console.error('Failed to complete task:', error);
    }
  };

  const handleCall = (phone: string) => {
    window.open(`tel:${phone}`, '_self');
  };

  const formatDueDate = (dateStr: string | undefined) => {
    if (!dateStr) return null;
    const date = new Date(dateStr);
    const today = new Date();
    const diffDays = Math.ceil((date.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
    
    if (diffDays < 0) return { text: `${Math.abs(diffDays)}d overdue`, isOverdue: true };
    if (diffDays === 0) return { text: 'Today', isOverdue: false };
    if (diffDays === 1) return { text: 'Tomorrow', isOverdue: false };
    return { text: `${diffDays}d`, isOverdue: false };
  };

  const filteredTasks = filter === 'all' 
    ? tasks 
    : tasks.filter(t => t.assignee?.toLowerCase() === filter.toLowerCase());

  // Get unique assignees
  const assignees = [...new Set(tasks.map(t => t.assignee).filter(Boolean))];

  // Get hot tasks (urgent + high priority, or overdue)
  const hotTasks = filteredTasks.filter(t => 
    t.priority === 'urgent' || 
    t.priority === 'high' || 
    (t.due_date && new Date(t.due_date) < new Date())
  );

  if (loading) {
    return (
      <Card className="bg-white/5 border-white/10">
        <CardHeader className="pb-2">
          <CardTitle className="text-lg text-white flex items-center gap-2">
            <Flame className="h-5 w-5 text-orange-400" />
            Hot List
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-white/60 text-sm">Loading...</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="bg-gradient-to-br from-red-500/10 to-orange-500/10 border-orange-500/20">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg text-white flex items-center gap-2">
            <Flame className="h-5 w-5 text-orange-400" />
            Hot List
            <Badge variant="outline" className="ml-2 bg-red-500/20 text-red-300 border-red-500/30">
              {hotTasks.length} urgent
            </Badge>
          </CardTitle>
        </div>
        {/* Filter buttons */}
        <div className="flex gap-1 mt-2 flex-wrap">
          <Button
            variant={filter === 'all' ? 'default' : 'ghost'}
            size="sm"
            className={filter === 'all' ? 'bg-teal-500 text-white' : 'text-white/60 hover:text-white'}
            onClick={() => setFilter('all')}
          >
            All ({tasks.length})
          </Button>
          {assignees.map(assignee => (
            <Button
              key={assignee}
              variant={filter === assignee ? 'default' : 'ghost'}
              size="sm"
              className={filter === assignee ? 'bg-teal-500 text-white' : 'text-white/60 hover:text-white'}
              onClick={() => setFilter(assignee || 'all')}
            >
              {assignee}
            </Button>
          ))}
        </div>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[280px] pr-4">
          <div className="space-y-2">
            {filteredTasks.length === 0 ? (
              <p className="text-white/60 text-sm text-center py-4">No pending tasks</p>
            ) : (
              filteredTasks.map((task) => {
                const dueInfo = formatDueDate(task.due_date);
                return (
                  <div
                    key={task.id}
                    className="p-3 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition-colors"
                  >
                    <div className="flex items-start gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-6 w-6 p-0 text-white/40 hover:text-green-400 shrink-0 mt-0.5"
                        onClick={() => handleComplete(task.id)}
                      >
                        <CheckCircle2 className="h-5 w-5" />
                      </Button>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <Badge 
                            variant="outline" 
                            className={`text-xs ${priorityColors[task.priority] || priorityColors.medium}`}
                          >
                            {task.priority}
                          </Badge>
                          {task.blocked_by_task && (
                            <Badge variant="outline" className="text-xs bg-gray-500/20 text-gray-300 border-gray-500/30">
                              Blocked
                            </Badge>
                          )}
                          {dueInfo && (
                            <span className={`text-xs flex items-center gap-1 ${dueInfo.isOverdue ? 'text-red-400' : 'text-white/50'}`}>
                              {dueInfo.isOverdue && <AlertTriangle className="h-3 w-3" />}
                              <Clock className="h-3 w-3" />
                              {dueInfo.text}
                            </span>
                          )}
                        </div>
                        <p className="text-white text-sm font-medium mt-1">{task.title}</p>
                        {task.assignee && (
                          <p className="text-white/50 text-xs mt-0.5">Assigned: {task.assignee}</p>
                        )}
                      </div>
                      {task.phone && (
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-8 w-8 p-0 text-teal-400 hover:text-teal-300 hover:bg-teal-500/20 shrink-0"
                          onClick={() => handleCall(task.phone!)}
                        >
                          <Phone className="h-4 w-4" />
                        </Button>
                      )}
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
