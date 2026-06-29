import os
import joblib
import pandas as pd

IA_MODEL_PATH = "app/services/IA/outputs/model_final.joblib"
IA_SCALER_PATH = "app/services/IA/outputs/scaler.joblib"


def predict_emission(distance: int) -> float:
    """
    Prédit l'émission CO₂ (kg) d'un trip via le modèle IA du dossier services/IA.
    """
    # Essayer de charger le modèle et scaler du dossier IA
    try:
        if not os.path.exists(IA_MODEL_PATH) or not os.path.exists(IA_SCALER_PATH):
            raise FileNotFoundError(f"Modèles IA non trouvés aux chemins: {IA_MODEL_PATH}, {IA_SCALER_PATH}")
        
        model = joblib.load(IA_MODEL_PATH)
        scaler = joblib.load(IA_SCALER_PATH)
        
        # Préparation des données (le modèle IA utilise seulement la distance)
        X = pd.DataFrame([[distance]], columns=["distance"])
        
        # Normalisation
        X_scaled = scaler.transform(X)
        
        # Prédiction
        prediction = model.predict(X_scaled)[0]
        
        # Éviter les valeurs négatives
        prediction = max(0, prediction)
        
        return round(float(prediction), 2)
        
    except FileNotFoundError as e:
        # Fallback : si le modèle IA n'existe pas, utiliser l'estimation ADEME
        print(f"⚠️  Modèle IA non disponible: {e}")
        print(f"   Utilisation de l'estimation ADEME par défaut")
        return round((distance or 0) * 0.00369, 4)
    except Exception as e:
        print(f"❌ Erreur lors de la prédiction: {e}")
        # Fallback ADEME en cas d'erreur
        return round((distance or 0) * 0.00369, 4)