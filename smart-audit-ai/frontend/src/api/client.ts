import type { ScanResult } from '../types';
const API = 'http://localhost:8000';
export async function createScan(code:string, files:File[]){
  const fd=new FormData(); if(code.trim()) fd.append('code', code); files.forEach(f=>fd.append('files',f));
  const r=await fetch(`${API}/api/scans`,{method:'POST',body:fd}); if(!r.ok) throw new Error(await r.text()); return r.json();
}
export async function getScan(id:number):Promise<ScanResult>{ const r=await fetch(`${API}/api/scans/${id}`); if(!r.ok) throw new Error(await r.text()); return r.json(); }
