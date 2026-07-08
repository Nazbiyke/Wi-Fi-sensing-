import os
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdates




# MAE heatmap for each router, with eps on x-axis and alpha on y-axis
#--------------------------------------------------------------------------------


def create_output_folder():

    os.makedirs("results/figures", exist_ok=True)


def plot_mae_heatmap(

    router_number,

    mae_grid,

    eps_values,

    alpha_values,

    best_eps,

    best_alpha

):

    plt.figure(
        figsize=(8, 6)
    )

    # ----------------------------------------
    # Build scatter coordinates
    # ----------------------------------------

    eps_points = []

    alpha_points = []

    mae_points = []

    for alpha_index, alpha in enumerate(alpha_values):

        for eps_index, eps in enumerate(eps_values):

            eps_points.append(
                eps
            )

            alpha_points.append(
                alpha
            )

            mae_points.append(
                mae_grid[alpha_index, eps_index]
            )

    # ----------------------------------------
    # Scatter plot
    # ----------------------------------------

    scatter = plt.scatter(

        eps_points,

        alpha_points,

        c=mae_points,

        cmap="viridis",

        s=70

    )

    # ----------------------------------------
    # Best parameter combination
    # ----------------------------------------

    plt.scatter(

        best_eps,

        best_alpha,

        marker="*",

        s=250,

        color="black",

        edgecolors="white",

        linewidth=1.5,

        label="Best Parameter Pair"

    )

    # ----------------------------------------
    # Colorbar
    # ----------------------------------------

    plt.colorbar(

        scatter,

        label="MAE"

    )

    # ----------------------------------------
    # Axes
    # ----------------------------------------

    plt.xticks(
        eps_values
    )

    plt.yticks(
        alpha_values[::10]
    )

    plt.xlabel(
        r"$\varepsilon$"
    )

    plt.ylabel(
        r"$\alpha$"
    )

    plt.title(

        f"Grid Search Results: Router {router_number}"

    )

    plt.grid(
        alpha=0.3
    )

    plt.legend()

    plt.tight_layout()

    plt.savefig(

        f"results/figures/router_{router_number}_grid_search.png",

        dpi=300

    )

    plt.close()





# DEVICE-FREE VS DEVICE-BASED OCCUPANCY CURVES OVER TIME 
#-------------------------------------------------------------  

def plot_occupancy_comparison(

    router_number,

    window_times,

    db_occupancies,

    df_occupancies

):

    plt.figure(
        figsize=(10,5)
    )

    plt.plot(

        window_times,

        db_occupancies,

        label="Device-based",

        linewidth=2

    )

    plt.plot(

        window_times,

        df_occupancies,

        label="Device-free",

        linewidth=2

    )

    plt.xlabel(
        "Time"
    )

    plt.ylabel(
        "Estimated occupancy"
    )

    plt.title(
        f"Occupancy Comparison: Router {router_number}"
    )

    plt.legend()

    plt.grid(alpha=0.3)

    plt.gca().xaxis.set_major_formatter(
        mdates.DateFormatter("%H:%M")
    )

    plt.xticks(rotation=45)

    plt.tight_layout()

    plt.savefig(

        f"results/figures/router_{router_number}_occupancy_comparison.png",

        dpi=300

    )

    plt.close()




# the beacon RSSI variance on x-axis and the occupancy on y-axis (both DB and DF, distance betweent them is the MAE )
#--------------------------------------------------------------------------------


def plot_variance_occupancy_relationship(results):

    fig, axes = plt.subplots(
        2,
        2,
        figsize=(12, 10)
    )

    for i, (ax, (router, data)) in enumerate(
        zip(axes.flatten(), results.items()),
        start=1
    ):

        variances = np.array(
            data["variances"]
        )

        db_occupancies = np.array(
            data["db_occupancies"]
        )

        df_occupancies = np.array(
            data["df_occupancies"]
        )

        alpha = data["best_alpha"]

        # ----------------------------------------
        # Device-based occupancy
        # ----------------------------------------

        ax.scatter(
            variances,
            db_occupancies,
            s=20,
            alpha=0.7,
            label="Device-based"
        )

        # ----------------------------------------
        # Device-free occupancy
        # ----------------------------------------

        ax.scatter(
            variances,
            df_occupancies,
            s=20,
            alpha=0.7,
            marker="x",
            label="Device-free"
        )

        # ----------------------------------------
        # Plot formatting
        # ----------------------------------------

        ax.set_title(
            f"Router {i} (α = {alpha:.2f})"
        )

        ax.grid(
            alpha=0.3
        )

        ax.legend()

    # ----------------------------------------
    # Common figure labels
    # ----------------------------------------

    fig.supxlabel(
        "Beacon RSSI Variance",
        fontsize=12
    )

    fig.supylabel(
        "Estimated Occupancy",
        fontsize=12
    )

    fig.suptitle(
        "Variance–Occupancy Relationship",
        fontsize=14,
        fontweight="bold"
    )

    plt.tight_layout(
        rect=[0, 0.03, 1, 0.96]
    )

    plt.savefig(
        "results/figures/variance_occupancy_relationship.png",
        dpi=300
    )

    plt.close()





# number windows(frequency ) having a specific occupancy (Since the DB is the weak ground thruth then we will do that )
#--------------------------------------------------------------------------------



def plot_occupancy_distribution(results):

    fig, axes = plt.subplots(
        2,
        2,
        figsize=(12, 10)
    )

    for i, (ax, (router, data)) in enumerate(
        zip(axes.flatten(), results.items()),
        start=1
    ):

        db_occupancies = np.array(
            data["db_occupancies"]
        )

        # ----------------------------------------
        # Integer-width bins
        # ----------------------------------------

        bins = np.arange(

            db_occupancies.min(),

            db_occupancies.max() + 2

        ) - 0.5

        ax.hist(

            db_occupancies,

            bins=bins,

            alpha=0.8

        )

        ax.set_title(

            f"Router {i}"

        )

        ax.grid(

            alpha=0.3

        )

    # ----------------------------------------
    # Common figure labels
    # ----------------------------------------

    fig.supxlabel(

        "Estimated Device-based Occupancy",

        fontsize=12

    )

    fig.supylabel(

        "Number of Windows",

        fontsize=12

    )

    fig.suptitle(

        "Distribution of Device-based Occupancy Estimates",

        fontsize=14,

        fontweight="bold"

    )

    plt.tight_layout(

        rect=[0, 0.03, 1, 0.96]

    )

    plt.savefig(

        "results/figures/occupancy_distribution.png",

        dpi=300

    )

    plt.close()



# Finally the bar chart showing the MAE of each router, with the best alpha and eps values 
#---------------------------------------------------------------------------------



def plot_router_mae(results):

    routers = []

    maes = []

    for i, (router, data) in enumerate(

        results.items(),

        start=1

    ):

        routers.append(

            f"Router {i}"

        )

        maes.append(

            data["best_mae"]

        )

    plt.figure(

        figsize=(8,5)

    )

    plt.bar(

        routers,

        maes

    )

    plt.xlabel(

        "Router"

    )

    plt.ylabel(

        "Minimum MAE"

    )

    plt.title(

        "Minimum Mean Absolute Error for Each Router"

    )

    plt.grid(

        axis="y",

        alpha=0.3

    )

    plt.tight_layout()

    plt.savefig(

        "results/figures/router_mae_comparison.png",

        dpi=300

    )

    plt.close()