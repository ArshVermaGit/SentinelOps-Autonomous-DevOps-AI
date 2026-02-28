"use client"
import React, { useCallback, useEffect } from 'react';
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  Edge,
  Node,
} from 'reactflow';
import 'reactflow/dist/style.css';

interface GraphData {
  pr_id: string;
  pr_title: string;
  author: string;
  author_failure_rate: number;
  commits: Array<{
    sha: string;
    message: string;
  }>;
  files: string[];
  ci_run_id: string;
  ci_status: string;
  incident_title: string;
}

export default function IncidentMemoryGraph({ data }: { data?: GraphData }) {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  const onConnect = useCallback((params: Connection | Edge) => setEdges((eds) => addEdge(params, eds)), [setEdges]);

  useEffect(() => {
    if (!data) return;

    const newNodes: Node[] = [
      { 
        id: 'pr', 
        position: { x: 50, y: 150 }, 
        data: { label: `PR: ${data.pr_title}` }, 
        type: 'input', 
        style: { background: '#111827', color: '#fff', border: '1px solid #6366f1', borderRadius: '8px', padding: '10px' } 
      },
      { 
        id: 'author', 
        position: { x: 250, y: 50 }, 
        data: { label: `Author: ${data.author}\nFail Rate: ${Math.round(data.author_failure_rate * 100)}%` }, 
        style: { background: '#312e81', color: '#fff', border: '1px solid #4f46e5', borderRadius: '8px', padding: '10px' } 
      },
      { 
        id: 'commit', 
        position: { x: 250, y: 150 }, 
        data: { label: `Commit: ${data.commits[0]?.sha.substring(0, 7)}\n${data.commits[0]?.message}` }, 
        style: { background: '#111827', color: '#fff', border: '1px solid #374151', borderRadius: '8px', padding: '10px' } 
      },
      { 
        id: 'files', 
        position: { x: 250, y: 250 }, 
        data: { label: `Files:\n${data.files.join('\n')}` }, 
        style: { background: '#111827', color: '#fff', border: '1px solid #374151', borderRadius: '8px', padding: '10px' } 
      },
      { 
        id: 'ci', 
        position: { x: 500, y: 150 }, 
        data: { label: `CI Run #${data.ci_run_id}\nStatus: ${data.ci_status}` }, 
        style: { background: data.ci_status === 'failed' ? '#7f1d1d' : '#064e3b', color: '#fff', border: `1px solid ${data.ci_status === 'failed' ? '#ef4444' : '#10b981'}`, borderRadius: '8px', padding: '10px' } 
      },
      { 
        id: 'incident', 
        position: { x: 750, y: 150 }, 
        data: { label: `Incident:\n${data.incident_title}` }, 
        type: 'output', 
        style: { background: '#7c2d12', color: '#fff', border: '1px solid #f97316', borderRadius: '8px', padding: '10px' } 
      },
    ];

    const newEdges: Edge[] = [
      { id: 'e-pr-author', source: 'pr', target: 'author', animated: true, style: { stroke: '#6366f1' } },
      { id: 'e-pr-commit', source: 'pr', target: 'commit', animated: true, style: { stroke: '#6b7280' } },
      { id: 'e-pr-files', source: 'pr', target: 'files', animated: true, style: { stroke: '#6b7280' } },
      { id: 'e-commit-ci', source: 'commit', target: 'ci', animated: true, style: { stroke: '#6b7280' } },
      { id: 'e-ci-incident', source: 'ci', target: 'incident', animated: true, style: { stroke: '#ef4444', strokeWidth: 2 } },
      { id: 'e-files-incident', source: 'files', target: 'incident', animated: false, style: { stroke: '#374151', strokeDasharray: '5 5' } },
    ];

    setNodes(newNodes);
    setEdges(newEdges);
  }, [data, setNodes, setEdges]);

  if (!data) return (
    <div className="bg-[#111827] border border-gray-800 rounded-xl p-5 flex items-center justify-center h-[500px]">
      <p className="text-gray-500">No relationship data available</p>
    </div>
  );

  return (
    <div className="bg-[#111827] border border-gray-800 rounded-xl p-5" style={{ height: '500px' }}>
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="font-semibold text-white">Incident Memory Graph</h3>
          <p className="text-sm text-gray-400">Interactive PR → Commit → Author → Failure relationship trace.</p>
        </div>
      </div>
      <div className="h-[400px] border border-gray-800 rounded-lg overflow-hidden bg-[#030712]">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          fitView
          attributionPosition="bottom-right"
        >
          <Controls className="bg-gray-800 fill-white text-black!" />
          <MiniMap className="bg-gray-900" maskColor="rgba(0, 0, 0, 0.7)" nodeColor="#374151" />
          <Background color="#1f2937" gap={16} />
        </ReactFlow>
      </div>
    </div>
  );
}
