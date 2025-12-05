# 🧪 Protocole de Test - Wavestone Local AI Workbench (v2025)

Ce document détaille les tests standardisés à effectuer pour évaluer les performances des modèles **Locaux** (Llama 3.2, Qwen 2.5, Gemma 2, Phi-3.5) et **API** (Mistral, Magistral) sur les cas d'usage implémentés.

---

## 🏢 Onglet 1 : Ops Entreprise

### Test A : Triage & Classification d'Email
**Objectif :** Vérifier la capacité à produire un JSON strict et à catégoriser correctement.
**Modèle Recommandé (Local) :** `Qwen 2.5 1.5B` (Très fort en structuré) ou `Llama 3.2 3B`.
**Modèle Recommandé (API) :** `Ministral 3 3B`.

**🟢 DONNÉES À COPIER (Input) :**
```text
Objet : URGENCE - Blocage production - Ticket #9928

Bonjour l'équipe support,

C'est inadmissible. Depuis la mise à jour de ce matin, plus aucun consultant ne peut accéder à la plateforme WaveInsight. Nous avons une livraison client prévue à 14h aujourd'hui.
Si ce n'est pas réglé dans l'heure, nous risquons des pénalités financières.
Merci de faire le nécessaire immédiatement.

Cordialement,
Directeur de Projet.
```

**🔴 RÉSULTAT ATTENDU :**
Le modèle doit sortir un JSON valide (parfois entouré de markdown, mais la structure doit être correcte).
* **Category :** Delivery ou Tech
* **Urgency :** High
* **Sentiment :** Negative

### Test B : Anonymisation (PII)
**Objectif :** Tester la capacité à identifier et remplacer les entités nommées (NER).
**Modèle Recommandé (Local) :** `Phi-3.5 Mini` ou `Llama 3.2 3B`.

**🟢 DONNÉES À COPIER (Input) :**
```text
Le rapport a été validé par Mme Sophie Martin (sophie.martin@client-bancaire.fr) le 12/05/2025 lors de la réunion à La Défense. M. Thomas Durand (t.durand@wavestone.com) sera en charge de l'implémentation technique.
```

**🔴 RÉSULTAT ATTENDU :**
* "Sophie Martin" / "Thomas Durand" -> `[PERSON]`
* Emails -> `[EMAIL]`
* Le reste de la phrase doit rester intelligible.

---

## 🤖 Onglet 2 : IoT & Agentique

**Objectif :** Vérifier si le modèle "comprend" les outils disponibles et mappe la demande vers des arguments JSON (Function Calling simulé).
**Modèle Recommandé (Local) :** `Qwen 2.5 3B` (Excellent en tool use) ou `SmolLM2 1.7B` (Pour tester les limites).

**🟢 DONNÉES À COPIER (Input) :**
```text
Il fait trop chaud dans la salle de réunion principale. Baisse la température à 19 degrés et passe la ventilation en mode silencieux.
```

**🔴 RÉSULTAT ATTENDU :**
JSON correspondant à la signature des outils fictifs.
```json
{
  "tool": "set_ac",
  "args": {
    "room": "salle de réunion principale",
    "temp": 19,
    "mode": "silencieux" // ou state selon l'interprétation du modèle
  }
}
```

---

## 📝 Onglet 3 : Synthèse & RAG

**Objectif :** Tester la capacité de synthèse et le respect des instructions de formatage.
**Modèle Recommandé (Local) :** `Gemma 2 2B` (Très bonne plume) ou `Phi-3.5 Mini` (Concis).
**Modèle Recommandé (API) :** `Mistral Large 3` (Référence).

**🟢 DONNÉES À COPIER (Input) :**
*Uploadez un PDF technique ou copiez ce texte :*
```text
L'intelligence artificielle générative (GenAI) transforme rapidement le paysage technologique. Bien que ses capacités à créer du contenu, du code et des images soient impressionnantes, elles soulèvent également des questions importantes concernant la sécurité des données, la propriété intellectuelle et la consommation énergétique. Les entreprises doivent donc adopter une approche gouvernée, en mettant en place des garde-fous éthiques et techniques. Wavestone accompagne ses clients dans cette transition sécurisée via l'offre "Trusted AI".
```

**🟢 INSTRUCTION (Text Area) :**
```text
Résume ce texte en une seule phrase percutante de moins de 15 mots pour un titre LinkedIn.
```

**🔴 RÉSULTAT ATTENDU :**
Une phrase courte, marketing, mentionnant "Gouvernance", "GenAI" et "Wavestone".

---

## 🌐 Onglet 4 : Traduction

**Objectif :** Vérifier la fluidité linguistique et la préservation du sens technique.
**Modèle Recommandé (Local) :** `Gemma 2 2B` (Multilingue fort) ou `Llama 3.2 3B`.

**🟢 DONNÉES À COPIER (Input) :**
```text
The deployment of Small Language Models directly on edge devices reduces latency and ensures data privacy, as no information leaves the corporate network.
```

**🔴 RÉSULTAT ATTENDU (Cible : Espagnol ou Allemand) :**
Une traduction fluide qui conserve les termes techniques ("Edge devices", "Latency") correctement traduits ou adaptés au contexte pro.

---

## 💻 Onglet 5 : Code

**Objectif :** Générer un script fonctionnel sans "hallucination" de librairies.
**Modèle Recommandé (Local) :** `Qwen 2.5 3B` (Le meilleur codeur local) ou `Phi-3.5`.

**🟢 DONNÉES À COPIER (Input) :**
*Langage : Python*
```text
Écris une fonction qui prend en entrée une liste de prix [10.5, 20.0, 5.5], applique une TVA de 20%, et retourne la liste des prix TTC arrondis à 2 décimales. Utilise une list comprehension.
```

**🔴 RÉSULTAT ATTENDU :**
Code Python valide, utilisant `[round(x * 1.2, 2) for x in prices]`. Pas de blabla inutile.

---

## 🧠 Onglet 6 : Logique (Reasoning)

**Objectif :** Tester le raisonnement étape par étape (CoT).
**Modèle Recommandé (API) :** `Magistral Small` (Modèle de raisonnement dédié).
**Modèle Recommandé (Local) :** `Phi-3.5 Mini` ou `Qwen 2.5 3B`.

**🟢 TEST 1 : Le problème de la chemise (Logique simple)**
```text
S'il faut 1 heure pour faire sécher une chemise au soleil, combien de temps faut-il pour faire sécher 5 chemises mises au soleil en même temps ? Explique ton raisonnement.
```
* *Réponse attendue :* 1 heure (Parallélisme).

**🟢 TEST 2 : Le problème "Strawberry" (Tokenization)**
```text
Combien de fois la lettre "r" apparaît-elle dans le mot "strawberry" ? Réfléchis étape par étape.
```
* *Réponse attendue :* 3.
* *Note :* `Llama 3.2` échoue souvent ici (répond 2). `Magistral` ou `Qwen 2.5` devraient réussir.