import SwiftUI
import SwiftData

struct PantryView: View {
    @Query(sort: \Meal.name) private var allMeals: [Meal]
    @State private var selectedIngredients: Set<String> = []
    @State private var searchText = ""
    @State private var navigationPath = NavigationPath()

    private var allIngredients: [(name: String, category: String, count: Int)] {
        var map: [String: (category: String, count: Int)] = [:]
        for meal in allMeals {
            for ing in meal.ingredients where !ing.isOptional {
                let key = ing.name.lowercased()
                if let existing = map[key] {
                    map[key] = (existing.category, existing.count + 1)
                } else {
                    map[key] = (ing.category, 1)
                }
            }
        }
        return map.map { (name: $0.key, category: $0.value.category, count: $0.value.count) }
            .sorted { $0.count > $1.count }
    }

    private var filteredIngredients: [(name: String, category: String, count: Int)] {
        if searchText.isEmpty { return allIngredients.filter { $0.count >= 3 } }
        let q = searchText.lowercased()
        return allIngredients.filter { $0.name.contains(q) }
    }

    private var matchedMeals: [(meal: Meal, matched: Int, total: Int, missing: [String])] {
        guard !selectedIngredients.isEmpty else { return [] }
        return allMeals.compactMap { meal in
            let required = meal.ingredients.filter { !$0.isOptional }
            let matched = required.filter { selectedIngredients.contains($0.name.lowercased()) }.count
            let missing = required.filter { !selectedIngredients.contains($0.name.lowercased()) }.map(\.name)
            guard matched > 0 else { return nil }
            return (meal: meal, matched: matched, total: required.count, missing: missing)
        }
        .sorted { Double($0.matched) / Double($0.total) > Double($1.matched) / Double($1.total) }
    }

    private let categoryOrder = ["protein", "vegetable", "grain", "dairy", "fruit",
                                  "herb", "spice", "sauce-condiment", "oil-fat", "legume",
                                  "nut-seed", "sweetener", "liquid", "other"]

    var body: some View {
        NavigationStack(path: $navigationPath) {
            VStack(spacing: 0) {
                header
                content
            }
            .background(Theme.bg)
            .navigationBarHidden(true)
            .navigationDestination(for: String.self) { mealId in
                MealDetailView(mealId: mealId)
            }
        }
    }

    private var header: some View {
        VStack(spacing: 8) {
            HStack {
                Text("What can I cook?")
                    .font(.system(size: 24, weight: .bold, design: .serif))
                Spacer()
                if !selectedIngredients.isEmpty {
                    Button("Clear") {
                        selectedIngredients.removeAll()
                    }
                    .font(.caption)
                    .foregroundStyle(Theme.accent)
                }
            }

            HStack {
                Image(systemName: "magnifyingglass")
                    .foregroundStyle(Theme.textMuted)
                TextField("Search ingredients...", text: $searchText)
                    .font(.subheadline)
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 8)
            .background(Theme.surface)
            .clipShape(RoundedRectangle(cornerRadius: 10))

            if !selectedIngredients.isEmpty {
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 6) {
                        ForEach(Array(selectedIngredients).sorted(), id: \.self) { ing in
                            Button {
                                selectedIngredients.remove(ing)
                            } label: {
                                HStack(spacing: 4) {
                                    Text(ing)
                                        .font(.caption)
                                    Image(systemName: "xmark")
                                        .font(.system(size: 8, weight: .bold))
                                }
                                .padding(.horizontal, 10)
                                .padding(.vertical, 5)
                                .background(Theme.accent.opacity(0.2))
                                .foregroundStyle(Theme.accent)
                                .clipShape(Capsule())
                            }
                        }
                    }
                }
            }
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 10)
    }

    @ViewBuilder
    private var content: some View {
        if selectedIngredients.isEmpty {
            ingredientPicker
        } else {
            mealResults
        }
    }

    private var ingredientPicker: some View {
        ScrollView {
            LazyVStack(alignment: .leading, spacing: 16) {
                ForEach(categoryOrder, id: \.self) { category in
                    let items = filteredIngredients.filter { $0.category == category }
                    if !items.isEmpty {
                        VStack(alignment: .leading, spacing: 6) {
                            Text(category.replacingOccurrences(of: "-", with: " ").capitalized)
                                .font(.caption)
                                .fontWeight(.semibold)
                                .foregroundStyle(Theme.textMuted)

                            FlowLayout(spacing: 6) {
                                ForEach(items, id: \.name) { item in
                                    let selected = selectedIngredients.contains(item.name)
                                    Button {
                                        if selected {
                                            selectedIngredients.remove(item.name)
                                        } else {
                                            selectedIngredients.insert(item.name)
                                        }
                                    } label: {
                                        HStack(spacing: 4) {
                                            Circle()
                                                .fill(Theme.categoryColor(item.category))
                                                .frame(width: 6, height: 6)
                                            Text(item.name)
                                                .font(.caption)
                                        }
                                        .padding(.horizontal, 10)
                                        .padding(.vertical, 6)
                                        .background(selected ? Theme.accent.opacity(0.2) : Theme.surface)
                                        .foregroundStyle(selected ? Theme.accent : Theme.text)
                                        .clipShape(Capsule())
                                        .overlay(
                                            Capsule().stroke(selected ? Theme.accent : Theme.border, lineWidth: 1)
                                        )
                                    }
                                }
                            }
                        }
                    }
                }
            }
            .padding(.horizontal, 16)
            .padding(.bottom, 20)
        }
    }

    private var mealResults: some View {
        ScrollView {
            LazyVStack(spacing: 12) {
                Text("\(matchedMeals.count) meals match")
                    .font(.caption)
                    .foregroundStyle(Theme.textMuted)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(.horizontal, 16)

                ForEach(matchedMeals.prefix(30), id: \.meal.id) { result in
                    Button {
                        navigationPath.append(result.meal.id)
                    } label: {
                        HStack(spacing: 12) {
                            MealImage(imageUrl: result.meal.imageUrl, cuisine: result.meal.cuisine, height: 70)
                                .frame(width: 70)
                                .clipShape(RoundedRectangle(cornerRadius: 8))

                            VStack(alignment: .leading, spacing: 4) {
                                Text(result.meal.name)
                                    .font(.subheadline)
                                    .fontWeight(.medium)
                                    .foregroundStyle(Theme.text)
                                    .lineLimit(1)

                                ProgressView(value: Double(result.matched), total: Double(result.total))
                                    .tint(result.matched == result.total ? Theme.green : Theme.accent)

                                Text("You have \(result.matched)/\(result.total) ingredients")
                                    .font(.caption2)
                                    .foregroundStyle(Theme.textMuted)

                                if !result.missing.isEmpty {
                                    Text("Need: \(result.missing.prefix(3).joined(separator: ", "))")
                                        .font(.caption2)
                                        .foregroundStyle(Theme.accent)
                                        .lineLimit(1)
                                }
                            }

                            Spacer()
                        }
                        .padding(.horizontal, 16)
                    }
                    .buttonStyle(.plain)
                }
            }
            .padding(.bottom, 20)
        }
    }
}

struct FlowLayout: Layout {
    var spacing: CGFloat = 6

    func sizeThatFits(proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) -> CGSize {
        let result = layout(proposal: proposal, subviews: subviews)
        return result.size
    }

    func placeSubviews(in bounds: CGRect, proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) {
        let result = layout(proposal: proposal, subviews: subviews)
        for (index, position) in result.positions.enumerated() {
            subviews[index].place(at: CGPoint(x: bounds.minX + position.x, y: bounds.minY + position.y), proposal: .unspecified)
        }
    }

    private func layout(proposal: ProposedViewSize, subviews: Subviews) -> (size: CGSize, positions: [CGPoint]) {
        let maxWidth = proposal.width ?? .infinity
        var positions: [CGPoint] = []
        var x: CGFloat = 0
        var y: CGFloat = 0
        var rowHeight: CGFloat = 0

        for subview in subviews {
            let size = subview.sizeThatFits(.unspecified)
            if x + size.width > maxWidth && x > 0 {
                x = 0
                y += rowHeight + spacing
                rowHeight = 0
            }
            positions.append(CGPoint(x: x, y: y))
            rowHeight = max(rowHeight, size.height)
            x += size.width + spacing
        }

        return (CGSize(width: maxWidth, height: y + rowHeight), positions)
    }
}
