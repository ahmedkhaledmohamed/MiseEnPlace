import SwiftUI
import SwiftData

struct SimilarMealsCard: View {
    let meal: Meal
    var onTapMeal: ((String) -> Void)? = nil

    @Query private var allMeals: [Meal]
    @Query private var similarities: [MealSimilarity]

    private var topSimilar: [(meal: Meal, shared: Int, ingredients: [String])] {
        similarities
            .filter { $0.mealAId == meal.id || $0.mealBId == meal.id }
            .sorted { $0.overlapRatio > $1.overlapRatio }
            .prefix(5)
            .compactMap { sim in
                let otherId = sim.mealAId == meal.id ? sim.mealBId : sim.mealAId
                guard let other = allMeals.first(where: { $0.id == otherId }) else { return nil }
                return (meal: other, shared: sim.sharedCount, ingredients: sim.sharedIngredients)
            }
    }

    var body: some View {
        if !topSimilar.isEmpty {
            VStack(alignment: .leading, spacing: 8) {
                Text("You might also like")
                    .font(.caption)
                    .fontWeight(.semibold)
                    .foregroundStyle(Theme.textMuted)
                    .padding(.horizontal, 14)

                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 10) {
                        ForEach(topSimilar, id: \.meal.id) { item in
                            Button {
                                onTapMeal?(item.meal.id)
                            } label: {
                                VStack(alignment: .leading, spacing: 4) {
                                    MealImage(imageUrl: item.meal.imageUrl, cuisine: item.meal.cuisine, height: 100)
                                        .frame(width: 140)
                                        .clipShape(RoundedRectangle(cornerRadius: 8))

                                    Text(item.meal.name)
                                        .font(.caption)
                                        .fontWeight(.medium)
                                        .foregroundStyle(Theme.text)
                                        .lineLimit(1)

                                    Text("\(item.shared) shared: \(item.ingredients.prefix(3).joined(separator: ", "))")
                                        .font(.system(size: 10))
                                        .foregroundStyle(Theme.accent)
                                        .lineLimit(1)
                                }
                                .frame(width: 140)
                            }
                            .buttonStyle(.plain)
                        }
                    }
                    .padding(.horizontal, 14)
                }
            }
            .padding(.vertical, 8)
        }
    }
}
