# Smart Audit AI

SaaS local d'audit IA pour smart contracts Solidity (analyse statique + Slither optionnel + Claude optionnel), scoring sécurité et rapport complet.

## Structure
- `backend/` FastAPI + SQLite + moteur d'analyse
- `frontend/` React + TypeScript + Vite

## Installation rapide
```bash
cd smart-audit-ai/backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

```bash
cd smart-audit-ai/frontend
npm install
npm run dev
```

## Exemple de contrat vulnérable
```solidity
pragma solidity ^0.8.0;
contract VulnerableBank {
    mapping(address => uint256) public balances;
    address public owner = 0x1111111111111111111111111111111111111111;

    function deposit() external payable { balances[msg.sender] += msg.value; }
    function withdraw(uint256 amount) external {
        require(balances[msg.sender] >= amount);
        (bool ok,) = msg.sender.call{value: amount}("");
        require(ok);
        balances[msg.sender] -= amount;
    }
    function insecureAuth() external view returns(bool){ return tx.origin == owner; }
}
```

Collez ce contrat dans la WebApp puis cliquez **Lancer l'audit**.
