import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from typing import Optional


def plot_responder_comparison_boxplot(df: pd.DataFrame, save_path: Optional[str] = None):
    populations = sorted(df['population'].unique())
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()
    sns.set_style("whitegrid")
    
    for idx, population in enumerate(populations):
        pop_data = df[df['population'] == population]
        sns.boxplot(
            data=pop_data,
            x='response',
            y='percentage',
            hue='response',
            ax=axes[idx],
            palette={'yes': '#2ecc71', 'no': '#e74c3c'},
            legend=False
        )
        axes[idx].set_title(f'{population.replace("_", " ").title()}', fontsize=12, fontweight='bold')
        axes[idx].set_xlabel('Response', fontsize=10)
        axes[idx].set_ylabel('Relative Frequency (%)', fontsize=10)
        axes[idx].set_xticks([0, 1])
        axes[idx].set_xticklabels(['Non-Responder', 'Responder'])
    
    axes[-1].axis('off')
    
    plt.suptitle('Cell Population Frequencies: Responders vs Non-Responders\n(Melanoma, Miraclib, PBMC)', 
                 fontsize=14, fontweight='bold', y=1.00)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {save_path}")
    
    return fig