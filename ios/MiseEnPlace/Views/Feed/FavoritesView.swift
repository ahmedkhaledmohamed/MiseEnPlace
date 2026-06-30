import SwiftUI
import SwiftData

struct FavoritesView: View {
    @Query private var allMeals: [Meal]
    @Query(sort: \FavoriteMeal.createdAt, order: .reverse) private var favorites: [FavoriteMeal]
    @State private var navigationPath = NavigationPath()

    private var favoriteMeals: [Meal] {
        let favIds = Set(favorites.map(\.mealId))
        return allMeals.filter { favIds.contains($0.id) }
    }

    var body: some View {
        NavigationStack(path: $navigationPath) {
            Group {
                if favoriteMeals.isEmpty {
                    VStack(spacing: 12) {
                        Image(systemName: "heart")
                            .font(.system(size: 48))
                            .foregroundStyle(Theme.textMuted)
                        Text("No favorites yet")
                            .font(.headline)
                        Text("Heart meals you love to find them here")
                            .font(.subheadline)
                            .foregroundStyle(Theme.textMuted)
                    }
                    .frame(maxHeight: .infinity)
                } else {
                    ScrollView {
                        LazyVStack(spacing: 2) {
                            ForEach(favoriteMeals, id: \.id) { meal in
                                MealCard(meal: meal) {
                                    navigationPath.append(meal.id)
                                }
                            }
                        }
                        .padding(.bottom, 20)
                    }
                }
            }
            .background(Theme.bg)
            .navigationTitle("Favorites")
            .navigationDestination(for: String.self) { mealId in
                MealDetailView(mealId: mealId)
            }
        }
    }
}
