export default function ScoreCard({score,risk}:{score:number;risk:string}){return <div className='card'><h2>Score: {score}/100</h2><p>{risk}</p></div>}
