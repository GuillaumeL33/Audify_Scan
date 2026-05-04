export default function ScanButton({onClick,loading}:{onClick:()=>void;loading:boolean}){return <button onClick={onClick} disabled={loading}>{loading?'Audit en cours...':'Lancer l\'audit'}</button>}
