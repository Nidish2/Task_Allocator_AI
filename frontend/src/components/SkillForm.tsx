// frontend/src/components/SkillForm.tsx
import React, { useState } from "react";

interface SkillFormProps {
  onSubmit: (skill: { skillName: string; proficiencyLevel: number }) => void;
}

const SkillForm: React.FC<SkillFormProps> = ({ onSubmit }) => {
  const [skillName, setSkillName] = useState("");
  const [proficiencyLevel, setProficiencyLevel] = useState(1);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (skillName.trim()) {
      onSubmit({ skillName: skillName.trim(), proficiencyLevel });
      setSkillName("");
      setProficiencyLevel(1);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="mt-4 bg-gray-100 p-4 rounded">
      <h2 className="text-xl font-semibold mb-2">Add Skill</h2>
      <div className="mb-2">
        <label className="block">Skill Name</label>
        <input
          type="text"
          value={skillName}
          onChange={(e) => setSkillName(e.target.value)}
          className="w-full p-2 border rounded"
          required
        />
      </div>
      <div className="mb-2">
        <label className="block">Proficiency Level (1-5)</label>
        <input
          type="number"
          min="1"
          max="5"
          value={proficiencyLevel}
          onChange={(e) => setProficiencyLevel(Number(e.target.value))}
          className="w-full p-2 border rounded"
          required
        />
      </div>
      <button type="submit" className="bg-green-500 text-white p-2 rounded">
        Add Skill
      </button>
    </form>
  );
};

export default SkillForm;
