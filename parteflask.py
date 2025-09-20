#### Salvataggio immagine sul db

import base64
import io
from datetime import datetime

# converto l'immagine in base64 per poterla salvare su mongodb
def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str



# funzione per salvare la predizione sul db
def salva_predizione(nome_tab, image, prediction, utente, filename):
    img_base64 = image_to_base64(image)
    document = {
        "filename": filename,
        "image": img_base64,
        "prediction": prediction,
        "utente": utente,
        "timestamp": datetime.now()
    }
    id = nome_tab.insert_one(document) # salviamo all'interno della tabella
    return id.inserted_id


from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from PIL import Image
import io
import numpy as np
from tensorflow.keras.models import load_model as keras_load_model



app = Flask(__name__)
app.secret_key = "chiave_segreta"
modello = keras_load_model("best_model.h5")


# operazioni di preprocessing sull'immagine caricata dall'utente
def preprocess_image(image):
    image = image.convert("RGB")            # converte in RGB
    image = image.resize((128, 128))        # adatto alle dimensioni richieste modello
    image = np.array(image)/255.0           # normalizzazione 0, 1
    image = np.expand_dims(image, axis=0)   # trasformo l'immagine in un batch di 1 immagine 
    return image


classi=['Carta', 'Indifferenziato', 'Organico', 'Plastica', 'Vetro']

# funzione che fa la predizione dell'immagine
def predict(model, image):
    pred = model.predict(image)                 # contiene le prob. di appartenere a ciascuna classe
    predicted_class = int(np.argmax(pred))      # indice della classe con probabilità + alta
    nome_classe_prevista = classi[predicted_class] 
    return f"Il rifiuto è di tipo: {nome_classe_prevista}"



#################################################################


from connessione_db import utenti, tab_predizioni

######### Route 

@app.route("/previsioni_immagini", methods=["POST"])
def predict_image():
    
    if 'image' not in request.files: # contiene file inviati dal client 
        return jsonify({"error": "Nessun immagine inviata"}), 400
    
    file = request.files["image"]

    try:
        image = Image.open(file.stream) # per leggerlo
        immagine = preprocess_image(image) # preprocesso l'immagine
        prediction = predict(modello, immagine) # faccio la previsione
        email_utente = session.get("email_utente","anonimo")
        doc_id = salva_predizione(tab_predizioni, image, prediction, email_utente, file.filename) # salvo la previsione sul db
        storico = list(tab_predizioni.find({"utente": email_utente}).sort("timestamp", -1))
        # con find recupero dal db tutte le predizioni fatte dall'utente loggato. Ordino in base al timestamp dal + recente
        return render_template("risultato.html", prediction=prediction, doc_id=doc_id, storico=storico)
    except Exception as e:
         return jsonify({"Errore": "Sollevata eccezione"}), 400



from werkzeug.security import generate_password_hash, check_password_hash

@app.route("/", methods=["POST","GET"]) # homepage
def login():
    
    if request.method=="POST":
        email=request.form["email"]
        password=request.form["password"] 
        utente=utenti.find_one({"email": email}) # utente è un dizionario 
        if utente and check_password_hash(utente["password"], password):
            session["email_utente"] = utente["email"] # salvo l'email dell'utente nel dizionario session così da mantenerlo tra le pagine
            return redirect(url_for("caricamento")) # nome della funzione nella route
        else:
            return "Errore: utente non esistente o password errata"
     # checkpassword hash confronta la pwd criptata salvata nel db con quella inserita dall'utente a cui viene rifatta il calcolo dell'hashing

    return render_template("index.html", show_login=True)




@app.route("/registrazione", methods=["GET","POST"])
def registrazione():
    
    if request.method=="POST":
        email=request.form["email"]
        password=request.form["password"]
        pw_criptata = generate_password_hash(password)

        if utenti.find_one({"email": email}): # verifico se esiste già 
            return "Errore: utente già registrato"
        else:  # se non esiste lo inserisco
            utenti.insert_one({
            "email": email,
            "password": pw_criptata  
        })  
        
        return redirect(url_for("login")) # riporto l'utente alla pagina di login (nome della funzione nella route)

    return render_template("index.html", show_login=False)


@app.route("/caricamento")
def caricamento():
    return render_template("caricamento_immagine.html")




if __name__ == "__main__":
    app.run(debug=True)
