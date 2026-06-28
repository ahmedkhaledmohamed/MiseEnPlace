import SwiftUI
import SwiftData

struct GroceryItem: Identifiable {
    let id: String
    let name: String
    let category: String
    let totalQuantity: Double
    let unit: String
    let cost: Double?
    let mealNames: [String]
    var isChecked: Bool = false
}

struct GroceryListView: View {
    @Query private var allMeals: [Meal]
    @Query private var entries: [PlanEntry]
    @Query private var pantryItems: [PantryItem]
    @State private var checkedItems: Set<String> = []

    private var weekStart: Date {
        Calendar.current.dateInterval(of: .weekOfYear, for: .now)?.start ?? .now
    }

    private var weekEntries: [PlanEntry] {
        entries.filter { Calendar.current.isDate($0.weekStart, equalTo: weekStart, toGranularity: .weekOfYear) }
    }

    private var groceryItems: [String: [GroceryItem]] {
        let pantryNames = Set(pantryItems.map { $0.name.lowercased() })
        let mealIds = Set(weekEntries.map(\.mealId))
        let plannedMeals = allMeals.filter { mealIds.contains($0.id) }

        var grouped: [String: (Double, String, Double?, [String], String)] = [:]

        for meal in plannedMeals {
            for ing in meal.ingredients {
                let key = ing.name.lowercased()
                if pantryNames.contains(key) { continue }
                if let existing = grouped[key] {
                    grouped[key] = (
                        existing.0 + ing.quantity,
                        ing.unit,
                        existing.2 ?? ing.cost,
                        existing.3 + [meal.name],
                        ing.category
                    )
                } else {
                    grouped[key] = (ing.quantity, ing.unit, ing.cost, [meal.name], ing.category)
                }
            }
        }

        let items = grouped.map { key, val in
            GroceryItem(
                id: key, name: key.capitalized,
                category: sectionForCategory(val.4),
                totalQuantity: val.0, unit: val.1,
                cost: val.2, mealNames: val.3
            )
        }
        .sorted { $0.name < $1.name }

        return Dictionary(grouping: items, by: \.category)
    }

    private var totalCost: Double {
        groceryItems.values.flatMap { $0 }.compactMap(\.cost).reduce(0, +)
    }

    private var totalItems: Int {
        groceryItems.values.flatMap { $0 }.count
    }

    var body: some View {
        NavigationStack {
            Group {
                if weekEntries.isEmpty {
                    VStack(spacing: 12) {
                        Image(systemName: "cart")
                            .font(.system(size: 40))
                            .foregroundStyle(Theme.textMuted)
                        Text("Plan meals first")
                            .font(.headline)
                        Text("Add meals to your weekly plan to generate a grocery list")
                            .font(.subheadline)
                            .foregroundStyle(Theme.textMuted)
                            .multilineTextAlignment(.center)
                    }
                    .padding()
                } else {
                    List {
                        ForEach(sectionOrder, id: \.self) { section in
                            if let items = groceryItems[section], !items.isEmpty {
                                Section(section) {
                                    ForEach(items) { item in
                                        GroceryRow(
                                            item: item,
                                            isChecked: checkedItems.contains(item.id),
                                            onToggle: {
                                                if checkedItems.contains(item.id) {
                                                    checkedItems.remove(item.id)
                                                } else {
                                                    checkedItems.insert(item.id)
                                                }
                                            }
                                        )
                                    }
                                }
                            }
                        }

                        Section {
                            HStack {
                                Text("\(totalItems) items")
                                Spacer()
                                Text(String(format: "~$%.2f", totalCost))
                                    .fontWeight(.semibold)
                            }
                            .foregroundStyle(Theme.textMuted)
                        }
                    }
                    .listStyle(.insetGrouped)
                }
            }
            .background(Theme.bg)
            .navigationTitle("Grocery List")
        }
    }

    private let sectionOrder = [
        "Produce", "Protein", "Dairy", "Grains & Pasta",
        "Spices & Herbs", "Oils & Sauces", "Other",
    ]

    private func sectionForCategory(_ category: String) -> String {
        switch category {
        case "vegetable", "fruit", "herb": return "Produce"
        case "protein", "legume": return "Protein"
        case "dairy": return "Dairy"
        case "grain": return "Grains & Pasta"
        case "spice": return "Spices & Herbs"
        case "oil-fat", "sauce-condiment", "liquid": return "Oils & Sauces"
        default: return "Other"
        }
    }
}

struct GroceryRow: View {
    let item: GroceryItem
    let isChecked: Bool
    let onToggle: () -> Void

    var body: some View {
        Button(action: onToggle) {
            HStack {
                Image(systemName: isChecked ? "checkmark.circle.fill" : "circle")
                    .foregroundStyle(isChecked ? Theme.green : Theme.textMuted)

                VStack(alignment: .leading, spacing: 2) {
                    Text(item.name)
                        .font(.subheadline)
                        .strikethrough(isChecked)
                        .foregroundStyle(isChecked ? Theme.textMuted : Theme.text)
                    Text(item.mealNames.joined(separator: ", "))
                        .font(.caption2)
                        .foregroundStyle(Theme.textMuted)
                        .lineLimit(1)
                }

                Spacer()

                Text("\(item.totalQuantity, specifier: "%g") \(item.unit)")
                    .font(.caption)
                    .foregroundStyle(Theme.textMuted)
                    .monospacedDigit()
            }
        }
        .buttonStyle(.plain)
    }
}
