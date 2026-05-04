export default function UploadBox({onFiles}:{onFiles:(f:File[])=>void}){return <input type='file' accept='.sol' multiple onChange={e=>onFiles(Array.from(e.target.files||[]))}/>}
