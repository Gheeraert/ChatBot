import tkinter as tk
import pyttsx3
from openai import OpenAI
import re

# Configuration du client LM Studio
client = OpenAI(base_url="http://127.0.0.1:1234/v1", api_key="lm-studio")


# Fonction pour obtenir la réponse du modèle
def obtenir_reponse():
    prompt = entry_prompt.get()  # Récupérer le texte saisi par l'utilisateur
    if prompt.strip() == "":
        text_response.delete(1.0, tk.END)  # Effacer la réponse précédente
        text_response.insert(tk.END, "Veuillez entrer un prompt.")  # Message si pas de prompt
        return

    try:
        # Demande de complétion avec LM Studio
        completion = client.completions.create(
            model="gpt-oss-20-b",  # Remplacer par le modèle que tu utilises
            prompt=prompt,
            temperature=0.7,
            max_tokens=150
        )

        # Récupérer la réponse brute
        response = completion.choices[0].text

        # Imprimer la réponse brute pour débogage
        print("Réponse brute du modèle :")
        print(response)

        # Extraire les messages des channels
        messages = extraire_messages(response)

        # Effacer la réponse précédente dans le champ
        text_response.delete(1.0, tk.END)

        # Afficher l'analyse (en bleu italique)
        if 'analysis' in messages:
            text_response.insert(tk.END, "Analyse: ", 'blue_italic')
            text_response.insert(tk.END, messages['analysis'], 'blue_italic')
            text_response.insert(tk.END, "\n")

        # Afficher la réponse finale (en gras)
        if 'final' in messages:
            text_response.insert(tk.END, "Réponse Finale: ", 'bold')
            text_response.insert(tk.END, messages['final'], 'bold')
            text_response.insert(tk.END, "\n")

        # Convertir la réponse finale en audio avec pyttsx3 (SAPI5)
        if 'final' in messages:
            text_to_speech(messages['final'])

    except Exception as e:
        text_response.delete(1.0, tk.END)
        text_response.insert(tk.END, f"Erreur: {str(e)}")


# Fonction pour extraire les messages des channels
def extraire_messages(response):
    # Initialiser un dictionnaire pour stocker les messages
    messages = {'analysis': '', 'final': ''}

    # Expression régulière pour extraire le texte après <|message|> jusqu'à <|end|> (pour analysis)
    analysis_pattern = r'<\|channel\|>analysis<\|message\|>(.*?)<\|end\|>'
    # Expression régulière pour extraire le texte après <|message|> jusqu'à la fin (pour final)
    final_pattern = r'<\|channel\|>final<\|message\|>(.*?)$'

    # Extraire le message "analysis" (texte après <|message|> jusqu'à <|end|>)
    analysis_message = re.search(analysis_pattern, response, re.DOTALL)
    # Extraire le message "final" (texte après <|message|> jusqu'à la fin)
    final_message = re.search(final_pattern, response, re.DOTALL)

    # Si le message "analysis" est trouvé, l'ajouter au dictionnaire
    if analysis_message:
        messages['analysis'] = analysis_message.group(1).strip()

    # Si le message "final" est trouvé, l'ajouter au dictionnaire
    if final_message:
        messages['final'] = final_message.group(1).strip()

    return messages


# Fonction pour convertir le texte en audio avec pyttsx3 (SAPI5 local et discret)
def text_to_speech(text):
    # Initialiser pyttsx3
    engine = pyttsx3.init()

    # Liste des voix disponibles
    voices = engine.getProperty('voices')

    # Choisir une voix (par exemple, la première voix disponible sur SAPI5)
    engine.setProperty('voice', voices[0].id)  # Tu peux essayer voices[1] pour une voix différente

    # Optionnel : Ajuster la vitesse de la voix (par exemple, 150 mots par minute)
    engine.setProperty('rate', 150)

    # Optionnel : Ajuster le volume de la voix (volume de 0 à 1)
    engine.setProperty('volume', 1)

    # Convertir le texte en parole
    engine.say(text)
    engine.runAndWait()  # Exécuter la parole


# Créer la fenêtre principale
fenetre = tk.Tk()
fenetre.title("Chatbot LM Studio")

# Créer un label pour le prompt
label_prompt = tk.Label(fenetre, text="Entrez votre prompt:")
label_prompt.pack(pady=10)

# Créer une boîte de saisie pour le prompt
entry_prompt = tk.Entry(fenetre, width=50)
entry_prompt.pack(pady=5)

# Créer un bouton pour soumettre le prompt
button_submit = tk.Button(fenetre, text="Envoyer", command=obtenir_reponse)
button_submit.pack(pady=20)

# Créer une boîte de texte pour afficher la réponse (utiliser Text pour le formatage)
label_response = tk.Label(fenetre, text="Réponse du modèle:")
label_response.pack(pady=10)

# Utiliser un widget Text pour afficher avec du formatage
text_response = tk.Text(fenetre, width=60, height=10, wrap=tk.WORD)
text_response.pack(pady=5)

# Ajouter les styles pour le texte
text_response.tag_configure('blue_italic', foreground='blue', font=('Helvetica', 12, 'italic'))
text_response.tag_configure('bold', font=('Helvetica', 12, 'bold'))

# Lancer la boucle principale de l'interface graphique
fenetre.mainloop()
