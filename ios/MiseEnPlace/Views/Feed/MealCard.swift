import SwiftUI

struct MealCard: View {
    let meal: Meal

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            ZStack(alignment: .bottomLeading) {
                MealImage(imageName: meal.imageName, cuisine: meal.cuisine, height: 200)

                LinearGradient(
                    colors: [.clear, .black.opacity(0.7)],
                    startPoint: .center,
                    endPoint: .bottom
                )

                VStack(alignment: .leading, spacing: 4) {
                    CuisinePill(cuisine: meal.cuisine)
                    Text(meal.name)
                        .font(.title3)
                        .fontWeight(.bold)
                        .foregroundStyle(.white)
                }
                .padding(12)
            }

            HStack(spacing: 16) {
                StatBadge(icon: "clock", value: "\(meal.totalTime) min")
                StatBadge(icon: "dollarsign.circle", value: String(format: "$%.2f", meal.costPerServing))
                StatBadge(icon: "flame", value: meal.difficulty)
                Spacer()
                StatBadge(icon: "person.2", value: "\(meal.servings)")
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 10)
            .background(Theme.cardBg)
        }
        .clipShape(RoundedRectangle(cornerRadius: 12))
        .overlay(
            RoundedRectangle(cornerRadius: 12)
                .stroke(Theme.border, lineWidth: 1)
        )
    }
}
