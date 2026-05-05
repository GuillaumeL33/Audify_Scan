import type { Finding, Severity } from '../types';
export default function FindingsTable({rows,onSelect,filter}:{rows:Finding[];onSelect:(f:Finding)=>void;filter:Severity|'All'}){
 const data=filter==='All'?rows:rows.filter(r=>r.severity===filter);
 return <table><thead><tr><th>Severity</th><th>Title</th><th>File</th><th>Line</th></tr></thead><tbody>{data.map((f,i)=><tr key={i} onClick={()=>onSelect(f)}><td>{f.severity}</td><td>{f.title}</td><td>{f.file}</td><td>{f.line}</td></tr>)}</tbody></table>
}
