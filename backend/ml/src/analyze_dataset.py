from data_generator import (
    load_affinity_matrix,
    generate_dataset
)


def main():

    affinity_matrix = load_affinity_matrix()

    # 100 étudiants par parcours
    df = generate_dataset(
        affinity_matrix,
        students_per_class=100,
        seed=42
    )

    print("Dimensions du dataset :")
    print(df.shape)

    print("\nNombre d'étudiants par parcours :")
    print(df["parcours"].value_counts())

    print("\nMoyennes par parcours :")
    means = df.groupby("parcours").mean(numeric_only=True)

    print(means.round(2))


if __name__ == "__main__":
    main()