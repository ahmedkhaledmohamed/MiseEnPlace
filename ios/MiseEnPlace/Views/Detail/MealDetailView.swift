import SwiftUI
import SwiftData

struct MealDetailView: View {
    let mealId: String
    @Query private var meals: [Meal]
    @Query private var similarities: [MealSimilarity]
    @State private var showAddToPlan = false

    init(mealId: String) {
        self.mealId = mealId
        _meals = Query(filter: #Predicate<Meal> { $0.id == mealId })
    }

    private var meal: Meal? { meals.first }

    private var similarMealIds: [String] {
        similarities
            .filter { $0.mealAId == mealId || $0.mealBId == mealId }
            .sorted { $0.overlapRatio > $1.overlapRatio }
            .prefix(8)
            .map { $0.mealAId == mealId ? $0.mealBId : $0.mealAId }
    }

    var body: some View {
        Group {
            if let meal {
                ScrollView {
                    VStack(alignment: .leading, spacing: 0) {
                        MealImage(imageName: meal.imageName, cuisine: meal.cuisine, height: 280)

                        VStack(alignment: .leading, spacing: 16) {
                            headerSection(meal)
                            statsSection(meal)
                            dietarySection(meal)
                            ingredientsSection(meal)
                            stepsSection(meal)
                            tipsSection(meal)
                            equipmentSection(meal)
                            similarSection()
                            sourceSection(meal)
                        }
                        .padding()
                    }
                }
                .background(Theme.bg)
                .navigationBarTitleDisplayMode(.inline)
                .toolbar {
                    ToolbarItem(placement: .bottomBar) {
                        Button {
                            showAddToPlan = true
                        } label: {
                            Label("Add to Plan", systemImage: "calendar.badge.plus")
                                .frame(maxWidth: .infinity)
                                .padding(.vertical, 8)
                        }
                        .buttonStyle(.borderedProminent)
                        .tint(Theme.accent)
                    }
                }
                .sheet(isPresented: $showAddToPlan) {
                    AddToPlanSheet(meal: meal)
                }
            } else {
                ProgressView()
            }
        }
    }

    @ViewBuilder
    private func headerSection(_ meal: Meal) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack {
                CuisinePill(cuisine: meal.cuisine)
                TagPill(text: meal.difficulty, color: difficultyColor(meal.difficulty))
            }
            Text(meal.name)
                .font(.title)
                .fontWeight(.bold)
            Text(meal.desc)
                .font(.subheadline)
                .foregroundStyle(Theme.textMuted)
        }
    }

    @ViewBuilder
    private func statsSection(_ meal: Meal) -> some View {
        HStack(spacing: 12) {
            StatCard(label: "Time", value: "\(meal.totalTime) min")
            StatCard(label: "Cost", value: String(format: "$%.2f", meal.costPerServing))
            StatCard(label: "Servings", value: "\(meal.servings)")
        }
    }

    @ViewBuilder
    private func dietarySection(_ meal: Meal) -> some View {
        if !meal.dietaryTags.isEmpty {
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 6) {
                    ForEach(meal.dietaryTags, id: \.self) { tag in
                        TagPill(text: tag)
                    }
                }
            }
        }
    }

    @ViewBuilder
    private func ingredientsSection(_ meal: Meal) -> some View {
        SectionHeader(title: "Ingredients")
        VStack(spacing: 6) {
            ForEach(meal.ingredients.sorted(by: { $0.name < $1.name }), id: \.name) { ing in
                HStack {
                    Circle()
                        .fill(Theme.categoryColor(ing.category))
                        .frame(width: 8, height: 8)
                    Text(ing.name)
                        .font(.subheadline)
                        .foregroundStyle(ing.isOptional ? Theme.textMuted : Theme.text)
                        .italic(ing.isOptional)
                    if let note = ing.prepNote {
                        Text("(\(note))")
                            .font(.caption)
                            .foregroundStyle(Theme.textMuted)
                    }
                    Spacer()
                    Text("\(ing.quantity, specifier: "%g") \(ing.unit)")
                        .font(.caption)
                        .foregroundStyle(Theme.textMuted)
                        .monospacedDigit()
                }
            }
        }
    }

    @ViewBuilder
    private func stepsSection(_ meal: Meal) -> some View {
        SectionHeader(title: "Steps")
        VStack(alignment: .leading, spacing: 12) {
            ForEach(meal.steps.sorted(by: { $0.order < $1.order }), id: \.order) { step in
                HStack(alignment: .top, spacing: 10) {
                    Text("\(step.order)")
                        .font(.subheadline)
                        .fontWeight(.bold)
                        .foregroundStyle(Theme.accent)
                        .frame(width: 20)
                    Text(step.instruction)
                        .font(.subheadline)
                }
            }
        }
    }

    @ViewBuilder
    private func tipsSection(_ meal: Meal) -> some View {
        if !meal.tips.isEmpty {
            SectionHeader(title: "Tips")
            VStack(alignment: .leading, spacing: 6) {
                ForEach(meal.tips, id: \.self) { tip in
                    HStack(alignment: .top, spacing: 6) {
                        Text("•")
                            .foregroundStyle(Theme.textMuted)
                        Text(tip)
                            .font(.subheadline)
                            .foregroundStyle(Theme.textMuted)
                    }
                }
            }
        }
    }

    @ViewBuilder
    private func equipmentSection(_ meal: Meal) -> some View {
        if !meal.equipment.isEmpty {
            SectionHeader(title: "Equipment")
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 6) {
                    ForEach(meal.equipment, id: \.self) { eq in
                        Text(eq)
                            .font(.caption)
                            .padding(.horizontal, 8)
                            .padding(.vertical, 4)
                            .background(Theme.surface)
                            .clipShape(Capsule())
                    }
                }
            }
        }
    }

    @ViewBuilder
    private func similarSection() -> some View {
        if !similarMealIds.isEmpty {
            SectionHeader(title: "Similar Meals")
            SimilarMealsRow(mealIds: similarMealIds)
        }
    }

    @ViewBuilder
    private func sourceSection(_ meal: Meal) -> some View {
        if !meal.sourceInspiration.isEmpty {
            Text("Inspired by: \(meal.sourceInspiration)")
                .font(.caption)
                .italic()
                .foregroundStyle(Theme.textMuted)
                .padding(.top, 8)
        }
    }

    private func difficultyColor(_ d: String) -> Color {
        switch d {
        case "easy": return Theme.green
        case "medium": return .yellow
        case "advanced": return .orange
        case "project": return Theme.red
        default: return Theme.textMuted
        }
    }
}

struct StatCard: View {
    let label: String
    let value: String

    var body: some View {
        VStack(spacing: 2) {
            Text(label)
                .font(.caption2)
                .foregroundStyle(Theme.textMuted)
            Text(value)
                .font(.subheadline)
                .fontWeight(.semibold)
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 8)
        .background(Theme.surface)
        .clipShape(RoundedRectangle(cornerRadius: 8))
    }
}

struct SectionHeader: View {
    let title: String
    var body: some View {
        Text(title.uppercased())
            .font(.caption)
            .fontWeight(.semibold)
            .foregroundStyle(Theme.textMuted)
            .tracking(1)
            .padding(.top, 8)
    }
}

struct AddToPlanSheet: View {
    let meal: Meal
    @Environment(\.dismiss) private var dismiss
    @Environment(\.modelContext) private var context
    @State private var dayIndex = 0
    @State private var mealSlot = "dinner"

    private let days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    private let slots = ["breakfast", "lunch", "dinner"]

    var body: some View {
        NavigationStack {
            Form {
                Picker("Day", selection: $dayIndex) {
                    ForEach(0..<7) { i in
                        Text(days[i]).tag(i)
                    }
                }
                Picker("Meal", selection: $mealSlot) {
                    ForEach(slots, id: \.self) { s in
                        Text(s.capitalized).tag(s)
                    }
                }
            }
            .navigationTitle("Add \(meal.name)")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") { dismiss() }
                }
                ToolbarItem(placement: .confirmationAction) {
                    Button("Add") {
                        let entry = PlanEntry(
                            mealId: meal.id, dayIndex: dayIndex,
                            mealSlot: mealSlot, weekStart: currentWeekStart()
                        )
                        context.insert(entry)
                        dismiss()
                    }
                    .fontWeight(.semibold)
                }
            }
        }
        .presentationDetents([.medium])
    }

    private func currentWeekStart() -> Date {
        let cal = Calendar.current
        return cal.dateInterval(of: .weekOfYear, for: .now)?.start ?? .now
    }
}
