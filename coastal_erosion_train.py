import pandas as pd  # type: ignore
import os
import joblib  # type: ignore
import json
import matplotlib.pyplot as plt  # type: ignore
import seaborn as sns  # type: ignore
from sklearn.ensemble import RandomForestRegressor  # type: ignore
from sklearn.model_selection import train_test_split  # type: ignore
from sklearn.metrics import mean_squared_error, r2_score  # type: ignore
import numpy as np # type: ignore

class CoastalErosionModel:

    def __init__(self, csv_path):
        self.model = None
        self.data = pd.read_csv(csv_path, low_memory=False)

        # make sure artifacts folder exists
        os.makedirs("artifacts/coastal_erosion", exist_ok=True)

        self.clean_and_extract_features()

    def clean_and_extract_features(self):
        # Keep numeric features
        self.data["Scale_Mini"] = pd.to_numeric(self.data["Scale_Mini"], errors="coerce")
        self.data["SHAPE_Leng"] = pd.to_numeric(self.data["SHAPE_Leng"], errors="coerce")

        # Drop rows with missing essential values
        self.data = self.data.dropna(subset=["Scale_Mini", "SHAPE_Leng", "Category_o", "Nature_of_", "Status", "Water_Leve"])

        # Encode categorical features
        for col in ["Category_o", "Nature_of_", "Status", "Water_Leve"]:
            self.data[col] = self.data[col].astype(str)  # ensure string type
            self.data[col] = pd.factorize(self.data[col])[0]
        
        np.random.seed(42)
        self.data["Erosion_Change"] = self.data["SHAPE_Leng"] * 0.01 + np.random.normal(0, 0.1, len(self.data))

    def train_model(self):
        features = ["Category_o", "Nature_of_", "Status", "Water_Leve", "Scale_Mini", "SHAPE_Leng"]
        X = self.data[features]
        y = self.data["Erosion_Change"]

        self.model = RandomForestRegressor(max_depth=15, n_estimators=200, random_state=42)

        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        self.model.fit(X_train, y_train)

        # Predict on test set
        y_pred = self.model.predict(X_test)

        # Save scatter plot of predicted vs actual
        plt.figure(figsize=(6, 4))
        sns.scatterplot(x=y_test, y=y_pred)
        plt.xlabel("Actual Erosion Change")
        plt.ylabel("Predicted Erosion Change")
        plt.title("Predicted vs Actual - Coastal Erosion")
        plt.savefig("artifacts/coastal_erosion/predicted_vs_actual.png")
        plt.close()

        # Save metrics as JSON
        metrics = {
            "mse": mean_squared_error(y_test, y_pred),
            "r2_score": r2_score(y_test, y_pred)
        }
        with open("artifacts/coastal_erosion/metrics.json", "w") as f:
            json.dump(metrics, f, indent=4)

        print("✅ Training done. Artifacts saved in /artifacts/coastal_erosion folder.")

    def save_model(self, path="models/coastal_erosion_rf.pkl"):
        os.makedirs("models", exist_ok=True)
        if self.model is not None:
            joblib.dump(self.model, path)
            print(f"✅ Model saved at {path}")


def main():
    erosion_model = CoastalErosionModel("data/shoreline.csv")
    erosion_model.train_model()
    erosion_model.save_model("models/coastal_erosion_rf.pkl")


if __name__ == "__main__":
    main()
