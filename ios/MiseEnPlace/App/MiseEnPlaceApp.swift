import SwiftUI
import SwiftData

@main
struct MiseEnPlaceApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        .modelContainer(for: [
            Meal.self, MealIngredient.self, RecipeStep.self,
            MealSimilarity.self, PlanEntry.self, PantryItem.self,
            FavoriteMeal.self,
        ])
    }
}

struct ContentView: View {
    @Environment(\.modelContext) private var context

    var body: some View {
        TabView {
            FeedView()
                .tabItem {
                    Label("Feed", systemImage: "house.fill")
                }

            FavoritesView()
                .tabItem {
                    Label("Favorites", systemImage: "heart.fill")
                }

            PlannerView()
                .tabItem {
                    Label("Planner", systemImage: "calendar")
                }

            GroceryListView()
                .tabItem {
                    Label("Grocery", systemImage: "cart.fill")
                }
        }
        .preferredColorScheme(.dark)
        .tint(Theme.accent)
        .onAppear {
            DataSeeder.seedIfNeeded(context: context)
        }
    }
}
