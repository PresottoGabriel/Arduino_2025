import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as st
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import random

# Define constants
BASE_DIRECTORY = os.path.abspath('data')
SAVE_FOLDER = os.path.abspath('graphs')
REMOVE_POINTS = 2
COLNAMES = ["V", "2", "3", "4", "I"]
DIODE_SETTINGS = {
    'IN4007': {'filter': 500, 'temperature': 296},
    'IN60P': {'filter': 200, 'temperature': 296},
    '6A10': {'filter': 450, 'temperature': 296},
    'BAW62': {'filter': 550, 'temperature': 294},
    'ZY160': {'filter': 500, 'temperature': 294},
    'PR1007': {'filter': 450, 'temperature': 294},
    'BZX55C': {'filter': 700, 'temperature': 295},
    'BAW79C33': {'filter': 650, 'temperature': 294},
}
# Initialize a list to store summary data for all diodes
diode_summary_data = []

# Define the ratio e/k_B
e_over_kB = 1.160451812 * 10**4  # in C/K

# Ensure save folder exists
os.makedirs(SAVE_FOLDER, exist_ok=True)

# Number of samples to analyze for non-ideality factor
number_samples = 10

# Function to get the best distribution for a given dataset
def get_best_distribution(data):
    dist_names = [
    "norm", 
    ]
    # Add more distributions as needed
    results = []
    for dist_name in dist_names:
        # Get the distribution object
        dist = getattr(st, dist_name)
        # Fit the distribution to the data
        params = dist.fit(data)
        # Calculate the p-value using the Kolmogorov-Smirnov test
        D, p = st.kstest(data, dist_name, args=params)
        # Append the results
        results.append((dist_name, p, params))
    # Sort results by p-value
    best_dist, best_p, best_params = max(results, key=lambda x: x[1])
    return best_dist, best_p, best_params
# Function to process each file and return a DataFrame
def process_file(file_path, filter_value):
    try:
        # Read the file into a DataFrame
        df = pd.read_csv(file_path, sep=r'\s*,\s*', names=COLNAMES, engine='python')
        df = df.drop(columns=["2", "3", "4"]) # Remove unnecessary columns
        df = df[df['V'] > filter_value] # Filter out rows with V <= filter_value
        df = df.iloc[:-REMOVE_POINTS] # Remove the last two points
        df = df[df['I'] > 0] # Ensure current is positive
        df['ln_I'] = np.log(df['I']) # Calculate natural logarithm of current
        return df
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

# Function to analyze each diode
def analyze_diode(diode_name, diode_folder, settings):
    # Analyze a single diode and store results in the global summary data
    global diode_summary_data  # Use the global variable to store results
    filter_value = settings['filter']
    temperature = settings['temperature']
    theo_slope = e_over_kB / temperature
    # Initialize a list to store datasets for this diode
    datasets = []
    for file_name in os.listdir(diode_folder):
        if file_name.lower().endswith('.txt'):
            file_path = os.path.join(diode_folder, file_name)
            df = process_file(file_path, filter_value)
            if df is not None:
                datasets.append(df)
    
    # Antes de concatenar, filtre datasets vazios
    datasets = [df for df in datasets if df is not None and not df.empty]
    if datasets:
        # Concatenate all datasets
        combined_df = pd.concat(datasets)
        
        # Group by unique voltage values and calculate average ln(I)
        grouped = combined_df.groupby('V').mean().reset_index()

        # Só faz a regressão se houver dados suficientes
        if not grouped.empty and len(grouped) > 1:
            X = grouped[['V']]
            y = grouped['ln_I']
            model = LinearRegression()
            model.fit(X, y)
            slope, intercept = model.coef_[0], model.intercept_
            y_pred = model.predict(X)
            r2 = r2_score(y, y_pred)
        else:
            print(f"Atenção: Dados insuficientes para regressão em {diode_name}")
            slope, intercept, y_pred, r2 = np.nan, np.nan, [], np.nan

        # Calculate slopes for individual datasets
        slopes = []
        for df in datasets:
            X_single = df[['V']]
            y_single = df['ln_I']
            if len(X_single) > 0 and len(y_single) > 0:  # Só ajusta se houver dados
                model_single = LinearRegression()
                model_single.fit(X_single, y_single)
                slopes.append(model_single.coef_[0] * 1000)  # Convert to mV

        # Best distribution analysis e plot só se houver slopes
        if slopes:
            best_dist, best_p, best_params = get_best_distribution(slopes)
            dist = getattr(st, best_dist)
            mean, var = dist.stats(*best_params, moments='mv')
        else:
            print(f"Atenção: Nenhum slope calculado para {diode_name}. Pulando análise de distribuição.")
            best_dist, best_p, best_params, mean, std_dev = np.nan, np.nan, (), np.nan, np.nan

        # Append results to the summary data
        param_str = ', '.join([f'{param:.4f}' for param in best_params]) if slopes else ''
        diode_summary_data.append({
            'Diode': diode_name,
            'Best Distribution': best_dist,
            'p-value': best_p,
            'Mean': mean,
            'Standard Deviation': np.sqrt(var),
            'Distribution Parameters': param_str,  # Store as a formatted string
        })

        # Create the combined plot
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))

        # Histogram and distribution
        if slopes:
            axes[2].hist(slopes, bins='auto', density=True, alpha=0.6, color='g', label='Histogram')
            x = np.linspace(min(slopes) - 1, max(slopes) + 1, 1000)
            axes[2].plot(x, dist.pdf(x, *best_params), 'r-', label=f'{best_dist} Fit')
            axes[2].set_xlabel(r'$e/\eta kT$', fontsize=12)
            axes[2].set_ylabel('PDF', fontsize=12)
            axes[2].legend()

        # Scatter plot without logarithm
        axes[0].scatter(grouped['V'], grouped['I'], color='blue', label='Averaged Data')
        axes[0].set_xlabel(r'$\Delta V$ (mV)', fontsize=14)
        axes[0].text(
            0.5, 0.90, f'{diode_name}',
            transform=axes[0].transAxes,
            fontsize=16,
            ha='center',
            va='bottom'
        )
        axes[0].set_ylabel(r'$I$ (Current)', fontsize=14)
        axes[0].legend()
        
        # Scatter plot with regression
        axes[1].scatter(grouped['V'], grouped['ln_I'], label='Averaged Data', color='blue')
        axes[1].plot(grouped['V'], y_pred, color='red', label=f'Fit: slope={slope:.3f}, R²={r2:.3f}')
        axes[1].set_xlabel(r'$\Delta V$ (mV)', fontsize=12)
        axes[1].set_ylabel(r'$\ln(I)$', fontsize=12)
        axes[1].legend()

        # Save the combined plot
        plt.suptitle(f'{diode_name} Analysis', fontsize=16)
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.savefig(os.path.join(SAVE_FOLDER, f'{diode_name}_combined_plot.png'))
        plt.close()

def non_ideality_factor_analysis(diode_name, diode_folder, settings):
    # Non-ideality factor calculation
    filter_value = settings['filter']
    temperature = settings['temperature']
    theo_slope = 11739.13 / temperature
    results = []

    # Process each file in the diode folder
    all_files = [file_name for file_name in os.listdir(diode_folder) if file_name.lower().endswith('.txt')]
    selected_files = random.sample(all_files, number_samples)  # Sample 100 files
    for file_name in selected_files:
        file_path = os.path.join(diode_folder, file_name)
        df = process_file(file_path, filter_value)
        if df is not None and not df.empty:
            first_row = df.iloc[0]
            last_row = df.iloc[-1]
            V_dif = (last_row['V'] - first_row['V']) / 1000
            LnI_dif = last_row['ln_I'] - first_row['ln_I']
            non_ideality_factor = theo_slope * V_dif / LnI_dif
            results.append(non_ideality_factor)
    
    # Store the results
    if results:
        mean_non_ideality_factor = np.mean(results)
        std_dev_non_ideality_factor = np.std(results)
        return mean_non_ideality_factor, std_dev_non_ideality_factor
    else:
        return None, None



# Now, analyze all diodes and calculate the product and relative error
for diode_name, settings in DIODE_SETTINGS.items():
    diode_folder = os.path.join(BASE_DIRECTORY, diode_name)
    if os.path.exists(diode_folder):
        analyze_diode(diode_name, diode_folder, settings)
        non_ideality_factor, std_dev_non_ideality_factor = non_ideality_factor_analysis(diode_name, diode_folder, settings)
        
        # Add the product of non-ideality factor, temperature, and mean of distribution to the summary data
        mean_temp = settings['temperature']
        for row in diode_summary_data:
            if row['Diode'] == diode_name:
                mean_distribution = row['Mean']
                # Só calcula se todos os valores forem válidos
                if (
                    non_ideality_factor is not None and
                    mean_distribution is not None and
                    not np.isnan(non_ideality_factor) and
                    not np.isnan(mean_distribution)
                ):
                    product = non_ideality_factor * mean_temp * mean_distribution
                    std_product = np.sqrt(
                        (std_dev_non_ideality_factor * mean_temp * mean_distribution) ** 2 +
                        (non_ideality_factor * mean_temp * np.sqrt(row['Standard Deviation']) ** 2)
                    )
                    # Update the row with product and relative error
                    row['Product'] = product
                    row['Standard Deviation Product'] = std_product

                    # Calculate relative error in percentage
                    relative_error = abs((product - e_over_kB) / e_over_kB) * 100
                    row['Relative Error (%)'] = relative_error
                else:
                    row['Product'] = None
                    row['Relative Error (%)'] = None
                    row['Standard Deviation Product'] = None
    else:
        print(f"Warning: Folder for {diode_name} not found.")

# Save the updated summary table with the product and relative error
summary_df = pd.DataFrame(diode_summary_data)
summary_df.to_csv(os.path.join(SAVE_FOLDER, 'diode_summary_with_product_and_error.csv'), index=False)
