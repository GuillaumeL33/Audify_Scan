# 🔐 Audify_Scan — Rapport d'Audit Sécurité Complet
## Protocole : **Bondary**
> Date : 2026-05-04 | Scan ID : `bondary-2026-05-04` | Procédure : Analyse Statique + Claude AI

---

## 📊 Résumé des Scores

| Indicateur | Valeur | Niveau |
|---|---|---|
| **Security Score** | **0 / 100** | 🔴 Critical Risk |
| **Threat Score** | **80 / 100** | 🟠 High Threat |

### Formule Scoring (scoring.py)
```
base = 100
- Critical  × 1  = -20  (weight: 20)
- High      × 2  = -24  (weight: 12)
- Medium    × 6  = -42  (weight: 7)
- Low       × 4  = -12  (weight: 3)
- Info      × 4  = -4   (weight: 1)
- Gas       × 3  = -6   (weight: 2)
─────────────────────────────────
Total déductions  = -108
Security Score    = max(0, 100 - 108) = 0
```

> **Note** : Le scoring Audify_Scan est calibré pour des contrats unitaires. Sur un protocole 5 contrats, le cumul des findings reflète la complexité du système, pas nécessairement un niveau de risque catastrophique sur chaque vecteur individuel.

---

## 📋 Comptage des Findings

| Sévérité | Nombre | Poids/finding | Déduction totale |
|---|---|---|---|
| 🔴 **Critical** | **1** | 20 | 20 |
| 🟠 **High** | **2** | 12 | 24 |
| 🟡 **Medium** | **6** | 7 | 42 |
| 🔵 **Low** | **4** | 3 | 12 |
| ⚪ **Informational** | **4** | 1 | 4 |
| ⛽ **Gas** | **3** | 2 | 6 |
| **TOTAL** | **20** | — | **108** |

---

## 📁 Contrats Scannés

| Fichier | Taille | Findings |
|---|---|---|
| `src/CorporateBond.sol` | 51 850 bytes | 14 |
| `src/BondaryMarketplace.sol` | 14 172 bytes | 3 |
| `src/BondFactory.sol` | 6 305 bytes | 1 |
| `src/ComplianceManager.sol` | 8 413 bytes | 2 |
| `src/BondaryFeeCollector.sol` | 3 090 bytes | 0 |
| `src/interfaces/IERC3643.sol` | 4 848 bytes | 0 |

---

## 🔴 CRITICAL (1 finding)

### C-01 — Double Coupon Claim via `claimAllocation()` en état MATURED
- **Fichier** : `src/CorporateBond.sol` · ligne ~350
- **Catégorie** : Logic / Economic Attack

**Description**  
Quand `claimAllocation()` est appelé en état `MATURED`, la fonction `_update()` **ne déclenche pas** `_accrueCoupon(to)` (condition `state == State.ACTIVE` non satisfaite). Le `_couponCheckpoint[investor]` reste à **0**. La ligne suivante ajoute manuellement les coupons rétroactifs :
```solidity
_pendingCoupons[msg.sender] += (bonds * totalCouponPerToken) / PRECISION;
```
Mais le **checkpoint n'est pas mis à jour**. Quand `claimCoupons()` ou `redeemBonds()` est ensuite appelé, `_accrueCoupon()` recalcule le **même montant** (checkpoint=0, balance=bonds), aboutissant à **2× les coupons dus**.

**Scénario d'exploitation**
1. Investisseur A souscrit 1000 bonds. Ne réclame pas pendant la phase ACTIVE.
2. Plusieurs coupons versés → `totalCouponPerToken = X`
3. `signalMaturity()` → état MATURED
4. A appelle `claimAllocation()` → `_pendingCoupons[A] = 1000 × X / 1e18`, checkpoint reste 0
5. A appelle `claimCoupons()` → `_accrueCoupon` recalcule `earned = 1000 × X / 1e18` (encore)
6. **A reçoit 2× ses coupons dus, drainant le pool des autres investisseurs**

**Fix recommandé**
```solidity
if (terms.paymentMode == PaymentMode.COUPON && totalCouponPerToken > 0) {
    _pendingCoupons[msg.sender] += (bonds * totalCouponPerToken) / PRECISION;
    _couponCheckpoint[msg.sender] = totalCouponPerToken; // ← FIX REQUIS
}
```

---

## 🟠 HIGH (2 findings)

### H-01 — Agent Burn Sans Accrual des Coupons → Perte de Fonds Investisseur
- **Fichier** : `src/CorporateBond.sol` · ligne ~710
- **Catégorie** : Fund Loss / Agent Privilege

`_agentBurnBondTokens()` appelle directement `_decreaseCouponEligibleSupply()` + `_burn()` **sans** appeler `_accrueCoupon(userAddress)`. Tous les coupons accrus et non-réclamés sont **perdus définitivement**. Le chemin utilisateur normal (`redeemBonds()`) appelle `_accrueCoupon()` avant burn.

**Fix** : Ajouter `_accrueCoupon(userAddress)` en tête de `_agentBurnBondTokens()` pour les bonds en mode COUPON.

---

### H-02 — `BondFactory.upgradeImplementation()` Sans Timelock
- **Fichier** : `src/BondFactory.sol` · ligne ~88
- **Catégorie** : Centralization / Upgrade Risk

Contrairement à `CorporateBond` (timelock 48h via `proposeUpgrade`), `BondFactory.upgradeImplementation()` remplace instantanément l'implémentation pour **tous les futurs bonds**. Un admin compromis peut injecter une implémentation malveillante et créer des bonds «officiels» backdoorés.

**Fix** : Implémenter le même pattern `proposeUpgrade` / `executeUpgrade` avec délai 48h minimum.

---

## 🟡 MEDIUM (6 findings)

### M-01 — Agent `mint()` Autorisé en état FAILED
`src/CorporateBond.sol` · ligne ~635  
Le guard `state != MATURED && state != CLOSED` autorise le mint en état FAILED. Tokens non-backés mintables pendant le remboursement des souscripteurs.

### M-02 — `recoveryAddress()` Non-Fonctionnel pour KYC EOA
`src/CorporateBond.sol + ComplianceManager.sol`  
`whitelist(account)` enregistre `IIdentity(account)` = EOA. `recoveryAddress()` appelle `keyHasPurpose()` sur l'EOA → retourne `false` → `require` échoue → récupération impossible pour le flux KYC principal.

### M-03 — Race Condition au Hard Cap → DoS Dernier Investisseur
`src/CorporateBond.sol` · ligne ~270  
Si `bondAmount` est réduit à `remaining`, le `payment` peut être < `minInvestment`. Les dernières positions deviennent impossibles à souscrire. Risque de soft cap non atteint.

### M-04 — Aucune Validation Minimum de `couponFrequency`
`src/CorporateBond.sol` · `initialize()`  
Si `couponFrequency = 0` : `expectedCouponAmount()` = 0, `payCoupon()` revert always, bond COUPON mode non-fonctionnel.

### M-05 — Aucune Limite de Batch dans `ComplianceManager`
`src/ComplianceManager.sol` · ligne ~72  
`batchWhitelist()` et `batchRegisterIdentity()` sans `MAX_BATCH_SIZE`. Potentiel out-of-gas sur grandes listes.

### M-06 — `pause()` Ne Bloque Pas les Rachats/Burns
`src/CorporateBond.sol`  
Le check `!paused()` dans `_update()` ne s'applique qu'aux transferts (from≠0 && to≠0). Burns (to=0) non soumis au check. `redeemBonds()` et `redeemEarly()` restent accessibles en pause.

---

## 🔵 LOW (4 findings)

| ID | Titre | Fichier |
|---|---|---|
| L-01 | `cancelSubscription()` non bloquée par pause (non-documenté) | CorporateBond.sol |
| L-02 | Dépendance `block.timestamp` pour logique financière (acceptable sur horizons longs) | CorporateBond.sol |
| L-03 | `signalMaturity()` appelable par n'importe qui | CorporateBond.sol |
| L-04 | Marketplace non auto-whitelisté dans ComplianceManager (risque déploiement) | BondaryMarketplace.sol |

---

## ⚪ INFORMATIONAL (4 findings)

| ID | Titre | Fichier |
|---|---|---|
| I-01 | `bindToken()` auto-enregistrement par n'importe quel contrat | ComplianceManager.sol |
| I-02 | `deleteIdentity()` échec silencieux dans `recoveryAddress()` | CorporateBond.sol |
| I-03 | Centralisation : admin unique contrôle tous les rôles critiques | Multi-contrats |
| I-04 | `TOKEN_VERSION` constante non mise à jour lors des upgrades UUPS | CorporateBond.sol |

---

## ⛽ GAS (3 findings)

| ID | Titre | Économie estimée |
|---|---|---|
| G-01 | `_accrueCoupon()` : écriture storage inconditionnelle | ~5 000 gas/appel |
| G-02 | `terms` struct relue depuis storage dans chaque fonction | ~200-400 gas/fn |
| G-03 | Batch functions : `.length` lu à chaque itération | Minime |

---

## ✅ Points Positifs

- **SafeERC20** utilisé partout (protection contre tokens non-standards)
- **ReentrancyGuard (nonReentrant)** sur toutes les fonctions critiques
- **AccessControl OpenZeppelin** bien structuré avec séparation des rôles
- **Timelock 48h UUPS** dans CorporateBond (proposeUpgrade / cancelUpgrade)
- **MAX_BATCH_SIZE = 200** dans CorporateBond (protection DoS)
- **Pattern dividend-per-token** correct pour l'accrual des coupons (sauf C-01)
- **Checks-Effects-Interactions** respecté dans claimRefund(), cancelSubscription()
- **Snapshots de frais** dans les ordres Marketplace (protection front-running)
- **ERC-3643 compliance** vérifiée à chaque transfert dans `_update()`
- **__gap[50]** pour protéger le storage lors des upgrades UUPS

---

## 🎯 Priorités de Correction

1. 🔴 **CRITIQUE IMMÉDIAT** : Corriger C-01 (ajouter `_couponCheckpoint[msg.sender] = totalCouponPerToken` dans `claimAllocation()` après l'addition rétroactive)
2. 🟠 **Avant déploiement** : Corriger H-01 (accrual dans agent burn) + H-02 (timelock BondFactory)
3. 🟡 **Avant mainnet** : M-01 (mint FAILED state) + M-02 (recovery EOA) + M-03 (hard cap edge)
4. 🔵 **Post-déploiement** : Correctifs Low + documentation

---

*Rapport généré par Audify_Scan · Analyse Statique + Claude AI · 2026-05-04*
