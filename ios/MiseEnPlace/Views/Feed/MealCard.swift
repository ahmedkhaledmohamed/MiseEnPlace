import SwiftUI

struct MealCard: View {
    let meal: Meal

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            HStack(spacing: 8) {
                CuisinePill(cuisine: meal.cuisine)
                Text(meal.name)
                    .font(.subheadline)
                    .fontWeight(.semibold)
                    .lineLimit(1)
                Spacer()
            }
            .padding(.horizontal, 14)
            .padding(.vertical, 10)

            MealImage(imageUrl: meal.imageUrl, cuisine: meal.cuisine, height: 420)

            VStack(alignment: .leading, spacing: 6) {
                MealActions(meal: meal, iconSize: 22, tint: Theme.text)

                Text("\(meal.totalTime) min · \(String(format: "$%.2f", meal.costPerServing)) · \(meal.difficulty)")
                    .font(.caption)
                    .fontWeight(.medium)
                    .foregroundStyle(Theme.text)

                Text(meal.desc)
                    .font(.caption)
                    .foregroundStyle(Theme.textMuted)
                    .lineLimit(1)
            }
            .padding(.horizontal, 14)
            .padding(.vertical, 10)
        }
    }
}
