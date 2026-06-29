import SwiftUI
import SwiftData

struct MealActions: View {
    let meal: Meal
    var iconSize: CGFloat = 24
    var spacing: CGFloat = 16

    @Environment(\.modelContext) private var context
    @Query private var favorites: [FavoriteMeal]
    @State private var showAddToPlan = false

    private var isFavorited: Bool {
        favorites.contains { $0.mealId == meal.id }
    }

    var body: some View {
        HStack(spacing: spacing) {
            Button {
                toggleFavorite()
            } label: {
                Image(systemName: isFavorited ? "heart.fill" : "heart")
                    .font(.system(size: iconSize))
                    .foregroundStyle(isFavorited ? .red : .white)
                    .contentTransition(.symbolEffect(.replace))
            }

            Button {
                showAddToPlan = true
            } label: {
                Image(systemName: "calendar.badge.plus")
                    .font(.system(size: iconSize))
                    .foregroundStyle(.white)
            }

            ShareLink(
                item: shareText,
                subject: Text(meal.name),
                message: Text(meal.desc)
            ) {
                Image(systemName: "square.and.arrow.up")
                    .font(.system(size: iconSize))
                    .foregroundStyle(.white)
            }
        }
        .sheet(isPresented: $showAddToPlan) {
            AddToPlanSheet(meal: meal)
        }
    }

    private var shareText: String {
        var text = "\(meal.name) — \(meal.cuisine)\n\(meal.desc)\n\(meal.totalTime) min · $\(String(format: "%.2f", meal.costPerServing))/serving"
        if let url = meal.imageUrl {
            text += "\n\(url)"
        }
        return text
    }

    private func toggleFavorite() {
        let impact = UIImpactFeedbackGenerator(style: .medium)
        impact.impactOccurred()

        if let existing = favorites.first(where: { $0.mealId == meal.id }) {
            context.delete(existing)
        } else {
            context.insert(FavoriteMeal(mealId: meal.id))
        }
    }
}
