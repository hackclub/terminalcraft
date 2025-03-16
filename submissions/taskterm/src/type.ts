export interface ITask {
  id: number;
  description: string;
  completed: boolean;
  created_at: string;
  priority: "high" | "medium" | "low";
  due_date?: string;
  tags?: string[];
}
