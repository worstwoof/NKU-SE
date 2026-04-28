# -*- coding: utf-8 -*-
"""
Moon Colony Transportation Model - MCM 2026 Problem B
Multi-Modal Logistics Optimization for 100,000-Person Lunar Colony
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import json
import os

# ============================================================================
# Global Settings - Nature/Science Style
# ============================================================================
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'DejaVu Sans'],
    'font.size': 11,
    'axes.unicode_minus': False,
    'axes.linewidth': 0.8,
    'axes.edgecolor': '#333333',
    'axes.labelcolor': '#333333',
    'xtick.color': '#333333',
    'ytick.color': '#333333',
    'text.color': '#333333',
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'axes.grid': True,
    'grid.alpha': 0.3,
    'grid.linestyle': '--',
    'grid.linewidth': 0.5,
})

# Color Palette - Academic Style
COLORS = {
    'blue': '#4C72B0',
    'orange': '#DD8452',
    'green': '#55A868',
    'red': '#C44E52',
    'purple': '#8172B3',
    'brown': '#937860',
    'cyan': '#64B5CD',
    'gray': '#8C8C8C',
}

# Create output directories
os.makedirs('../figures', exist_ok=True)
os.makedirs('../results', exist_ok=True)

# ============================================================================
# Model Parameters
# ============================================================================

# Mission Requirements
TOTAL_MATERIAL = 100_000_000  # metric tons
COLONY_POPULATION = 100_000  # people
START_YEAR = 2050

# Space Elevator System Parameters
N_GALACTIC_HARBOURS = 3
ELEVATOR_CAPACITY_PER_HARBOUR = 179_000  # metric tons/year (题目原文)
TOTAL_ELEVATOR_CAPACITY = N_GALACTIC_HARBOURS * ELEVATOR_CAPACITY_PER_HARBOUR  # 537,000 MT/year
ELEVATOR_COST_PER_KG = 100  # USD/kg (low operating cost, electricity-powered)
TETHER_LENGTH = 100_000  # km
GEO_ALTITUDE = 35_786  # km

# Rocket System Parameters (2050 projections with advanced reusable systems)
ROCKET_LAUNCH_SITES = {
    'Alaska': {'lat': 64.8, 'lon': -147.7, 'capacity': 200},
    'California': {'lat': 34.6, 'lon': -120.6, 'capacity': 350},
    'Texas': {'lat': 25.9, 'lon': -97.5, 'capacity': 500},
    'Florida': {'lat': 28.5, 'lon': -80.6, 'capacity': 600},
    'Virginia': {'lat': 37.8, 'lon': -75.5, 'capacity': 150},
    'Kazakhstan': {'lat': 45.6, 'lon': 63.3, 'capacity': 300},
    'French_Guiana': {'lat': 5.2, 'lon': -52.8, 'capacity': 250},
    'India': {'lat': 13.7, 'lon': 80.2, 'capacity': 300},
    'China': {'lat': 38.8, 'lon': 111.6, 'capacity': 400},
    'New_Zealand': {'lat': -39.3, 'lon': 177.9, 'capacity': 200},
}
ROCKET_PAYLOAD = 125  # metric tons per launch (average of 100-150)
ROCKET_COST_PER_KG = 1500  # USD/kg to Moon (2050 estimate with reusable tech)

# Environmental Parameters
ROCKET_CO2_PER_LAUNCH = 500  # metric tons CO2 per launch (estimate)
ELEVATOR_CO2_PER_TON = 0.1  # metric tons CO2 per metric ton payload (electricity)

# Water Requirements (per person per year, with recycling)
WATER_CONSUMPTION_DAILY = 15  # liters/person/day (after recycling)
WATER_DENSITY = 1  # kg/liter

# Failure Rates
ELEVATOR_FAILURE_RATE = 0.02  # 2% annual downtime
ROCKET_FAILURE_RATE = 0.03  # 3% failure per launch
TETHER_SWAY_IMPACT = 0.05  # 5% capacity reduction due to sway

# ============================================================================
# Model 1: Pure Space Elevator System
# ============================================================================

def model_elevator_only():
    """Calculate cost and timeline using only Space Elevator System"""
    
    # Effective capacity considering downtime
    effective_capacity = TOTAL_ELEVATOR_CAPACITY * (1 - ELEVATOR_FAILURE_RATE)
    
    # Timeline
    years_needed = TOTAL_MATERIAL / effective_capacity
    completion_year = START_YEAR + years_needed
    
    # Cost
    total_cost = TOTAL_MATERIAL * 1000 * ELEVATOR_COST_PER_KG  # Convert to kg
    
    # Environmental impact
    total_co2 = TOTAL_MATERIAL * ELEVATOR_CO2_PER_TON
    
    # Annual breakdown
    years = np.arange(START_YEAR, int(np.ceil(completion_year)) + 1)
    annual_delivery = np.full(len(years), effective_capacity)
    cumulative = np.cumsum(annual_delivery)
    cumulative = np.minimum(cumulative, TOTAL_MATERIAL)
    
    # Adjust last year
    if len(annual_delivery) > 0:
        remaining = TOTAL_MATERIAL - (cumulative[-2] if len(cumulative) > 1 else 0)
        annual_delivery[-1] = min(annual_delivery[-1], remaining)
    
    return {
        'scenario': 'Elevator Only',
        'years_needed': years_needed,
        'completion_year': completion_year,
        'total_cost_usd': total_cost,
        'total_co2_mt': total_co2,
        'annual_capacity': effective_capacity,
        'years': years.tolist(),
        'annual_delivery': annual_delivery.tolist(),
        'cumulative_delivery': cumulative.tolist(),
    }

# ============================================================================
# Model 2: Pure Rocket System
# ============================================================================

def model_rocket_only(sites_to_use=None):
    """Calculate cost and timeline using only traditional rockets"""
    
    if sites_to_use is None:
        sites_to_use = list(ROCKET_LAUNCH_SITES.keys())
    
    # Total annual launches
    total_launches_per_year = sum(
        ROCKET_LAUNCH_SITES[site]['capacity'] 
        for site in sites_to_use
    )
    
    # Effective capacity considering failure rate
    successful_launches = total_launches_per_year * (1 - ROCKET_FAILURE_RATE)
    annual_capacity = successful_launches * ROCKET_PAYLOAD
    
    # Timeline
    years_needed = TOTAL_MATERIAL / annual_capacity
    completion_year = START_YEAR + years_needed
    
    # Cost
    total_cost = TOTAL_MATERIAL * 1000 * ROCKET_COST_PER_KG
    
    # Environmental impact
    total_launches = TOTAL_MATERIAL / ROCKET_PAYLOAD
    total_co2 = total_launches * ROCKET_CO2_PER_LAUNCH
    
    # Annual breakdown
    years = np.arange(START_YEAR, int(np.ceil(completion_year)) + 1)
    annual_delivery = np.full(len(years), annual_capacity)
    cumulative = np.cumsum(annual_delivery)
    cumulative = np.minimum(cumulative, TOTAL_MATERIAL)
    
    return {
        'scenario': 'Rocket Only',
        'years_needed': years_needed,
        'completion_year': completion_year,
        'total_cost_usd': total_cost,
        'total_co2_mt': total_co2,
        'annual_capacity': annual_capacity,
        'sites_used': sites_to_use,
        'annual_launches': total_launches_per_year,
        'years': years.tolist(),
        'annual_delivery': annual_delivery.tolist(),
        'cumulative_delivery': cumulative.tolist(),
    }

# ============================================================================
# Model 3: Hybrid Optimization
# ============================================================================

def model_hybrid(elevator_fraction=None, rocket_sites=None):
    """Optimize hybrid approach using both systems running in parallel
    
    If elevator_fraction is None, automatically optimize allocation based on capacity ratio.
    """
    
    if rocket_sites is None:
        # Use all sites for maximum capacity
        rocket_sites = list(ROCKET_LAUNCH_SITES.keys())
    
    # Elevator contribution
    elevator_capacity = TOTAL_ELEVATOR_CAPACITY * (1 - ELEVATOR_FAILURE_RATE) * (1 - TETHER_SWAY_IMPACT)
    
    # Rocket contribution
    total_launches = sum(ROCKET_LAUNCH_SITES[site]['capacity'] for site in rocket_sites)
    rocket_capacity = total_launches * (1 - ROCKET_FAILURE_RATE) * ROCKET_PAYLOAD
    
    # Total capacity (parallel operation)
    total_capacity = elevator_capacity + rocket_capacity
    
    # Optimal allocation: distribute material proportionally to capacity
    # This ensures both systems finish at the same time
    if elevator_fraction is None:
        elevator_fraction = elevator_capacity / total_capacity
    
    elevator_material = TOTAL_MATERIAL * elevator_fraction
    rocket_material = TOTAL_MATERIAL * (1 - elevator_fraction)
    
    # Timeline - both systems work in parallel
    # The timeline is determined by whichever finishes last
    elevator_years = elevator_material / elevator_capacity if elevator_capacity > 0 else float('inf')
    rocket_years = rocket_material / rocket_capacity if rocket_capacity > 0 else float('inf')
    
    # For truly parallel operation with optimal allocation
    # Total time = Total Material / Total Capacity
    years_needed = TOTAL_MATERIAL / total_capacity
    completion_year = START_YEAR + years_needed
    
    # Cost
    elevator_cost = elevator_material * 1000 * ELEVATOR_COST_PER_KG
    rocket_cost = rocket_material * 1000 * ROCKET_COST_PER_KG
    total_cost = elevator_cost + rocket_cost
    
    # Environmental impact
    elevator_co2 = elevator_material * ELEVATOR_CO2_PER_TON
    rocket_launches = rocket_material / ROCKET_PAYLOAD
    rocket_co2 = rocket_launches * ROCKET_CO2_PER_LAUNCH
    total_co2 = elevator_co2 + rocket_co2
    
    return {
        'scenario': f'Hybrid ({elevator_fraction*100:.0f}% Elevator)',
        'years_needed': years_needed,
        'completion_year': completion_year,
        'total_cost_usd': total_cost,
        'elevator_cost_usd': elevator_cost,
        'rocket_cost_usd': rocket_cost,
        'total_co2_mt': total_co2,
        'elevator_co2_mt': elevator_co2,
        'rocket_co2_mt': rocket_co2,
        'elevator_fraction': elevator_fraction,
        'rocket_fraction': 1 - elevator_fraction,
        'rocket_sites': rocket_sites,
        'elevator_capacity': elevator_capacity,
        'rocket_capacity': rocket_capacity,
        'total_capacity': total_capacity,
        'elevator_material': elevator_material,
        'rocket_material': rocket_material,
    }

# ============================================================================
# Model 4: Sensitivity Analysis with Failures
# ============================================================================

def sensitivity_analysis():
    """Analyze impact of different failure scenarios"""
    
    global ELEVATOR_FAILURE_RATE, ROCKET_FAILURE_RATE
    
    # Save original values
    orig_elevator_failure = ELEVATOR_FAILURE_RATE
    orig_rocket_failure = ROCKET_FAILURE_RATE
    
    # Failure scenarios
    scenarios = []
    
    # Vary elevator failure rate
    for failure_rate in np.arange(0, 0.21, 0.02):
        ELEVATOR_FAILURE_RATE = failure_rate
        ROCKET_FAILURE_RATE = orig_rocket_failure
        result = model_hybrid()
        scenarios.append({
            'parameter': 'Elevator Failure Rate',
            'value': failure_rate,
            'years_needed': result['years_needed'],
            'total_cost': result['total_cost_usd'],
            'total_co2': result['total_co2_mt'],
        })
    
    # Reset and vary rocket failure rate
    ELEVATOR_FAILURE_RATE = orig_elevator_failure
    for failure_rate in np.arange(0, 0.21, 0.02):
        ROCKET_FAILURE_RATE = failure_rate
        result = model_hybrid()
        scenarios.append({
            'parameter': 'Rocket Failure Rate',
            'value': failure_rate,
            'years_needed': result['years_needed'],
            'total_cost': result['total_cost_usd'],
            'total_co2': result['total_co2_mt'],
        })
    
    # Reset to original values
    ELEVATOR_FAILURE_RATE = orig_elevator_failure
    ROCKET_FAILURE_RATE = orig_rocket_failure
    
    return scenarios

# ============================================================================
# Water Requirement Analysis
# ============================================================================

def water_requirement_analysis():
    """Calculate annual water needs for the colony"""
    
    # Daily water consumption
    daily_water_liters = COLONY_POPULATION * WATER_CONSUMPTION_DAILY
    annual_water_liters = daily_water_liters * 365
    annual_water_kg = annual_water_liters * WATER_DENSITY
    annual_water_mt = annual_water_kg / 1000
    
    # Cost via different methods
    elevator_cost = annual_water_mt * 1000 * ELEVATOR_COST_PER_KG
    rocket_cost = annual_water_mt * 1000 * ROCKET_COST_PER_KG
    
    # Environmental impact
    elevator_co2 = annual_water_mt * ELEVATOR_CO2_PER_TON
    rocket_launches = annual_water_mt / ROCKET_PAYLOAD
    rocket_co2 = rocket_launches * ROCKET_CO2_PER_LAUNCH
    
    return {
        'annual_water_mt': annual_water_mt,
        'annual_water_liters': annual_water_liters,
        'elevator_cost_usd': elevator_cost,
        'rocket_cost_usd': rocket_cost,
        'elevator_co2_mt': elevator_co2,
        'rocket_co2_mt': rocket_co2,
        'water_per_person_daily_liters': WATER_CONSUMPTION_DAILY,
    }

# ============================================================================
# Optimization: Find Optimal Elevator Fraction
# ============================================================================

def optimize_hybrid_fraction():
    """Find optimal elevator fraction for different objectives
    
    Tests different manual allocations to show trade-offs.
    Note: The optimal allocation is when material is distributed
    proportionally to capacity (elevator_fraction = elevator_capacity / total_capacity)
    """
    
    # Get capacity-optimal allocation
    optimal = model_hybrid()
    optimal_fraction = optimal['elevator_fraction']
    
    # Test range of fractions around optimal
    fractions = np.arange(0.2, 0.95, 0.05)
    results = []
    
    for f in fractions:
        # Calculate with fixed fraction
        elevator_capacity = TOTAL_ELEVATOR_CAPACITY * (1 - ELEVATOR_FAILURE_RATE) * (1 - TETHER_SWAY_IMPACT)
        rocket_sites = list(ROCKET_LAUNCH_SITES.keys())
        total_launches = sum(ROCKET_LAUNCH_SITES[site]['capacity'] for site in rocket_sites)
        rocket_capacity = total_launches * (1 - ROCKET_FAILURE_RATE) * ROCKET_PAYLOAD
        
        elevator_material = TOTAL_MATERIAL * f
        rocket_material = TOTAL_MATERIAL * (1 - f)
        
        elevator_years = elevator_material / elevator_capacity if elevator_capacity > 0 else float('inf')
        rocket_years = rocket_material / rocket_capacity if rocket_capacity > 0 else float('inf')
        years = max(elevator_years, rocket_years)
        
        elevator_cost = elevator_material * 1000 * ELEVATOR_COST_PER_KG
        rocket_cost = rocket_material * 1000 * ROCKET_COST_PER_KG
        cost = elevator_cost + rocket_cost
        
        elevator_co2 = elevator_material * ELEVATOR_CO2_PER_TON
        rocket_launches = rocket_material / ROCKET_PAYLOAD
        rocket_co2 = rocket_launches * ROCKET_CO2_PER_LAUNCH
        co2 = elevator_co2 + rocket_co2
        
        results.append({
            'fraction': f,
            'years': years,
            'cost': cost,
            'co2': co2,
            'is_optimal': abs(f - optimal_fraction) < 0.03,
        })
    
    return results

# ============================================================================
# Visualization Functions
# ============================================================================

def plot_scenario_comparison():
    """Compare three main scenarios"""
    
    elevator = model_elevator_only()
    rocket = model_rocket_only()
    hybrid = model_hybrid()  # Auto-optimize
    
    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    
    hybrid_label = f'Hybrid\n({hybrid["elevator_fraction"]*100:.0f}% Elevator)'
    scenarios = ['Elevator\nOnly', 'Rocket\nOnly', hybrid_label]
    
    # Timeline comparison
    ax = axes[0]
    years = [elevator['years_needed'], rocket['years_needed'], hybrid['years_needed']]
    bars = ax.bar(scenarios, years, color=[COLORS['blue'], COLORS['orange'], COLORS['green']], 
                  edgecolor='white', linewidth=1.5)
    ax.set_ylabel('Years to Complete')
    ax.set_title('Timeline Comparison', fontweight='bold')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    for bar, val in zip(bars, years):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2, 
                f'{val:.1f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # Cost comparison (in trillion USD)
    ax = axes[1]
    costs = [elevator['total_cost_usd']/1e12, rocket['total_cost_usd']/1e12, 
             hybrid['total_cost_usd']/1e12]
    bars = ax.bar(scenarios, costs, color=[COLORS['blue'], COLORS['orange'], COLORS['green']],
                  edgecolor='white', linewidth=1.5)
    ax.set_ylabel('Total Cost (Trillion USD)')
    ax.set_title('Cost Comparison', fontweight='bold')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    for bar, val in zip(bars, costs):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                f'${val:.1f}T', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # CO2 comparison (in million tons)
    ax = axes[2]
    co2 = [elevator['total_co2_mt']/1e6, rocket['total_co2_mt']/1e6, hybrid['total_co2_mt']/1e6]
    bars = ax.bar(scenarios, co2, color=[COLORS['blue'], COLORS['orange'], COLORS['green']],
                  edgecolor='white', linewidth=1.5)
    ax.set_ylabel('CO₂ Emissions (Million MT)')
    ax.set_title('Environmental Impact', fontweight='bold')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    for bar, val in zip(bars, co2):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5, 
                f'{val:.1f}M', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # Add subplot labels
    for idx, ax in enumerate(axes):
        ax.text(-0.12, 1.05, f'({chr(97+idx)})', transform=ax.transAxes,
                fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('../figures/fig_01_scenario_comparison.pdf', dpi=300, bbox_inches='tight')
    plt.savefig('../figures/fig_01_scenario_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    return {'elevator': elevator, 'rocket': rocket, 'hybrid': hybrid}

def plot_optimization_surface():
    """Plot optimization of elevator fraction"""
    
    results = optimize_hybrid_fraction()
    fractions = [r['fraction'] for r in results]
    years = [r['years'] for r in results]
    costs = [r['cost']/1e12 for r in results]
    co2 = [r['co2']/1e6 for r in results]
    
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # Cost vs Years trade-off
    ax = axes[0]
    scatter = ax.scatter(years, costs, c=fractions, cmap='viridis', s=100, 
                         edgecolor='white', linewidth=1)
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Elevator Fraction')
    ax.set_xlabel('Years to Complete')
    ax.set_ylabel('Total Cost (Trillion USD)')
    ax.set_title('Cost-Time Trade-off', fontweight='bold')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Highlight optimal points
    min_cost_idx = np.argmin(costs)
    min_time_idx = np.argmin(years)
    ax.scatter(years[min_cost_idx], costs[min_cost_idx], s=200, marker='*', 
               c=COLORS['red'], label=f'Min Cost (f={fractions[min_cost_idx]:.2f})', zorder=5)
    ax.scatter(years[min_time_idx], costs[min_time_idx], s=200, marker='D', 
               c=COLORS['green'], label=f'Min Time (f={fractions[min_time_idx]:.2f})', zorder=5)
    ax.legend(frameon=False, loc='upper right')
    
    # CO2 vs Cost trade-off
    ax = axes[1]
    scatter = ax.scatter(costs, co2, c=fractions, cmap='viridis', s=100,
                         edgecolor='white', linewidth=1)
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Elevator Fraction')
    ax.set_xlabel('Total Cost (Trillion USD)')
    ax.set_ylabel('CO₂ Emissions (Million MT)')
    ax.set_title('Cost-Environment Trade-off', fontweight='bold')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Add subplot labels
    for idx, ax in enumerate(axes):
        ax.text(-0.12, 1.05, f'({chr(97+idx)})', transform=ax.transAxes,
                fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('../figures/fig_02_optimization_tradeoff.pdf', dpi=300, bbox_inches='tight')
    plt.savefig('../figures/fig_02_optimization_tradeoff.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    return results

def plot_timeline_projection():
    """Plot cumulative delivery over time for different scenarios"""
    
    elevator = model_elevator_only()
    rocket = model_rocket_only()
    hybrid = model_hybrid()  # Auto-optimize
    
    # Create extended timeline
    max_years = max(elevator['years_needed'], rocket['years_needed'], hybrid['years_needed'])
    years = np.arange(START_YEAR, START_YEAR + int(np.ceil(max_years)) + 1)
    
    # Calculate cumulative deliveries
    def calc_cumulative(capacity, total):
        cum = np.minimum(np.arange(1, len(years)+1) * capacity, total)
        return cum
    
    elevator_cum = calc_cumulative(elevator['annual_capacity'], TOTAL_MATERIAL)
    rocket_cum = calc_cumulative(rocket['annual_capacity'], TOTAL_MATERIAL)
    hybrid_cum = calc_cumulative(hybrid['total_capacity'], TOTAL_MATERIAL)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.plot(years, elevator_cum/1e6, color=COLORS['blue'], linewidth=2.5, 
            label='Elevator Only', marker='o', markevery=20, markersize=6)
    ax.fill_between(years, 0, elevator_cum/1e6, color=COLORS['blue'], alpha=0.1)
    
    ax.plot(years, rocket_cum/1e6, color=COLORS['orange'], linewidth=2.5, 
            label='Rocket Only', marker='s', markevery=20, markersize=6)
    ax.fill_between(years, 0, rocket_cum/1e6, color=COLORS['orange'], alpha=0.1)
    
    ax.plot(years, hybrid_cum/1e6, color=COLORS['green'], linewidth=2.5, 
            label='Hybrid (70% Elevator)', marker='^', markevery=20, markersize=6)
    ax.fill_between(years, 0, hybrid_cum/1e6, color=COLORS['green'], alpha=0.1)
    
    # Target line
    ax.axhline(y=TOTAL_MATERIAL/1e6, color=COLORS['red'], linestyle='--', 
               linewidth=1.5, label=f'Target: {TOTAL_MATERIAL/1e6:.0f}M MT')
    
    ax.set_xlabel('Year')
    ax.set_ylabel('Cumulative Material Delivered (Million MT)')
    ax.set_title('Material Delivery Timeline Projection', fontweight='bold')
    ax.legend(frameon=False, loc='lower right')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_xlim(START_YEAR, START_YEAR + int(np.ceil(max_years)))
    ax.set_ylim(0, TOTAL_MATERIAL/1e6 * 1.1)
    
    # Annotate completion years
    for scenario, cum, color, name in [
        (elevator, elevator_cum, COLORS['blue'], 'Elevator'),
        (rocket, rocket_cum, COLORS['orange'], 'Rocket'),
        (hybrid, hybrid_cum, COLORS['green'], 'Hybrid')
    ]:
        completion_year = START_YEAR + scenario['years_needed']
        ax.annotate(f'{name}: {completion_year:.0f}', 
                    xy=(completion_year, TOTAL_MATERIAL/1e6),
                    xytext=(completion_year - 15, TOTAL_MATERIAL/1e6 + 5),
                    fontsize=9, color=color,
                    arrowprops=dict(arrowstyle='->', color=color, lw=1))
    
    plt.tight_layout()
    plt.savefig('../figures/fig_03_timeline_projection.pdf', dpi=300, bbox_inches='tight')
    plt.savefig('../figures/fig_03_timeline_projection.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_sensitivity_analysis():
    """Plot sensitivity analysis results"""
    
    scenarios = sensitivity_analysis()
    
    # Separate by parameter
    elevator_scenarios = [s for s in scenarios if s['parameter'] == 'Elevator Failure Rate']
    rocket_scenarios = [s for s in scenarios if s['parameter'] == 'Rocket Failure Rate']
    
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # Elevator failure rate impact
    ax = axes[0]
    x = [s['value'] * 100 for s in elevator_scenarios]
    y_years = [s['years_needed'] for s in elevator_scenarios]
    y_cost = [s['total_cost'] / 1e12 for s in elevator_scenarios]
    
    ax2 = ax.twinx()
    line1 = ax.plot(x, y_years, color=COLORS['blue'], linewidth=2.5, marker='o', 
                    markersize=6, label='Years to Complete')
    line2 = ax2.plot(x, y_cost, color=COLORS['orange'], linewidth=2.5, marker='s', 
                     markersize=6, label='Total Cost')
    
    ax.set_xlabel('Elevator Failure Rate (%)')
    ax.set_ylabel('Years to Complete', color=COLORS['blue'])
    ax2.set_ylabel('Total Cost (Trillion USD)', color=COLORS['orange'])
    ax.set_title('Sensitivity to Elevator Failure Rate', fontweight='bold')
    ax.tick_params(axis='y', labelcolor=COLORS['blue'])
    ax2.tick_params(axis='y', labelcolor=COLORS['orange'])
    ax.spines['top'].set_visible(False)
    
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax.legend(lines, labels, frameon=False, loc='upper left')
    
    # Rocket failure rate impact
    ax = axes[1]
    x = [s['value'] * 100 for s in rocket_scenarios]
    y_years = [s['years_needed'] for s in rocket_scenarios]
    y_cost = [s['total_cost'] / 1e12 for s in rocket_scenarios]
    
    ax2 = ax.twinx()
    line1 = ax.plot(x, y_years, color=COLORS['blue'], linewidth=2.5, marker='o', 
                    markersize=6, label='Years to Complete')
    line2 = ax2.plot(x, y_cost, color=COLORS['orange'], linewidth=2.5, marker='s', 
                     markersize=6, label='Total Cost')
    
    ax.set_xlabel('Rocket Failure Rate (%)')
    ax.set_ylabel('Years to Complete', color=COLORS['blue'])
    ax2.set_ylabel('Total Cost (Trillion USD)', color=COLORS['orange'])
    ax.set_title('Sensitivity to Rocket Failure Rate', fontweight='bold')
    ax.tick_params(axis='y', labelcolor=COLORS['blue'])
    ax2.tick_params(axis='y', labelcolor=COLORS['orange'])
    ax.spines['top'].set_visible(False)
    
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax.legend(lines, labels, frameon=False, loc='upper left')
    
    # Add subplot labels
    for idx, ax in enumerate(fig.axes[:2]):
        ax.text(-0.15, 1.05, f'({chr(97+idx)})', transform=ax.transAxes,
                fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('../figures/fig_04_sensitivity_analysis.pdf', dpi=300, bbox_inches='tight')
    plt.savefig('../figures/fig_04_sensitivity_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_water_analysis():
    """Plot water requirement analysis"""
    
    water = water_requirement_analysis()
    
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # Water requirement breakdown
    ax = axes[0]
    methods = ['Space Elevator', 'Traditional Rocket']
    costs = [water['elevator_cost_usd']/1e9, water['rocket_cost_usd']/1e9]
    colors = [COLORS['blue'], COLORS['orange']]
    
    bars = ax.bar(methods, costs, color=colors, edgecolor='white', linewidth=1.5)
    ax.set_ylabel('Annual Water Delivery Cost (Billion USD)')
    ax.set_title('Water Supply Cost Comparison', fontweight='bold')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    for bar, val in zip(bars, costs):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                f'${val:.1f}B', ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    # Add water amount annotation
    ax.annotate(f'Annual Water: {water["annual_water_mt"]:,.0f} MT\n({water["annual_water_liters"]/1e9:.2f} billion liters)',
                xy=(0.5, 0.95), xycoords='axes fraction',
                fontsize=10, ha='center', va='top',
                bbox=dict(boxstyle='round', facecolor='#F5F5F5', edgecolor='#DDDDDD'))
    
    # Environmental impact
    ax = axes[1]
    co2 = [water['elevator_co2_mt']/1e3, water['rocket_co2_mt']/1e3]
    
    bars = ax.bar(methods, co2, color=colors, edgecolor='white', linewidth=1.5)
    ax.set_ylabel('Annual CO₂ Emissions (Thousand MT)')
    ax.set_title('Environmental Impact of Water Delivery', fontweight='bold')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    for bar, val in zip(bars, co2):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                f'{val:.1f}K', ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    # Add subplot labels
    for idx, ax in enumerate(axes):
        ax.text(-0.12, 1.05, f'({chr(97+idx)})', transform=ax.transAxes,
                fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('../figures/fig_05_water_analysis.pdf', dpi=300, bbox_inches='tight')
    plt.savefig('../figures/fig_05_water_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    return water

def plot_launch_site_map():
    """Plot world map with rocket launch sites"""
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Simple world map outline (using scatter for sites)
    # Create equator line
    ax.axhline(y=0, color='gray', linestyle='--', linewidth=0.5, alpha=0.5)
    
    # Plot launch sites
    for site, data in ROCKET_LAUNCH_SITES.items():
        size = data['capacity'] * 3
        ax.scatter(data['lon'], data['lat'], s=size, c=COLORS['orange'], 
                   alpha=0.7, edgecolor='white', linewidth=1.5, zorder=5)
        ax.annotate(site.replace('_', ' '), (data['lon'], data['lat']),
                    xytext=(5, 5), textcoords='offset points', fontsize=8)
    
    # Plot Galactic Harbours (120 degrees apart on equator)
    galactic_lons = [0, 120, 240]
    for i, lon in enumerate(galactic_lons):
        ax.scatter(lon if lon <= 180 else lon - 360, 0, s=300, c=COLORS['blue'], 
                   marker='*', edgecolor='white', linewidth=1.5, zorder=6)
        ax.annotate(f'GH-{i+1}', (lon if lon <= 180 else lon - 360, 0),
                    xytext=(0, 10), textcoords='offset points', fontsize=9, 
                    ha='center', fontweight='bold', color=COLORS['blue'])
    
    ax.set_xlim(-180, 180)
    ax.set_ylim(-60, 80)
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_title('Global Launch Infrastructure', fontweight='bold')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor=COLORS['orange'], 
               markersize=10, label='Rocket Launch Site'),
        Line2D([0], [0], marker='*', color='w', markerfacecolor=COLORS['blue'], 
               markersize=15, label='Galactic Harbour'),
    ]
    ax.legend(handles=legend_elements, loc='lower left', frameon=False)
    
    plt.tight_layout()
    plt.savefig('../figures/fig_06_launch_sites.pdf', dpi=300, bbox_inches='tight')
    plt.savefig('../figures/fig_06_launch_sites.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_cost_breakdown():
    """Plot detailed cost breakdown for hybrid scenario"""
    
    # Get optimal fraction first
    optimal = model_hybrid()
    opt_f = optimal['elevator_fraction']
    
    # Test different configurations around optimal
    fractions = [0.4, 0.5, 0.6, opt_f, 0.8]
    results = []
    for f in fractions:
        # Recalculate with fixed fraction
        elevator_capacity = TOTAL_ELEVATOR_CAPACITY * (1 - ELEVATOR_FAILURE_RATE) * (1 - TETHER_SWAY_IMPACT)
        rocket_sites = list(ROCKET_LAUNCH_SITES.keys())
        total_launches = sum(ROCKET_LAUNCH_SITES[site]['capacity'] for site in rocket_sites)
        rocket_capacity = total_launches * (1 - ROCKET_FAILURE_RATE) * ROCKET_PAYLOAD
        
        elevator_material = TOTAL_MATERIAL * f
        rocket_material = TOTAL_MATERIAL * (1 - f)
        
        elevator_cost = elevator_material * 1000 * ELEVATOR_COST_PER_KG
        rocket_cost = rocket_material * 1000 * ROCKET_COST_PER_KG
        
        results.append({
            'elevator_cost_usd': elevator_cost,
            'rocket_cost_usd': rocket_cost,
        })
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    x = np.arange(len(fractions))
    width = 0.35
    
    elevator_costs = [r['elevator_cost_usd']/1e12 for r in results]
    rocket_costs = [r['rocket_cost_usd']/1e12 for r in results]
    
    bars1 = ax.bar(x - width/2, elevator_costs, width, label='Elevator Cost', 
                   color=COLORS['blue'], edgecolor='white', linewidth=1.5)
    bars2 = ax.bar(x + width/2, rocket_costs, width, label='Rocket Cost', 
                   color=COLORS['orange'], edgecolor='white', linewidth=1.5)
    
    # Add total line
    totals = [e + r for e, r in zip(elevator_costs, rocket_costs)]
    ax.plot(x, totals, 'ko-', linewidth=2, markersize=8, label='Total Cost')
    
    ax.set_xlabel('Elevator Fraction')
    ax.set_ylabel('Cost (Trillion USD)')
    ax.set_title('Cost Breakdown by Transportation Mode', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([f'{f*100:.0f}%' for f in fractions])
    ax.legend(frameon=False, loc='upper right')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    plt.savefig('../figures/fig_07_cost_breakdown.pdf', dpi=300, bbox_inches='tight')
    plt.savefig('../figures/fig_07_cost_breakdown.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_environmental_comparison():
    """Detailed environmental impact comparison"""
    
    elevator = model_elevator_only()
    rocket = model_rocket_only()
    hybrid = model_hybrid()  # Auto-optimize
    
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # Total CO2 comparison
    ax = axes[0]
    scenarios = ['Elevator Only', 'Rocket Only', f'Hybrid ({hybrid["elevator_fraction"]*100:.0f}%)']
    co2_values = [elevator['total_co2_mt']/1e6, rocket['total_co2_mt']/1e6, 
                  hybrid['total_co2_mt']/1e6]
    colors = [COLORS['blue'], COLORS['orange'], COLORS['green']]
    
    bars = ax.bar(scenarios, co2_values, color=colors, edgecolor='white', linewidth=1.5)
    ax.set_ylabel('Total CO₂ Emissions (Million MT)')
    ax.set_title('Environmental Footprint Comparison', fontweight='bold')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    for bar, val in zip(bars, co2_values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2, 
                f'{val:.1f}M', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # CO2 per MT delivered
    ax = axes[1]
    co2_per_mt = [elevator['total_co2_mt']/TOTAL_MATERIAL, 
                   rocket['total_co2_mt']/TOTAL_MATERIAL,
                   hybrid['total_co2_mt']/TOTAL_MATERIAL]
    
    bars = ax.bar(scenarios, co2_per_mt, color=colors, edgecolor='white', linewidth=1.5)
    ax.set_ylabel('CO₂ per MT Delivered (MT CO₂/MT payload)')
    ax.set_title('Carbon Intensity Comparison', fontweight='bold')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    for bar, val in zip(bars, co2_per_mt):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.0005, 
                f'{val:.4f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # Add subplot labels
    for idx, ax in enumerate(axes):
        ax.text(-0.12, 1.05, f'({chr(97+idx)})', transform=ax.transAxes,
                fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('../figures/fig_08_environmental_impact.pdf', dpi=300, bbox_inches='tight')
    plt.savefig('../figures/fig_08_environmental_impact.png', dpi=300, bbox_inches='tight')
    plt.close()

# ============================================================================
# Main Execution
# ============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("Moon Colony Transportation Model - MCM 2026 Problem B")
    print("=" * 60)
    
    # Run all models
    print("\n[1] Running Model 1: Space Elevator Only...")
    elevator_result = model_elevator_only()
    print(f"    Timeline: {elevator_result['years_needed']:.1f} years")
    print(f"    Total Cost: ${elevator_result['total_cost_usd']/1e12:.2f} trillion")
    print(f"    CO2 Emissions: {elevator_result['total_co2_mt']/1e6:.2f} million MT")
    
    print("\n[2] Running Model 2: Rocket Only...")
    rocket_result = model_rocket_only()
    print(f"    Timeline: {rocket_result['years_needed']:.1f} years")
    print(f"    Total Cost: ${rocket_result['total_cost_usd']/1e12:.2f} trillion")
    print(f"    CO2 Emissions: {rocket_result['total_co2_mt']/1e6:.2f} million MT")
    
    print("\n[3] Running Model 3: Hybrid (Optimal Allocation)...")
    hybrid_result = model_hybrid()  # Auto-optimize allocation
    print(f"    Timeline: {hybrid_result['years_needed']:.1f} years")
    print(f"    Total Cost: ${hybrid_result['total_cost_usd']/1e12:.2f} trillion")
    print(f"    CO2 Emissions: {hybrid_result['total_co2_mt']/1e6:.2f} million MT")
    
    print("\n[4] Water Requirement Analysis...")
    water_result = water_requirement_analysis()
    print(f"    Annual Water Need: {water_result['annual_water_mt']:,.0f} MT")
    print(f"    Elevator Delivery Cost: ${water_result['elevator_cost_usd']/1e9:.2f} billion/year")
    print(f"    Rocket Delivery Cost: ${water_result['rocket_cost_usd']/1e9:.2f} billion/year")
    
    print("\n[5] Generating Visualizations...")
    
    # Generate all plots
    plot_scenario_comparison()
    print("    - fig_01_scenario_comparison.pdf/png")
    
    plot_optimization_surface()
    print("    - fig_02_optimization_tradeoff.pdf/png")
    
    plot_timeline_projection()
    print("    - fig_03_timeline_projection.pdf/png")
    
    plot_sensitivity_analysis()
    print("    - fig_04_sensitivity_analysis.pdf/png")
    
    plot_water_analysis()
    print("    - fig_05_water_analysis.pdf/png")
    
    plot_launch_site_map()
    print("    - fig_06_launch_sites.pdf/png")
    
    plot_cost_breakdown()
    print("    - fig_07_cost_breakdown.pdf/png")
    
    plot_environmental_comparison()
    print("    - fig_08_environmental_impact.pdf/png")
    
    # Save results to JSON
    print("\n[6] Saving Results...")
    all_results = {
        'elevator_only': elevator_result,
        'rocket_only': rocket_result,
        'hybrid': hybrid_result,
        'water_requirement': water_result,
        'parameters': {
            'total_material_mt': TOTAL_MATERIAL,
            'colony_population': COLONY_POPULATION,
            'start_year': START_YEAR,
            'elevator_capacity_per_harbour': ELEVATOR_CAPACITY_PER_HARBOUR,
            'n_galactic_harbours': N_GALACTIC_HARBOURS,
            'rocket_payload_mt': ROCKET_PAYLOAD,
            'elevator_cost_per_kg': ELEVATOR_COST_PER_KG,
            'rocket_cost_per_kg': ROCKET_COST_PER_KG,
        }
    }
    
    with open('../results/model_results.json', 'w') as f:
        json.dump(all_results, f, indent=2, default=str)
    print("    - model_results.json saved")
    
    print("\n" + "=" * 60)
    print("Analysis Complete!")
    print("=" * 60)
