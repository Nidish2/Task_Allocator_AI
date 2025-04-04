// frontend/src/pages/EmployeeDashboard.tsx
import React, { useEffect, useState } from "react";
import { useUser } from "@clerk/clerk-react";
import { useNavigate } from "react-router-dom";
import SkillForm from "../components/SkillForm";
import TaskList from "../components/TaskList";

interface Task {
  id: string;
  description: string;
  requiredSkills: string[];
  dueDate: string;
  startDate: string;
}

interface TaskResponse {
  id: string;
  description: string;
  required_skills: string[];
  due_date: string;
  start_date: string;
}

interface Skill {
  skillName: string;
  proficiencyLevel: number;
}

const EmployeeDashboard: React.FC = () => {
  const { user, isLoaded } = useUser();
  const navigate = useNavigate();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [skills, setSkills] = useState<Skill[]>([]);

  useEffect(() => {
    if (!isLoaded || !user) return;

    const userRole = user?.unsafeMetadata?.role as string | undefined;

    if (userRole !== "employee") {
      navigate("/role-selection");
      return;
    }

    const fetchData = async () => {
      try {
        // Fetch tasks
        const tasksResponse = await fetch(
          `http://localhost:8000/tasks?user_id=${user.id}&role=employee`
        );
        if (!tasksResponse.ok) throw new Error("Failed to fetch tasks");

        const tasksData = await tasksResponse.json();
        setTasks(
          tasksData.map((task: TaskResponse) => ({
            id: task.id,
            description: task.description,
            requiredSkills: task.required_skills,
            dueDate: task.due_date,
            startDate: task.start_date,
          }))
        );

        // Fetch skills
        const skillsResponse = await fetch(
          `http://localhost:8000/skills/${user.id}`
        );
        if (!skillsResponse.ok) throw new Error("Failed to fetch skills");
        const skillsData = await skillsResponse.json();
        setSkills(
          skillsData.map(
            (skill: { skill_name: string; proficiency_level: number }) => ({
              skillName: skill.skill_name,
              proficiencyLevel: skill.proficiency_level,
            })
          )
        );
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    fetchData();
  }, [user, isLoaded, navigate]);

  // Placeholder for handleAddSkill (updated in Step 2)
  const handleAddSkill = (skill: {
    skillName: string;
    proficiencyLevel: number;
  }) => {
    setSkills([...skills, skill]);
  };

  if (!isLoaded || !user) return <div>Loading...</div>;

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Employee Dashboard</h1>
      <p>Welcome, {user.firstName || "Employee"}</p>
      <SkillForm onSubmit={handleAddSkill} />
      <div className="mt-4">
        <h2 className="text-xl font-semibold">Your Skills</h2>
        <ul className="list-disc pl-5">
          {skills.map((skill, idx) => (
            <li key={idx}>
              {skill.skillName} (Proficiency: {skill.proficiencyLevel})
            </li>
          ))}
        </ul>
      </div>
      <TaskList tasks={tasks} />
    </div>
  );
};

export default EmployeeDashboard;
