import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';

const IntentDonut = ({ data }) => {
  return (
    <div className="h-full flex flex-col">
      <h3 className="text-xs font-bold uppercase tracking-widest text-slate-400 mb-4 px-1">Intent Distribution</h3>
      <div className="flex-1 min-h-[240px]">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={80}
              paddingAngle={5}
              dataKey="value"
              stroke="none"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip 
              contentStyle={{ background: '#161B22', border: '1px solid #30363D', borderRadius: '8px', fontSize: '12px' }}
              itemStyle={{ color: '#E6EDF3' }}
            />
            <Legend 
              verticalAlign="bottom" 
              align="center"
              iconType="circle"
              formatter={(value) => <span className="text-[10px] font-bold uppercase tracking-tighter text-slate-400">{value}</span>}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default IntentDonut;
