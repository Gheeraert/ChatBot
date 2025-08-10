import tkinter as tk
import threading
import re
import pyttsx3
import speech_recognition as sr
from openai import OpenAI

# ==============================
# Configuration client LM Studio
# ==============================
client = OpenAI(base_url="http://127.0.0.1:1234/v1", api_key="lm-studio")

# ==============================
# UI + Reconnaissance vocale
# ==============================
r = sr.Recognizer()
r.energy_threshold = 300     # seuil bruit ambiant
r.pause_threshold = 0.6      # silence => fin de phrase

def ecouter_micro():
    """Écoute le micro, transcrit en FR, remplit le prompt et envoie."""
    try:
        text_response.delete(1.0, tk.END)
        text_response.insert(tk.END, "🎤 J'écoute... Parlez !\n")
        with sr.Microphone() as source:
            # auto-ajustement au bruit ambiant
            r.adjust_for_ambient_noise(source, duration=0.6)
            audio = r.listen(source)

        try:
            texte = r.recognize_google(audio, language="fr-FR")
            entry_prompt.delete(0, tk.END)
            entry_prompt.insert(0, texte)
            obtenir_reponse()
        except sr.UnknownValueError:
            text_response.insert(tk.END, "🤷 Impossible de comprendre l'audio.\n")
        except sr.RequestError as e:
            text_response.insert(tk.END, f"🌐 Erreur du service de reconnaissance : {e}\n")
    except Exception as e:
        text_response.insert(tk.END, f"Erreur micro : {e}\n")

def lancer_ecoute():
    """Lance l'écoute micro dans un thread pour ne pas bloquer Tkinter."""
    threading.Thread(target=ecouter_micro, daemon=True).start()

# ==============================
# Appel LM Studio + TTS
# ==============================
def obtenir_reponse():
    prompt = entry_prompt.get()
    if prompt.strip() == "":
        text_response.delete(1.0, tk.END)
        text_response.insert(tk.END, "Veuillez entrer un prompt.")
        return

    try:
        completion = client.completions.create(
            model="gpt-oss-20-b",   # modèle chargé dans LM Studio
            prompt=prompt,
            temperature=0.7,
            max_tokens=150
        )

        # Réponse brute (debug)
        response = completion.choices[0].text
        print("Réponse brute du modèle :")
        print(response)

        # Extraction des channels
        messages = extraire_messages(response)

        # Affichage formaté
        text_response.delete(1.0, tk.END)
        if 'analysis' in messages and messages['analysis']:
            text_response.insert(tk.END, "Analyse: ", 'blue_italic')
            text_response.insert(tk.END, messages['analysis'], 'blue_italic')
            text_response.insert(tk.END, "\n")

        if 'final' in messages and messages['final']:
            text_response.insert(tk.END, "Réponse Finale: ", 'bold')
            text_response.insert(tk.END, messages['final'], 'bold')
            text_response.insert(tk.END, "\n")
            text_to_speech(messages['final'])  # Lecture vocale discrète

    except Exception as e:
        text_response.delete(1.0, tk.END)
        text_response.insert(tk.END, f"Erreur: {str(e)}")

def extraire_messages(response: str):
    """
    1) texte après le 1er <|message|> jusqu’à <|end|>  -> analysis
    2) texte après le 2e <|message|> jusqu’à la fin    -> final
    """
    messages = {'analysis': '', 'final': ''}

    # 1) Analysis : <|channel|>analysis<|message|> ... <|end|>
    analysis_pattern = r'<\|channel\|>analysis<\|message\|>(.*?)<\|end\|>'
    m1 = re.search(analysis_pattern, response, re.DOTALL)
    if m1:
        messages['analysis'] = m1.group(1).strip()

    # 2) Final : <|channel|>final<\|message\|> ... (jusqu’à la fin)
    final_pattern = r'<\|channel\|>final<\|message\|>(.*?)$'
    m2 = re.search(final_pattern, response, re.DOTALL)
    if m2:
        messages['final'] = m2.group(1).strip()

    return messages

def text_to_speech(text: str):
    """Synthèse vocale SAPI5 locale et discrète via pyttsx3."""
    try:
        engine = pyttsx3.init()
        # Personnalisation (optionnelle)
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 1.0)
        # Choix voix (optionnel) :
        # voices = engine.getProperty('voices'); engine.setProperty('voice', voices[0].id)
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        # On n'interrompt pas l'UI si TTS échoue
        print("Erreur TTS:", e)

# ==============================
# Interface Tkinter
# ==============================
fenetre = tk.Tk()
fenetre.title("Chatbot LM Studio")

label_prompt = tk.Label(fenetre, text="Entrez votre prompt:")
label_prompt.pack(pady=10)

entry_prompt = tk.Entry(fenetre, width=50)
entry_prompt.pack(pady=5)

button_submit = tk.Button(fenetre, text="Envoyer", command=obtenir_reponse)
button_submit.pack(pady=10)

# Bouton micro (Option A – en ligne)
button_mic = tk.Button(fenetre, text="🎤 Parler", command=lancer_ecoute)
button_mic.pack(pady=5)

label_response = tk.Label(fenetre, text="Réponse du modèle:")
label_response.pack(pady=10)

text_response = tk.Text(fenetre, width=60, height=12, wrap=tk.WORD)
text_response.pack(pady=5)

# Styles
text_response.tag_configure('blue_italic', foreground='blue', font=('Helvetica', 12, 'italic'))
text_response.tag_configure('bold', font=('Helvetica', 12, 'bold'))

fenetre.mainloop()
