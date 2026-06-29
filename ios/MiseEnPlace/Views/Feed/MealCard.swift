import SwiftUI

struct MealCard: View {
    let meal: Meal

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            ZStack {
                MealImage(imageUrl: meal.imageUrl, cuisine: meal.cuisine, height: 420)

                LinearGradient(
                    colors: [.black.opacity(0.6), .clear],
                    startPoint: .top,
                    endPoint: UnitPoint(x: 0.5, y: 0.3)
                )

                LinearGradient(
                    colors: [.clear, .black.opacity(0.5)],
                    startPoint: UnitPoint(x: 0.5, y: 0.75),
                    endPoint: .bottom
                )

                VStack {
                    HStack {
                        VStack(alignment: .leading, spacing: 4) {
                            CuisinePill(cuisine: meal.cuisine)
                            Text(meal.name)
                                .font(.system(size: 20, weight: .bold, design: .serif))
                                .foregroundStyle(.white)
                                .lineLimit(2)
                        }
                        Spacer()
                    }

                    Spacer()

                    HStack {
                        Text("\(meal.totalTime) min · \(String(format: "$%.2f", meal.costPerServing)) · \(meal.difficulty)")
                            .font(.caption)
                            .fontWeight(.semibold)
                            .foregroundStyle(.white)
                            .padding(.horizontal, 10)
                            .padding(.vertical, 5)
                            .background(.black.opacity(0.6))
                            .clipShape(Capsule())
                        Spacer()
                    }
                }
                .padding(14)
            }
            .frame(height: 420)
            .clipped()

            VStack(alignment: .leading, spacing: 8) {
                MealActions(meal: meal, iconSize: 22, tint: Theme.text)

                Text(meal.desc)
                    .font(.subheadline)
                    .foregroundStyle(Theme.text)
                    .lineLimit(2)
            }
            .padding(.horizontal, 14)
            .padding(.vertical, 10)
        }
    }
}
