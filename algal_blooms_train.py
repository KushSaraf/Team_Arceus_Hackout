import pandas as pd #type: ignore
import os
import joblib #type: ignore
import json
import matplotlib.pyplot as plt #type: ignore
import seaborn as sns #type: ignore
from sklearn.ensemble import RandomForestClassifier #type: ignore
from sklearn.model_selection import train_test_split #type: ignore
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report, confusion_matrix #type: ignore

class AlgalBloomsModel:

    def __init__(self, csv_path):
        self.model = None
        # read with low_memory disabled
        self.data = pd.read_csv(csv_path, low_memory=False)

        # make sure artifacts folder exists
        os.makedirs("artifacts/algal_blooms", exist_ok=True)

        self.clean_and_extract_features()

    def clean_and_extract_features(self):
        # force numeric conversion on key columns
        for col in ["CELLCOUNT", "SALINITY", "WATER_TEMP", "WIND_SPEED"]:
            self.data[col] = pd.to_numeric(self.data[col], errors="coerce")

        # drop rows with missing essential values
        self.data = self.data.dropna(subset=["CELLCOUNT", "LATITUDE", "LONGITUDE", "SALINITY", "WATER_TEMP", "WIND_SPEED"])

        # derive bloom label
        self.data["Bloom"] = (self.data["CELLCOUNT"] >= 20000).astype(int)

        # process date
        self.data["SAMPLE_DATE"] = pd.to_datetime(self.data["SAMPLE_DATE"], errors="coerce")
        self.data = self.data.dropna(subset=["SAMPLE_DATE"])
        self.data["Month"] = self.data["SAMPLE_DATE"].dt.month
        self.data["Year"] = self.data["SAMPLE_DATE"].dt.year

    def train_model(self):
        features = ["LATITUDE", "LONGITUDE", "SALINITY", "WATER_TEMP", "WIND_SPEED", "Month"]
        X = self.data[features]
        y = self.data["Bloom"]

        self.model = RandomForestClassifier(n_estimators=300, class_weight="balanced", random_state=42)

        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        self.model.fit(X_train, y_train)

        # Predict on test set
        y_pred = self.model.predict(X_test)

        # Save confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        plt.figure(figsize=(6, 4))
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                    xticklabels=["No Bloom", "Bloom"],
                    yticklabels=["No Bloom", "Bloom"])
        plt.xlabel("Predicted")
        plt.ylabel("Actual")
        plt.title("Confusion Matrix - Algal Bloom Model")
        plt.savefig("artifacts/algal_blooms/confusion_matrix.png")
        plt.close()

        # Save metrics as JSON
        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred),
            "recall": recall_score(y_test, y_pred),
            "f1_score": f1_score(y_test, y_pred),
            "report": classification_report(y_test, y_pred, output_dict=True)
        }
        with open("artifacts/algal_blooms/metrics.json", "w") as f:
            json.dump(metrics, f, indent=4)

        print("✅ Training done. Artifacts saved in /artifacts/algal_blooms folder.")

    def save_model(self, path="models/algal_bloom_rf.pkl"):
        os.makedirs("models", exist_ok=True)
        if self.model is not None:
            joblib.dump(self.model, path)
            print(f"✅ Model saved at {path}")


def main():
    algal_bloom_model = AlgalBloomsModel("data/algal_bloom.csv")
    algal_bloom_model.train_model()
    algal_bloom_model.save_model("models/algal_bloom_rf.pkl")

if __name__ == "__main__":
    main()
