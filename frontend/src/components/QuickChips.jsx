import React from 'react';
import { Search, RotateCcw, HelpCircle, Package } from 'lucide-react';

const QuickChips = ({ onSelect }) => {
  const chips = [
    { text: "Where is my order?", icon: Package, color: "text-brand-blue" },
    { text: "I want a refund", icon: RotateCcw, color: "text-brand-amber" },
    { text: "Return policy", icon: HelpCircle, color: "text-brand-purple" },
    { text: "Track order #5", icon: Search, color: "text-brand-blue" },
  ];

  return (
    <div className="flex flex-wrap gap-2 mb-4 px-4">
      {chips.map((chip, idx) => (
        <button
          key={idx}
          onClick={() => onSelect(chip.text)}
          className="flex items-center gap-2 px-3 py-1.5 rounded-full glass-panel hover:bg-slate-700/50 transition-colors text-xs text-slate-300 border border-slate-700/50"
        >
          <chip.icon className={`w-3.5 h-3.5 ${chip.color}`} />
          {chip.text}
        </button>
      ))}
    </div>
  );
};

export default QuickChips;
