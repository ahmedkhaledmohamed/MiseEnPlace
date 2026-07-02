import SwiftUI
import SwiftData

struct SeededRNG: RandomNumberGenerator {
    private var state: UInt64
    init(seed: UInt64) { self.state = seed }
    mutating func next() -> UInt64 {
        state &+= 0x9e3779b97f4a7c15
        var z = state
        z = (z ^ (z >> 30)) &* 0xbf58476d1ce4e5b9
        z = (z ^ (z >> 27)) &* 0x94d049bb133111eb
        return z ^ (z >> 31)
    }
}

struct FeedView: View {
    @Environment(\.modelContext) private var context
    @Query private var allMeals: [Meal]
    @Query private var seenMeals: [SeenMeal]
    @State private var searchText = ""
    @State private var showSearch = false
    @State private var selectedCuisine: String?
    @State private var selectedType: String?
    @State private var selectedDifficulty: String?
    @State private var navigationPath = NavigationPath()
    @State private var sessionSeed: UInt64 = UInt64.random(in: 0...UInt64.max)

    private var orderedMeals: [Meal] {
        let seenIds = Set(seenMeals.map(\.mealId))

        var unseen = allMeals.filter { !seenIds.contains($0.id) }
        var seen = allMeals.filter { seenIds.contains($0.id) }

        if unseen.isEmpty {
            try? context.delete(model: SeenMeal.self)
            unseen = allMeals
            seen = []
        }

        var rng = SeededRNG(seed: sessionSeed)
        unseen.shuffle(using: &rng)
        var rng2 = SeededRNG(seed: sessionSeed &+ 1)
        seen.shuffle(using: &rng2)

        return unseen + seen
    }

    private var filteredMeals: [Meal] {
        orderedMeals.filter { meal in
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
        NavigationStack(path: $navigationPath) {
            VStack(spacing: 0) {
                feedHeader

                ScrollView {
                    LazyVStack(spacing: 2) {
                        ForEach(filteredMeals, id: \.id) { meal in
                            MealCard(meal: meal) {
                                navigationPath.append(meal.id)
                            }
                            .onAppear { markSeen(meal) }
                        }
                    }
                    .padding(.bottom, 20)
                }
            }
            .background(Theme.bg)
            .navigationBarHidden(true)
            .navigationDestination(for: String.self) { mealId in
                MealDetailView(mealId: mealId)
            }
        }
    }

    private func markSeen(_ meal: Meal) {
        guard !seenMeals.contains(where: { $0.mealId == meal.id }) else { return }
        context.insert(SeenMeal(mealId: meal.id))
    }

    private var feedHeader: some View {
        VStack(spacing: 0) {
            HStack {
                Text("Potluck")
                    .font(.system(size: 28, weight: .bold, design: .serif))

                Spacer()

                Button {
                    withAnimation(.easeInOut(duration: 0.2)) {
                        showSearch.toggle()
                        if !showSearch { searchText = "" }
                    }
                } label: {
                    Image(systemName: showSearch ? "xmark.circle.fill" : "magnifyingglass")
                        .font(.system(size: 18))
                        .foregroundStyle(Theme.textMuted)
                        .frame(width: 36, height: 36)
                }

                filterMenu
            }
            .padding(.horizontal, 16)
            .padding(.top, 8)
            .padding(.bottom, showSearch ? 4 : 12)

            if showSearch {
                HStack {
                    Image(systemName: "magnifyingglass")
                        .foregroundStyle(Theme.textMuted)
                    TextField("Search meals or ingredients", text: $searchText)
                        .font(.subheadline)
                }
                .padding(.horizontal, 12)
                .padding(.vertical, 8)
                .background(Theme.surface)
                .clipShape(RoundedRectangle(cornerRadius: 10))
                .padding(.horizontal, 16)
                .padding(.bottom, 10)
                .transition(.move(edge: .top).combined(with: .opacity))
            }
        }
    }

    private var filterMenu: some View {
        Menu {
            Section("Cuisine") {
                Button("All Cuisines") { selectedCuisine = nil }
                ForEach(cuisines, id: \.self) { c in
                    Button {
                        selectedCuisine = c
                    } label: {
                        if selectedCuisine == c {
                            Label(c, systemImage: "checkmark")
                        } else {
                            Text(c)
                        }
                    }
                }
            }
            Section("Type") {
                Button("All Types") { selectedType = nil }
                ForEach(mealTypes, id: \.self) { t in
                    Button {
                        selectedType = t
                    } label: {
                        if selectedType == t {
                            Label(t, systemImage: "checkmark")
                        } else {
                            Text(t)
                        }
                    }
                }
            }
            Section("Difficulty") {
                Button("All") { selectedDifficulty = nil }
                ForEach(difficulties, id: \.self) { d in
                    Button {
                        selectedDifficulty = d
                    } label: {
                        if selectedDifficulty == d {
                            Label(d, systemImage: "checkmark")
                        } else {
                            Text(d)
                        }
                    }
                }
            }
        } label: {
            Image(systemName: "slider.horizontal.3")
                .font(.system(size: 18))
                .foregroundStyle(hasActiveFilter ? Theme.accent : Theme.textMuted)
                .frame(width: 36, height: 36)
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
