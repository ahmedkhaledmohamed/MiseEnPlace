import Foundation
import SwiftData

struct MealSuggestion: Identifiable {
    let id: String
    let meal: Meal
    let sharedIngredients: [String]
    let savings: Double
    let reason: String
}

enum MealSuggestionService {
    static func suggest(
        for plannedMealIds: Set<String>,
        allMeals: [Meal],
        similarities: [MealSimilarity],
        budget: Double,
        currentCost: Double,
        count: Int = 3
    ) -> [MealSuggestion] {
        guard !plannedMealIds.isEmpty else {
            return topBudgetMeals(allMeals: allMeals, budget: budget, count: count)
        }

        let plannedIngredients = Set(
            allMeals
                .filter { plannedMealIds.contains($0.id) }
                .flatMap { $0.ingredients.filter { !$0.isOptional }.map { $0.name.lowercased() } }
        )

        var candidates: [MealSuggestion] = []

        for meal in allMeals where !plannedMealIds.contains(meal.id) {
            let mealIngs = Set(meal.ingredients.filter { !$0.isOptional }.map { $0.name.lowercased() })
            let shared = mealIngs.intersection(plannedIngredients)
            guard shared.count >= 2 else { continue }

            let uniqueNewIngs = mealIngs.subtracting(plannedIngredients)
            let newCost = meal.ingredients
                .filter { uniqueNewIngs.contains($0.name.lowercased()) }
                .compactMap(\.cost)
                .reduce(0, +)

            if currentCost + newCost > budget && budget > 0 { continue }

            let savings = meal.totalCost - newCost
            let reason: String
            if shared.count >= 4 {
                reason = "Shares \(shared.count) ingredients — only \(uniqueNewIngs.count) new to buy"
            } else {
                let sharedList = Array(shared).prefix(3).joined(separator: ", ")
                reason = "Uses \(sharedList) you're already buying"
            }

            candidates.append(MealSuggestion(
                id: meal.id,
                meal: meal,
                sharedIngredients: Array(shared).sorted(),
                savings: savings,
                reason: reason
            ))
        }

        return Array(candidates.sorted { $0.sharedIngredients.count > $1.sharedIngredients.count }.prefix(count))
    }

    private static func topBudgetMeals(allMeals: [Meal], budget: Double, count: Int) -> [MealSuggestion] {
        allMeals
            .sorted { $0.costPerServing < $1.costPerServing }
            .prefix(count)
            .map { meal in
                MealSuggestion(
                    id: meal.id, meal: meal,
                    sharedIngredients: [],
                    savings: 0,
                    reason: "Budget-friendly at $\(String(format: "%.2f", meal.costPerServing))/serving"
                )
            }
    }
}
