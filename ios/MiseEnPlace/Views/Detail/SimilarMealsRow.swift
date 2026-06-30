import SwiftUI
import SwiftData

struct SimilarMealsRow: View {
    let mealId: String
    @Query private var allMeals: [Meal]
    @Query private var similarities: [MealSimilarity]

    private var topSimilar: [(meal: Meal, shared: Int, ingredients: [String])] {
        similarities
            .filter { $0.mealAId == mealId || $0.mealBId == mealId }
            .sorted { $0.overlapRatio > $1.overlapRatio }
            .prefix(8)
            .compactMap { sim in
                let otherId = sim.mealAId == mealId ? sim.mealBId : sim.mealAId
                guard let other = allMeals.first(where: { $0.id == otherId }) else { return nil }
                return (meal: other, shared: sim.sharedCount, ingredients: sim.sharedIngredients)
            }
    }

    var body: some View {
        if !topSimilar.isEmpty {
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 10) {
                    ForEach(topSimilar, id: \.meal.id) { item in
                        NavigationLink(value: item.meal.id) {
                            VStack(alignment: .leading, spacing: 4) {
                                MealImage(imageUrl: item.meal.imageUrl, cuisine: item.meal.cuisine, height: 80)
                                    .frame(width: 130)
                                    .clipShape(RoundedRectangle(cornerRadius: 8))
                                Text(item.meal.name)
                                    .font(.caption)
                                    .fontWeight(.medium)
                                    .lineLimit(1)
                                    .foregroundStyle(Theme.text)
                                Text("\(item.shared) shared: \(item.ingredients.prefix(3).joined(separator: ", "))")
                                    .font(.system(size: 10))
                                    .foregroundStyle(Theme.accent)
                                    .lineLimit(1)
                            }
                            .frame(width: 130)
                        }
                        .buttonStyle(.plain)
                    }
                }
            }
        }
    }
}
