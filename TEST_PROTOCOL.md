# 🧪 Protocole de Test - Wavestone Local AI Workbench

Ce document détaille les tests standardisés à effectuer pour évaluer les performances des modèles SLM (Granite, Llama, Qwen, Ministral) sur les différents cas d'usage implémentés dans l'application.

---

## 🏢 Onglet 1 : Ops Entreprise

### Test A : Triage & Classification d'Email
**Objectif :** Vérifier la capacité du modèle à produire un JSON structuré valide et à détecter l'urgence.
**Modèle Recommandé :** `Granite 1B` (Très strict sur le format) ou `Llama 3.2`.

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
Le modèle doit sortir un JSON strict (pas de phrase avant/après).
* **Category :** Support / Incident
* **Urgency :** High
* **Sentiment :** Negative

### Test B : Anonymisation (PII)
**Objectif :** Tester le respect de la RGPD (suppression des noms/emails).
**Modèle Recommandé :** `Granite 1B` ou `Ministral Instruct`.

**🟢 DONNÉES À COPIER (Input) :**
```text
Le rapport a été validé par Mme Sophie Martin (sophie.martin@client-bancaire.fr) le 12/05/2024 lors de la réunion à La Défense. M. Thomas Durand (t.durand@wavestone.com) sera en charge de l'implémentation technique à partir du lundi 20 mai.
```

**🔴 RÉSULTAT ATTENDU :**
Le texte doit être lisible mais les données sensibles remplacées.
* "Sophie Martin" -> `<PERSON>`
* Emails -> `<EMAIL>`
* Dates -> `<DATE>`

---

## 🤖 Onglet 2 : IoT & JSON (Function Calling)

**Objectif :** Vérifier si le modèle "comprend" les outils virtuels disponibles et mappe le langage naturel vers des arguments de fonction.
**Modèle Recommandé :** `Llama 3.2 1B` ou `Qwen 2.5`.

**🟢 DONNÉES À COPIER (Input) :**
```text
Il fait trop chaud dans la salle de réunion principale. Baisse la température à 19 degrés et passe la ventilation en mode silencieux.
```

**🔴 RÉSULTAT ATTENDU :**
JSON pur correspondant à la signature de l'outil `set_hvac`.
```json
{
  "function": "set_hvac",
  "args": {
    "location": "salle de réunion principale",
    "temperature": 19,
    "mode": "silencieux"
  }
}
```

---

## 📝 Onglet 3 : Synthèse & Rédac

### Test A : Micro-Summarization
**Objectif :** Tester la capacité de compression extrême (utile pour les vues mobiles ou objets de mail).
**Modèle Recommandé :** `Ministral Instruct` ou `Llama 3.2`.
**Réglage :** Sélectionner l'option radio *Micro-Résumé*.

**🟢 DONNÉES À COPIER (Input) :**
```text
L'intelligence artificielle générative (GenAI) transforme rapidement le paysage technologique. Bien que ses capacités à créer du contenu, du code et des images soient impressionnantes, elles soulèvent également des questions importantes concernant la sécurité des données, la propriété intellectuelle et la consommation énergétique. Les entreprises doivent donc adopter une approche gouvernée, en mettant en place des garde-fous éthiques et techniques, pour tirer parti de cette innovation sans compromettre leur intégrité ou leurs secrets d'affaires. Wavestone accompagne ses clients dans cette transition sécurisée.
```

**🔴 RÉSULTAT ATTENDU :**
Une phrase unique ou moins de 10 mots.
* *Exemple :* "Adoption gouvernée de la GenAI nécessaire pour sécuriser l'innovation en entreprise."

---

## 💻 Onglet 4 : Code

**Objectif :** Générer un script fonctionnel sans "bavardage" (chatting).
**Modèle Recommandé :** `Granite 1B` (C'est sa spécialité) ou `Qwen 2.5`.

**🟢 DONNÉES À COPIER (Input) :**
*Langage : Python*
```text
Écris une fonction qui prend en entrée un fichier CSV 'data.csv', lit la colonne 'price', calcule la moyenne, et l'écrit dans un nouveau fichier 'result.txt'. Gère les erreurs si le fichier n'existe pas.
```

**🔴 RÉSULTAT ATTENDU :**
Un code Python propre, avec imports (`csv` ou `pandas`), bloc `try/except` et commentaires. Pas de texte d'intro du type "Voici votre code".

---

## 🧠 Onglet 5 : Logique (Reasoning)

**Objectif :** Piéger le modèle pour voir s'il "réfléchit" avant de répondre (Chain of Thought).
**Modèle Recommandé :** `Ministral Reasoning` (Obligatoire) ou `Qwen 2.5`.

**🟢 TEST 1 : Le problème de la chemise (Logique simple)**
```text
Si il faut 1 heure pour faire sécher une chemise au soleil, combien de temps faut-il pour faire sécher 5 chemises mises au soleil en même temps ?
```
* *Réponse attendue :* 1 heure (et non 5 heures).

**🟢 TEST 2 : Le problème "Strawberry" (Tokenization)**
```text
Combien de fois la lettre "r" apparaît-elle dans le mot "strawberry" ? Réfléchis étape par étape.
```
* *Réponse attendue :* 3. (Beaucoup de petits modèles répondent 2 car ils voient le token "straw" + "berry").
* *Note :* Avec Ministral Reasoning, vérifiez la présence des balises `<thinking>` ou du processus de pensée explicite.