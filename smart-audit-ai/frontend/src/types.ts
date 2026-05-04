export type Severity = 'Critical'|'High'|'Medium'|'Low'|'Informational';
export interface Finding { title:string; severity:Severity; category?:string; file?:string; line?:number; description:string; impact?:string; exploit_scenario?:string; recommendation?:string; patch_example?:string; status?:string; code_snippet?:string }
export interface ScanResult { id:number; score:number; risk_level:string; summary:string; findings:Finding[] }
