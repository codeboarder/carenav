// Built by Gregory Katz and Rick Weyenberg
// Code is as-is, open source

/**
 * Task Create Form - Add new tasks with priority, assignee, due date
 */
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Plus } from 'lucide-react';
import { taskApi } from '@/lib/api';

interface TaskCreateFormProps {
  patientId: number;
  onTaskCreated?: () => void;
}

export function TaskCreateForm({ patientId, onTaskCreated }: TaskCreateFormProps) {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: 'general',
    priority: 'medium',
    due_date: '',
    phone: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.title.trim()) return;

    setLoading(true);
    try {
      await taskApi.create(patientId, {
        title: formData.title,
        description: formData.description || undefined,
        category: formData.category,
        priority: formData.priority,
        due_date: formData.due_date || undefined,
        phone: formData.phone || undefined,
      });
      setFormData({
        title: '',
        description: '',
        category: 'general',
        priority: 'medium',
        due_date: '',
        phone: '',
      });
      setOpen(false);
      onTaskCreated?.();
    } catch (error) {
      console.error('Failed to create task:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button className="bg-teal-500 hover:bg-teal-600 text-white">
          <Plus className="h-4 w-4 mr-2" />
          Add Task
        </Button>
      </DialogTrigger>
      <DialogContent className="bg-[#0B1437] border-white/10 text-white sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle className="text-white">Create New Task</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4 mt-4">
          <div className="space-y-2">
            <Label htmlFor="title" className="text-white">Title *</Label>
            <Input
              id="title"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              placeholder="Enter task title"
              className="bg-white/5 border-white/10 text-white placeholder:text-white/40"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="description" className="text-white">Description</Label>
            <Textarea
              id="description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Enter task description"
              className="bg-white/5 border-white/10 text-white placeholder:text-white/40 min-h-[80px]"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="category" className="text-white">Category</Label>
              <Select
                value={formData.category}
                onValueChange={(value) => setFormData({ ...formData, category: value })}
              >
                <SelectTrigger className="bg-white/5 border-white/10 text-white">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-[#0B1437] border-white/10">
                  <SelectItem value="general" className="text-white hover:bg-white/10">General</SelectItem>
                  <SelectItem value="financial" className="text-white hover:bg-white/10">Financial</SelectItem>
                  <SelectItem value="benefit" className="text-white hover:bg-white/10">Benefit</SelectItem>
                  <SelectItem value="facility" className="text-white hover:bg-white/10">Facility</SelectItem>
                  <SelectItem value="document" className="text-white hover:bg-white/10">Document</SelectItem>
                  <SelectItem value="legal" className="text-white hover:bg-white/10">Legal</SelectItem>
                  <SelectItem value="veteran" className="text-white hover:bg-white/10">Veteran</SelectItem>
                  <SelectItem value="medical" className="text-white hover:bg-white/10">Medical</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="priority" className="text-white">Priority</Label>
              <Select
                value={formData.priority}
                onValueChange={(value) => setFormData({ ...formData, priority: value })}
              >
                <SelectTrigger className="bg-white/5 border-white/10 text-white">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-[#0B1437] border-white/10">
                  <SelectItem value="urgent" className="text-red-300 hover:bg-white/10">Urgent</SelectItem>
                  <SelectItem value="high" className="text-orange-300 hover:bg-white/10">High</SelectItem>
                  <SelectItem value="medium" className="text-yellow-300 hover:bg-white/10">Medium</SelectItem>
                  <SelectItem value="low" className="text-blue-300 hover:bg-white/10">Low</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="due_date" className="text-white">Due Date</Label>
              <Input
                id="due_date"
                type="date"
                value={formData.due_date}
                onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
                className="bg-white/5 border-white/10 text-white [color-scheme:dark]"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="phone" className="text-white">Phone (tap to call)</Label>
              <Input
                id="phone"
                type="tel"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                placeholder="(555) 555-5555"
                className="bg-white/5 border-white/10 text-white placeholder:text-white/40"
              />
            </div>
          </div>

          <div className="flex justify-end gap-2 pt-4">
            <Button
              type="button"
              variant="ghost"
              onClick={() => setOpen(false)}
              className="text-white hover:bg-white/10"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={loading || !formData.title.trim()}
              className="bg-teal-500 hover:bg-teal-600 text-white"
            >
              {loading ? 'Creating...' : 'Create Task'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
