import SwiftUI
import SwiftData

struct FeedView: View {
    @Environment(\.modelContext) private var context
    @Environment(\.scenePhase) private var scenePhase
    @Query private var allMeals: [Meal]
    @Query private var favorites: [FavoriteMeal]
    @State private var rankedMealIds: [String] = []
    @State private var searchText = ""
    @State private var showSearch = false
    @State private var selectedCuisine: String?
    @State private var selectedType: String?
    @State private var selectedDifficulty: String?
    @State private var navigationPath = NavigationPath()
    @State private var firstVisibleId: String?
    @State private var hasBuiltFeed = false
    @AppStorage("feedScrollPosition") private var savedPosition: String = ""
    @AppStorage("lastActiveTimestamp") private var lastActive: Double = 0

    private var orderedMeals: [Meal] {
        if rankedMealIds.isEmpty { return allMeals }
        let lookup = Dictionary(uniqueKeysWithValues: allMeals.map { ($0.id, $0) })
        return rankedMealIds.compactMap { lookup[$0] }
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

                ScrollViewReader { proxy in
                    ScrollView {
                        LazyVStack(spacing: 2) {
                            ForEach(Array(filteredMeals.enumerated()), id: \.element.id) { index, meal in
                                MealCard(meal: meal) {
                                    navigationPath.append(meal.id)
                                }
                                .id(meal.id)
                                .onAppear {
                                    firstVisibleId = meal.id
                                    markSeen(meal)
                                    prefetchImages(around: index)
                                }
                            }
                        }
                        .padding(.bottom, 20)
                    }
                    .refreshable { await refreshFeed() }
                    .onAppear {
                        if !hasBuiltFeed && !allMeals.isEmpty {
                            buildFeed()
                            hasBuiltFeed = true
                            restoreScrollPosition(proxy: proxy)
                        }
                    }
                    .onChange(of: allMeals.count) { _, count in
                        if count > 0 && !hasBuiltFeed {
                            buildFeed()
                            hasBuiltFeed = true
                        }
                    }
                }
            }
            .background(Theme.bg)
            .navigationBarHidden(true)
            .navigationDestination(for: String.self) { mealId in
                MealDetailView(mealId: mealId)
            }
            .onChange(of: scenePhase) { _, phase in
                if phase == .background || phase == .inactive {
                    saveScrollPosition()
                }
            }
        }
    }

    private func buildFeed() {
        let seenIds: Set<String> = {
            let descriptor = FetchDescriptor<SeenMeal>()
            let seen = (try? context.fetch(descriptor)) ?? []
            return Set(seen.map(\.mealId))
        }()

        let cuisineCounts = Dictionary(grouping: favorites, by: { fav in
            allMeals.first { $0.id == fav.mealId }?.cuisine ?? ""
        }).mapValues(\.count)

        let typeCounts = Dictionary(grouping: favorites, by: { fav in
            allMeals.first { $0.id == fav.mealId }?.mealType ?? ""
        }).mapValues(\.count)

        var rng = SeededRNG(seed: UInt64.random(in: 0...UInt64.max))

        let scored = allMeals.map { meal -> (String, Double) in
            let ca = Double(cuisineCounts[meal.cuisine] ?? 0)
            let ta = Double(typeCounts[meal.mealType] ?? 0)
            let unseen: Double = seenIds.contains(meal.id) ? 0 : 1
            let jitter = Double(rng.next() % 1000) / 2000.0
            let score = (ca * 3) + (ta * 2) + (unseen * 1) + jitter
            return (meal.id, score)
        }

        rankedMealIds = scored.sorted { $0.1 > $1.1 }.map(\.0)
    }

    private func refreshFeed() async {
        buildFeed()
        savedPosition = ""
        firstVisibleId = nil
        try? await Task.sleep(for: .milliseconds(200))
    }

    private func markSeen(_ meal: Meal) {
        let mealId = meal.id
        let descriptor = FetchDescriptor<SeenMeal>(predicate: #Predicate<SeenMeal> { $0.mealId == mealId })
        let exists = (try? context.fetchCount(descriptor)) ?? 0
        if exists == 0 {
            context.insert(SeenMeal(mealId: mealId))
        }
    }

    private func saveScrollPosition() {
        if let id = firstVisibleId {
            savedPosition = id
            lastActive = Date().timeIntervalSince1970
        }
    }

    private func restoreScrollPosition(proxy: ScrollViewProxy) {
        let now = Date().timeIntervalSince1970
        if (now - lastActive) > 86400 {
            savedPosition = ""
        } else if !savedPosition.isEmpty {
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
                proxy.scrollTo(savedPosition, anchor: .top)
            }
        }
    }

    private func prefetchImages(around index: Int) {
        let meals = filteredMeals
        for i in (index + 1)...(index + 4) {
            guard i < meals.count,
                  let urlString = meals[i].imageUrl,
                  let url = URL(string: urlString) else { continue }
            URLSession.shared.dataTask(with: url) { _, _, _ in }.resume()
        }
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
                    Button { selectedCuisine = c } label: {
                        if selectedCuisine == c { Label(c, systemImage: "checkmark") } else { Text(c) }
                    }
                }
            }
            Section("Type") {
                Button("All Types") { selectedType = nil }
                ForEach(mealTypes, id: \.self) { t in
                    Button { selectedType = t } label: {
                        if selectedType == t { Label(t, systemImage: "checkmark") } else { Text(t) }
                    }
                }
            }
            Section("Difficulty") {
                Button("All") { selectedDifficulty = nil }
                ForEach(difficulties, id: \.self) { d in
                    Button { selectedDifficulty = d } label: {
                        if selectedDifficulty == d { Label(d, systemImage: "checkmark") } else { Text(d) }
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
    private var cuisines: [String] { Array(Set(allMeals.map(\.cuisine))).sorted() }
    private var mealTypes: [String] { Array(Set(allMeals.map(\.mealType))).sorted() }
    private var difficulties: [String] { ["easy", "medium", "advanced", "project"] }
}

private struct SeededRNG: RandomNumberGenerator {
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
