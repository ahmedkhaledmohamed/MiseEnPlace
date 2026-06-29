import SwiftUI
import SwiftData

struct SimilarMealsRow: View {
    let mealIds: [String]
    @Query private var allMeals: [Meal]

    private var similarMeals: [Meal] {
        mealIds.compactMap { id in allMeals.first(where: { $0.id == id }) }
    }

    var body: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 10) {
                ForEach(similarMeals, id: \.id) { meal in
                    NavigationLink(value: meal.id) {
                        VStack(alignment: .leading, spacing: 4) {
                            MealImage(imageUrl: meal.imageUrl, cuisine: meal.cuisine, height: 80)
                                .frame(width: 120)
                                .clipShape(RoundedRectangle(cornerRadius: 8))
                            Text(meal.name)
                                .font(.caption)
                                .fontWeight(.medium)
                                .lineLimit(2)
                                .foregroundStyle(Theme.text)
                            Text(meal.cuisine)
                                .font(.caption2)
                                .foregroundStyle(Theme.textMuted)
                        }
                        .frame(width: 120)
                    }
                    .buttonStyle(.plain)
                }
            }
        }
    }
}
