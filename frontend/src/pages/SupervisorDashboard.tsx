// frontend/src/pages/SupervisorDashboard.tsx
import React, { useEffect, useState } from "react";
import { useUser } from "@clerk/clerk-react";
import { useNavigate } from "react-router-dom";
import TaskForm from "../components/TaskForm";
import TaskList from "../components/TaskList";

interface Task {
  id: string;
  description: string;
  requiredSkills: string[];
  dueDate: string;
  startDate: string;
  assignedTo?: string;
}

const SupervisorDashboard: React.FC = () => {
  const { user, isLoaded } = useUser();
  const navigate = useNavigate();
  const [tasks, setTasks] = useState<Task[]>([]);

  useEffect(() => {
    if (!isLoaded || !user) return;

    const userRole = user?.unsafeMetadata?.role as string | undefined;

    if (userRole !== "supervisor") {
      navigate("/role-selection");
      return;
    }

    interface ApiTask {
      id: string;
      description: string;
      required_skills: string[];
      due_date: string;
      start_date: string;
      assigned_to?: string;
    }

    const fetchTasks = async () => {
      try {
        const response = await fetch(
          `http://localhost:8000/tasks/?user_id=${user.id}&role=supervisor`
        );
        if (!response.ok) throw new Error("Failed to fetch tasks");
        const data = await response.json();
        setTasks(
          data.map((task: ApiTask) => ({
            id: task.id,
            description: task.description,
            requiredSkills: task.required_skills,
            dueDate: task.due_date,
            startDate: task.start_date,
            assignedTo: task.assigned_to,
          }))
        );
      } catch (error) {
        console.error("Error fetching tasks:", error);
      }
    };

    fetchTasks();
  }, [user, isLoaded, navigate]);

  // frontend/src/pages/SupervisorDashboard.tsx
  const handleAddTask = async (newTask: {
    description: string;
    requiredSkills: string[];
    dueDate: string;
    startDate: string;
  }) => {
    try {
      const response = await fetch("http://localhost:8000/tasks/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          supervisor_id: user?.id || "",
          description: newTask.description,
          required_skills: newTask.requiredSkills,
          due_date: newTask.dueDate,
          start_date: newTask.startDate,
          assigned_to: null, // Default; adjust if needed
          status: "pending", // Required by Task model
        }),
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(
          `Failed to add task: ${errorData.detail || response.statusText}`
        );
      }
      const createdTask = await response.json();
      setTasks([
        ...tasks,
        {
          id: createdTask.id,
          description: createdTask.description,
          requiredSkills: createdTask.required_skills,
          dueDate: createdTask.due_date,
          startDate: createdTask.start_date,
          assignedTo: createdTask.assigned_to,
        },
      ]);
    } catch (error) {
      console.error("Error adding task:", error);
      // Optionally, set an error state to display to the user
      // e.g., setError(error.message);
    }
  };

  const handleUpdateTask = async (updatedTask: Task) => {
    try {
      const response = await fetch(
        `http://localhost:8000/tasks/${updatedTask.id}`,
        {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            description: updatedTask.description,
            // Include other fields if editable
          }),
        }
      );
      if (!response.ok) throw new Error("Failed to update task");
      const patchedTask = await response.json();
      setTasks(
        tasks.map((task) =>
          task.id === updatedTask.id
            ? {
                id: patchedTask.id,
                description: patchedTask.description,
                requiredSkills: patchedTask.required_skills,
                dueDate: patchedTask.due_date,
                startDate: patchedTask.start_date,
                assignedTo: patchedTask.assigned_to,
              }
            : task
        )
      );
    } catch (error) {
      console.error("Error updating task:", error);
    }
  };
  const handleRemoveTask = (taskId: string) => {
    setTasks(tasks.filter((task) => task.id !== taskId));
  };

  if (!isLoaded || !user) return <div>Loading...</div>;

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Supervisor Dashboard</h1>
      <p>Welcome, {user.firstName || "Supervisor"}</p>
      <TaskForm onSubmit={handleAddTask} />
      <TaskList
        tasks={tasks}
        onRemove={handleRemoveTask}
        onUpdate={handleUpdateTask}
        showAssigned
      />
    </div>
  );
};

export default SupervisorDashboard;
