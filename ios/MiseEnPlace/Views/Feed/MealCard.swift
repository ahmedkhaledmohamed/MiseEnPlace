import SwiftUI

struct MealCard: View {
    let meal: Meal

    var body: some View {
        ZStack(alignment: .bottom) {
            MealImage(imageUrl: meal.imageUrl, cuisine: meal.cuisine, height: 420)

            LinearGradient(
                colors: [.clear, .clear, .black.opacity(0.8)],
                startPoint: .top,
                endPoint: .bottom
            )

            VStack(alignment: .leading, spacing: 6) {
                HStack(alignment: .bottom) {
                    CuisinePill(cuisine: meal.cuisine)
                    Spacer()
                    MealActions(meal: meal, iconSize: 22, spacing: 14)
                }

                Text(meal.name)
                    .font(.system(size: 22, weight: .bold, design: .serif))
                    .foregroundStyle(.white)
                    .lineLimit(2)

                Text("\(meal.totalTime) min · \(String(format: "$%.2f", meal.costPerServing)) · \(meal.difficulty)")
                    .font(.caption)
                    .foregroundStyle(.white.opacity(0.7))
            }
            .padding(14)
        }
        .frame(height: 420)
        .clipped()
    }
}
