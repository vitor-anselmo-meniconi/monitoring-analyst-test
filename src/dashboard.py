import matplotlib.pyplot as plt
import pandas as pd
import os

def generate_dashboard():
    # File paths - ensures it looks for data in the right place
    input_path = 'data/transactions.csv'
    output_dir = 'assets'
    output_path = f'{output_dir}/realtime_dashboard.png'

    # Ensure assets directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"Loading data from {input_path}...")
    try:
        df = pd.read_csv(input_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Pivot data to organize columns by status
        df_pivot = df.pivot_table(index='timestamp', columns='status', values='count', fill_value=0)
        
        # Plotting configuration
        fig, axes = plt.subplots(3, 1, figsize=(15, 10), sharex=True)
        
        # Chart 1: Failed Transactions (Critical)
        axes[0].plot(df_pivot.index, df_pivot.get('failed', 0), color='#e74c3c', linewidth=2, label='Failed')
        axes[0].set_title('Critical: Failed Transactions', fontsize=12, fontweight='bold')
        axes[0].set_ylabel('Count')
        axes[0].grid(True, alpha=0.3)
        axes[0].legend(loc='upper left')
        
        # Chart 2: Denied Transactions (Warning)
        axes[1].plot(df_pivot.index, df_pivot.get('denied', 0), color='#f39c12', linewidth=2, label='Denied')
        axes[1].set_title('Warning: Denied Transactions', fontsize=12, fontweight='bold')
        axes[1].set_ylabel('Count')
        axes[1].grid(True, alpha=0.3)
        axes[1].legend(loc='upper left')

        # Chart 3: Reversed Transactions (Info)
        # Summing 'reversed' and 'backend_reversed' if both exist
        reversed_data = df_pivot.get('reversed', 0)
        if 'backend_reversed' in df_pivot.columns:
            reversed_data = reversed_data + df_pivot['backend_reversed']

        axes[2].plot(df_pivot.index, reversed_data, color='#3498db', linewidth=2, label='Reversed')
        axes[2].set_title('Info: Reversed Transactions', fontsize=12, fontweight='bold')
        axes[2].set_ylabel('Count')
        axes[2].set_xlabel('Time')
        axes[2].grid(True, alpha=0.3)
        axes[2].legend(loc='upper left')
        
        plt.tight_layout()
        plt.savefig(output_path)
        print(f"Dashboard successfully generated at: {output_path}")

    except FileNotFoundError:
        print(f"Error: The file {input_path} was not found. Please ensure it exists in the 'data' folder.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    generate_dashboard()
