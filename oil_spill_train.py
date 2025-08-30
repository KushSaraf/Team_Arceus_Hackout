import pandas as pd #type: ignore
from sklearn.ensemble import RandomForestClassifier #type: ignore
from sklearn.model_selection import train_test_split #type: ignore
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, precision_score, recall_score, f1_score #type: ignore
import joblib #type: ignore
import matplotlib.pyplot as plt #type: ignore
import seaborn as sns #type: ignore
import json
import os

class OilSpillModel:

    def __init__(self, csv_path):

        self.model = None
        self.data = pd.read_csv(csv_path)
        # make sure artifacts folder exists
        os.makedirs("artifacts/oil_spill", exist_ok=True)

    def train_model(self):

        self.model = RandomForestClassifier(n_estimators=300, class_weight="balanced", random_state=42)

        # Split features and labels
        X = self.data.drop("target", axis=1)
        y = self.data["target"]

        # Train-test split (80% train, 20% test)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        self.model.fit(X_train, y_train)

        # Predict on test set
        y_pred = self.model.predict(X_test)

        # Save confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        plt.figure(figsize=(6, 4))
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=["No Spill", "Spill"], yticklabels=["No Spill", "Spill"])
        plt.xlabel("Predicted")
        plt.ylabel("Actual")
        plt.title("Confusion Matrix - Oil Spill Model")
        plt.savefig("artifacts/oil_spill/confusion_matrix.png")
        plt.close()

        # Save metrics as JSON
        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred),
            "recall": recall_score(y_test, y_pred),
            "f1_score": f1_score(y_test, y_pred),
            "report": classification_report(y_test, y_pred, output_dict=True)
        }
        with open("artifacts/oil_spill/metrics.json", "w") as f:
            json.dump(metrics, f, indent=4)

        print("✅ Training done. Artifacts saved in /artifacts/oil_spill folder.")

    def save_model(self, path="models/oil_spill_rf.pkl"):

        os.makedirs("models", exist_ok=True)
        if self.model is not None:
            joblib.dump(self.model, path)
            print(f"✅ Model saved at {path}")

    def show_feature_importance(self):
        
        if self.model is None:
            print("Train the model first!")
            return
        importances = self.model.feature_importances_
        features = self.data.drop("target", axis=1).columns
        plt.figure(figsize=(10,6))
        plt.barh(features, importances)
        plt.xlabel("Importance")
        plt.title("Feature Importance in Oil Spill Detection")
        plt.show()

def main():
    oil_spill_model = OilSpillModel("data/oil_spill.csv")
    oil_spill_model.train_model()
    oil_spill_model.save_model("models/oil_spill_rf.pkl")

if __name__ == "__main__":
    main()
