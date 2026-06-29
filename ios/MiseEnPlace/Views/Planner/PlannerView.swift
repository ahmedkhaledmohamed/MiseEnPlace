import SwiftUI
import SwiftData

struct PlannerView: View {
    @Environment(\.modelContext) private var context
    @Query private var allMeals: [Meal]
    @Query private var entries: [PlanEntry]
    @State private var budget: Double = 80.0
    @State private var showBudgetEditor = false

    private let days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    private let slots = ["breakfast", "lunch", "dinner"]

    private var weekStart: Date {
        Calendar.current.dateInterval(of: .weekOfYear, for: .now)?.start ?? .now
    }

    private var weekEntries: [PlanEntry] {
        entries.filter { Calendar.current.isDate($0.weekStart, equalTo: weekStart, toGranularity: .weekOfYear) }
    }

    private var groceryCost: Double {
        let mealIds = Set(weekEntries.map(\.mealId))
        var ingredientCosts: [String: Double] = [:]
        for meal in allMeals where mealIds.contains(meal.id) {
            for ing in meal.ingredients {
                if let cost = ing.cost, ingredientCosts[ing.name] == nil {
                    ingredientCosts[ing.name] = cost
                }
            }
        }
        return ingredientCosts.values.reduce(0, +)
    }

    var body: some View {
        NavigationStack {
            VStack(spacing: 0) {
                BudgetBar(spent: groceryCost, budget: budget) {
                    showBudgetEditor = true
                }
                .padding()

                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 12) {
                        ForEach(0..<7, id: \.self) { dayIndex in
                            DayColumn(
                                dayLabel: days[dayIndex],
                                entries: weekEntries.filter { $0.dayIndex == dayIndex },
                                allMeals: allMeals,
                                onRemove: { entry in
                                    context.delete(entry)
                                }
                            )
                        }
                    }
                    .padding(.horizontal)
                    .padding(.bottom, 20)
                }
            }
            .background(Theme.bg)
            .navigationTitle("Weekly Plan")
            .alert("Weekly Budget", isPresented: $showBudgetEditor) {
                TextField("Budget", value: $budget, format: .currency(code: "CAD"))
                Button("Done") {}
            }
        }
    }
}

struct BudgetBar: View {
    let spent: Double
    let budget: Double
    let onTap: () -> Void

    private var ratio: Double { min(spent / max(budget, 1), 1.0) }
    private var color: Color {
        ratio < 0.8 ? Theme.green : ratio < 1.0 ? .orange : Theme.red
    }

    var body: some View {
        VStack(spacing: 4) {
            HStack {
                Text(String(format: "$%.2f / $%.0f", spent, budget))
                    .font(.subheadline)
                    .fontWeight(.semibold)
                Spacer()
                Button {
                    onTap()
                } label: {
                    Image(systemName: "pencil.circle")
                        .foregroundStyle(Theme.textMuted)
                }
            }
            GeometryReader { geo in
                ZStack(alignment: .leading) {
                    RoundedRectangle(cornerRadius: 4)
                        .fill(Theme.surface)
                    RoundedRectangle(cornerRadius: 4)
                        .fill(color)
                        .frame(width: geo.size.width * ratio)
                }
            }
            .frame(height: 8)
        }
    }
}

struct DayColumn: View {
    let dayLabel: String
    let entries: [PlanEntry]
    let allMeals: [Meal]
    let onRemove: (PlanEntry) -> Void

    private let slots = ["breakfast", "lunch", "dinner"]

    var body: some View {
        VStack(spacing: 8) {
            Text(dayLabel)
                .font(.caption)
                .fontWeight(.bold)
                .foregroundStyle(Theme.textMuted)

            ForEach(slots, id: \.self) { slot in
                if let entry = entries.first(where: { $0.mealSlot == slot }),
                   let meal = allMeals.first(where: { $0.id == entry.mealId }) {
                    VStack(spacing: 2) {
                        MealImage(imageName: meal.imageName, cuisine: meal.cuisine, height: 50)
                            .clipShape(RoundedRectangle(cornerRadius: 6))
                        Text(meal.name)
                            .font(.caption2)
                            .lineLimit(1)
                            .foregroundStyle(Theme.text)
                    }
                    .frame(width: 80)
                    .swipeActions {
                        Button(role: .destructive) {
                            onRemove(entry)
                        } label: {
                            Label("Remove", systemImage: "trash")
                        }
                    }
                } else {
                    RoundedRectangle(cornerRadius: 6)
                        .strokeBorder(Theme.border, style: StrokeStyle(lineWidth: 1, dash: [4]))
                        .frame(width: 80, height: 50)
                        .overlay {
                            Text(slot.prefix(1).uppercased())
                                .font(.caption2)
                                .foregroundStyle(Theme.textMuted)
                        }
                }
            }
        }
    }
}
