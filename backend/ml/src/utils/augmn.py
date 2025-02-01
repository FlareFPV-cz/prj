import pandas as pd
import numpy as np
from sklearn.utils import resample
from imblearn.over_sampling import SMOTE

def augment_soil_data(df, n_samples_per_class=100, noise_level=0.05):
    """
    Augments soil data to balance classes and add variability.

    Parameters:
        df (pd.DataFrame): Input DataFrame containing soil data.
        n_samples_per_class (int): Minimum number of samples per class.
        noise_level (float): Standard deviation of Gaussian noise.

    Returns:
        pd.DataFrame: Augmented DataFrame.
    """
    # Drop latitude and longitude if present
    df = df.drop(columns=['lon', 'lat'], errors='ignore')

    # Identify numeric and categorical columns
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
    categorical_col = 'soil_type'

    if categorical_col not in df.columns:
        raise ValueError(f"Column '{categorical_col}' not found in DataFrame.")

    # Handle missing values by filling with column means (for numeric)
    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())

    # Check class distribution
    class_counts = df[categorical_col].value_counts()
    min_class_count = class_counts.min()

    # Adjust SMOTE parameters based on class distribution
    k_neighbors = min(5, min_class_count - 1) if min_class_count > 1 else 1

    # Apply SMOTE only if feasible
    if min_class_count > 1:
        smote = SMOTE(k_neighbors=k_neighbors)
        X, y = df[numeric_cols], df[categorical_col]
        X_resampled, y_resampled = smote.fit_resample(X, y)

        # Combine resampled data
        balanced_df = pd.DataFrame(X_resampled, columns=numeric_cols)
        balanced_df[categorical_col] = y_resampled
    else:
        balanced_df = df.copy()

    # Add Gaussian noise to numeric columns for additional variability
    def add_noise(data, noise_level):
        noise = np.random.normal(0, noise_level, data.shape)
        return data + noise

    augmented_data = []
    for soil_class in balanced_df[categorical_col].unique():
        class_data = balanced_df[balanced_df[categorical_col] == soil_class]

        # Duplicate rows if SMOTE could not generate enough samples
        while len(class_data) < n_samples_per_class:
            noisy_data = add_noise(class_data[numeric_cols], noise_level)
            noisy_data[categorical_col] = soil_class
            class_data = pd.concat([class_data, noisy_data], ignore_index=True)

        augmented_data.append(class_data.head(n_samples_per_class))

    # Combine all classes into a single DataFrame
    augmented_df = pd.concat(augmented_data, ignore_index=True)

    return augmented_df

# Example usage (assuming processed_soil_data.csv is loaded as `df`):
df = pd.read_csv('backend/ml/processed_soil_data.csv')
augmented_df = augment_soil_data(df)
augmented_df.to_csv('backend/ml/augmented_soil_data.csv', index=False)
