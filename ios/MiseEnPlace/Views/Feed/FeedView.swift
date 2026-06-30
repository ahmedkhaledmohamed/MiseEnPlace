import SwiftUI
import SwiftData

struct FeedView: View {
    @Environment(\.modelContext) private var context
    @Query(sort: \Meal.name) private var allMeals: [Meal]
    @State private var searchText = ""
    @State private var selectedCuisine: String?
    @State private var selectedType: String?
    @State private var selectedDifficulty: String?

    private var filteredMeals: [Meal] {
        allMeals.filter { meal in
            if !searchText.isEmpty {
                let q = searchText.lowercased()
                guard meal.name.lowercased().contains(q) ||
                      meal.cuisine.lowercased().contains(q) ||
                      meal.ingredients.contains(where: { $0.name.lowercased().contains(q) })
                else { return false }
            }
            if let c = selectedCuisine, meal.cuisine != c { return false }
            if let t = selectedType, meal.mealType != t { return false }
            if let d = selectedDifficulty, meal.difficulty != d { return false }
            return true
        }
    }

    var body: some View {
        NavigationStack {
            ScrollView {
                LazyVStack(spacing: 2) {
                    ForEach(filteredMeals, id: \.id) { meal in
                        MealCard(meal: meal, onTapImage: meal.id)
                    }
                }
                .padding(.bottom, 20)
            }
            .background(Theme.bg)
            .searchable(text: $searchText, prompt: "Search meals or ingredients")
            .navigationTitle("Potluck")
            .navigationDestination(for: String.self) { mealId in
                MealDetailView(mealId: mealId)
            }
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Menu {
                        Section("Cuisine") {
                            Button("All Cuisines") { selectedCuisine = nil }
                            ForEach(cuisines, id: \.self) { c in
                                Button(c) { selectedCuisine = c }
                            }
                        }
                        Section("Type") {
                            Button("All Types") { selectedType = nil }
                            ForEach(mealTypes, id: \.self) { t in
                                Button(t) { selectedType = t }
                            }
                        }
                        Section("Difficulty") {
                            Button("All") { selectedDifficulty = nil }
                            ForEach(difficulties, id: \.self) { d in
                                Button(d) { selectedDifficulty = d }
                            }
                        }
                    } label: {
                        Image(systemName: "line.3.horizontal.decrease.circle")
                            .foregroundStyle(hasActiveFilter ? Theme.accent : Theme.textMuted)
                    }
                }
            }
        }
    }

    private var hasActiveFilter: Bool {
        selectedCuisine != nil || selectedType != nil || selectedDifficulty != nil
    }

    private var cuisines: [String] {
        Array(Set(allMeals.map(\.cuisine))).sorted()
    }

    private var mealTypes: [String] {
        Array(Set(allMeals.map(\.mealType))).sorted()
    }

    private var difficulties: [String] {
        ["easy", "medium", "advanced", "project"]
    }
}
