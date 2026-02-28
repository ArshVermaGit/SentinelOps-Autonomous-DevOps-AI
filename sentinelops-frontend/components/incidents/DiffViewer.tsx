"use client"

interface DiffViewerProps {
  diff: string
}

export default function DiffViewer({ diff }: DiffViewerProps) {
  const lines = diff.split("\n")
  
  return (
    <div className="font-mono text-xs bg-gray-950 rounded-lg overflow-auto max-h-64 border border-gray-800">
      <table className="w-full border-collapse">
        <tbody>
          {lines.map((line, i) => {
            let bg = ""
            let text = "text-gray-400"
            
            if (line.startsWith("+") && !line.startsWith("+++")) {
              bg = "bg-emerald-900/30"
              text = "text-emerald-400"
            } else if (line.startsWith("-") && !line.startsWith("---")) {
              bg = "bg-red-900/30"
              text = "text-red-400"
            } else if (line.startsWith("@@")) {
              bg = "bg-indigo-900/20"
              text = "text-indigo-400"
            } else if (line.startsWith("---") || line.startsWith("+++")) {
              text = "text-gray-500"
            }
            
            return (
              <tr key={i} className={bg}>
                <td className="w-8 text-gray-700 text-right pr-3 py-0.5 select-none border-r border-gray-800 pl-2">
                  {i + 1}
                </td>
                <td className={`pl-4 py-0.5 ${text} whitespace-pre`}>
                  {line || " "}
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
