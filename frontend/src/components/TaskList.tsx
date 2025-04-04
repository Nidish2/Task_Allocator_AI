// frontend/src/components/TaskList.tsx
import React, { useState } from "react";

interface Task {
  id: string;
  description: string;
  requiredSkills: string[];
  dueDate: string;
  startDate: string;
  assignedTo?: string;
}

interface TaskListProps {
  tasks: Task[];
  onRemove?: (taskId: string) => void;
  onUpdate?: (task: Task) => void;
  showAssigned?: boolean;
}

const TaskList: React.FC<TaskListProps> = ({
  tasks,
  onRemove,
  onUpdate,
  showAssigned = false,
}) => {
  const [editingTaskId, setEditingTaskId] = useState<string | null>(null);
  const [editDescription, setEditDescription] = useState("");

  const handleEdit = (task: Task) => {
    setEditingTaskId(task.id);
    setEditDescription(task.description);
  };

  const handleSave = (task: Task) => {
    if (onUpdate) {
      onUpdate({ ...task, description: editDescription });
    }
    setEditingTaskId(null);
  };

  return (
    <div className="mt-4">
      <h2 className="text-xl font-semibold mb-2">Tasks</h2>
      {tasks.length === 0 ? (
        <p>No tasks available.</p>
      ) : (
        <ul className="space-y-2">
          {tasks.map((task) => (
            <li key={task.id} className="bg-white p-4 rounded shadow">
              {editingTaskId === task.id ? (
                <>
                  <input
                    type="text"
                    value={editDescription}
                    onChange={(e) => setEditDescription(e.target.value)}
                    className="w-full p-2 border rounded mb-2"
                  />
                  <button
                    onClick={() => handleSave(task)}
                    className="bg-blue-500 text-white p-1 rounded mr-2"
                  >
                    Save
                  </button>
                  <button
                    onClick={() => setEditingTaskId(null)}
                    className="bg-gray-500 text-white p-1 rounded"
                  >
                    Cancel
                  </button>
                </>
              ) : (
                <>
                  <p>
                    <strong>Description:</strong> {task.description}
                  </p>
                  <p>
                    <strong>Skills:</strong> {task.requiredSkills.join(", ")}
                  </p>
                  <p>
                    <strong>Start Date:</strong> {task.startDate}
                  </p>
                  <p>
                    <strong>Due Date:</strong> {task.dueDate}
                  </p>
                  {showAssigned && task.assignedTo && (
                    <p>
                      <strong>Assigned To:</strong> {task.assignedTo}
                    </p>
                  )}
                  {onUpdate && (
                    <button
                      onClick={() => handleEdit(task)}
                      className="mt-2 bg-yellow-500 text-white p-1 rounded mr-2"
                    >
                      Edit
                    </button>
                  )}
                  {onRemove && (
                    <button
                      onClick={() => onRemove(task.id)}
                      className="mt-2 bg-red-500 text-white p-1 rounded"
                    >
                      Remove
                    </button>
                  )}
                </>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default TaskList;
