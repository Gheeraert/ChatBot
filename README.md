# Chatbot LM Studio avec Tkinter et Synthèse Vocale (SAPI5)

Ce projet est une interface graphique **Python/Tkinter** permettant d'interagir avec un modèle de langage exécuté **en local** dans [LM Studio](https://lmstudio.ai/) via son **API compatible OpenAI**.  
L’application affiche l’analyse et la réponse du modèle, puis lit la **réponse finale** à voix haute grâce à la synthèse vocale **SAPI5** (Windows) via `pyttsx3`.

---

## ✨ Fonctionnalités
- Interface graphique **Tkinter** simple et compacte.
- Envoi d’un prompt à LM Studio et récupération de la réponse.
- Affichage formaté :
  - **Analyse** (canal `analysis`) : bleu *italique*.
  - **Réponse finale** (canal `final`) : **gras**.
- Lecture vocale discrète de la réponse via **SAPI5** (aucun lecteur multimédia externe).

---

## 📦 Prérequis

### Logiciels
1. **LM Studio** installé : <https://lmstudio.ai/>
2. **Modèle** téléchargé et chargé dans LM Studio, par ex. : `gpt-oss-20-b`  
   > Vous pouvez bien sûr utiliser un autre modèle, mais mettez son identifiant exact dans le code.
3. **Serveur API OpenAI-compatible** démarré dans LM Studio :  
   Menu **Developer** → **OpenAI Compatible REST API Server** → **Start**  
   L’API est accessible (par défaut) à :
   ```
   http://127.0.0.1:1234/v1
   ```

### Python
- **Python 3.9+** (Tkinter est livré avec Python sur Windows/macOS).
- Dépendances :
  ```bash
  pip install openai pyttsx3
  ```
  > Sur certaines distributions Linux, il peut être nécessaire d’installer `python3-tk` via le gestionnaire de paquets (ex. `sudo apt install python3-tk`).

---

## 🚀 Utilisation

1. **Lancer LM Studio**, charger le modèle `gpt-oss-20-b` (ou autre), puis démarrer le serveur API.
2. **Exécuter** le script Python (ex. `chatbot_lmstudio.py`).  
3. Dans l’interface :
   - Saisir votre prompt.
   - Cliquer sur **Envoyer**.
   - Lire l’**analyse** (bleu italique) et la **réponse finale** (gras).
   - Écouter la lecture vocale de la réponse.

---

## 🧩 Extrait de code (configuration principale)

```python
from openai import OpenAI

# Client LM Studio (serveur local OpenAI-compatible)
client = OpenAI(base_url="http://127.0.0.1:1234/v1", api_key="lm-studio")

# Appel /v1/completions
completion = client.completions.create(
    model="gpt-oss-20-b",     # Identifiant du modèle chargé dans LM Studio
    prompt=prompt,            # Texte saisi dans l'UI
    temperature=0.7,
    max_tokens=150
)
response = completion.choices[0].text
```

> **Note** : le code du projet filtre la sortie pour afficher uniquement :
> - le texte qui suit la **première** balise `<|message|>` jusqu’à `<|end|>` (canal `analysis`),
> - puis le texte qui suit la **seconde** balise `<|message|>` jusqu’à **la fin** (canal `final`).

---

## ⚙️ Personnalisation utile

- **Changer de modèle** : modifiez `model="gpt-oss-20-b"`.
- **Voix SAPI5** : dans `text_to_speech`, essayez une autre voix :
  ```python
  voices = engine.getProperty('voices')
  engine.setProperty('voice', voices[1].id)  # tester d'autres index
  ```
- **Vitesse/volume** :
  ```python
  engine.setProperty('rate', 150)
  engine.setProperty('volume', 1.0)
  ```

---

## 🛠️ Dépannage

- **La fenêtre ne s’ouvre pas** : vérifiez que `fenetre.mainloop()` est bien appelé et que Tkinter est disponible.
- **Pas de son** : assurez-vous que SAPI5 fonctionne (Windows), essayez un autre index de voix.
- **Erreur connexion** : confirmez que LM Studio écoute bien sur `http://127.0.0.1:1234/v1` et que le modèle est chargé.
- **Réponse vide** : selon le modèle, le format des balises peut varier. Adaptez l’extraction par expressions régulières au besoin.

---

## 📄 Licence
Projet fourni à des fins pédagogiques et personnelles. Vous pouvez l’adapter librement dans vos projets.
