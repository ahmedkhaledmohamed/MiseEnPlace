import SwiftUI
import SwiftData

struct FeedView: View {
    @Environment(\.modelContext) private var context
    @Query(sort: \Meal.name) private var allMeals: [Meal]
    @State private var searchText = ""
    @State private var showSearch = false
    @State private var selectedCuisine: String?
    @State private var selectedType: String?
    @State private var selectedDifficulty: String?
    @State private var navigationPath = NavigationPath()
    @State private var headerVisible = true
    @State private var lastScrollOffset: CGFloat = 0

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
        NavigationStack(path: $navigationPath) {
            VStack(spacing: 0) {
                if headerVisible {
                    feedHeader
                        .transition(.move(edge: .top).combined(with: .opacity))
                }

                ScrollView {
                    LazyVStack(spacing: 2) {
                        ForEach(Array(filteredMeals.enumerated()), id: \.element.id) { index, meal in
                            MealCard(meal: meal) {
                                navigationPath.append(meal.id)
                            }

                            if index % 3 == 2 {
                                SimilarMealsCard(meal: meal) { mealId in
                                    navigationPath.append(mealId)
                                }
                            }
                        }
                    }
                    .padding(.bottom, 20)
                    .overlay(
                        GeometryReader { geo -> Color in
                            let offset = geo.frame(in: .global).minY
                            DispatchQueue.main.async {
                                let delta = offset - lastScrollOffset
                                if abs(delta) > 2 {
                                    if delta < -50 && headerVisible {
                                        withAnimation(.easeOut(duration: 0.25)) { headerVisible = false }
                                        lastScrollOffset = offset
                                    } else if delta > 40 && !headerVisible {
                                        withAnimation(.easeOut(duration: 0.25)) { headerVisible = true }
                                        lastScrollOffset = offset
                                    }
                                }
                            }
                            return Color.clear
                        }
                    )
                }
            }
            .background(Theme.bg)
            .navigationBarHidden(true)
            .navigationDestination(for: String.self) { mealId in
                MealDetailView(mealId: mealId)
            }
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
