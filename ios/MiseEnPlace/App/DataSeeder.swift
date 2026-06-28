import Foundation
import SwiftData

struct MealsExport: Codable {
    let meals: [MealJSON]
    let similarities: [SimilarityJSON]
}

struct MealJSON: Codable {
    let id: String
    let name: String
    let description: String
    let cuisine: String
    let mealType: String
    let difficulty: String
    let prepTime: Int
    let cookTime: Int
    let totalTime: Int
    let servings: Int
    let costPerServing: Double
    let totalCost: Double
    let sourceInspiration: String
    let imageName: String?
    let dietaryTags: [String]
    let seasons: [String]
    let equipment: [String]
    let tips: [String]
    let variations: [String]
    let ingredients: [IngredientJSON]
    let steps: [StepJSON]
}

struct IngredientJSON: Codable {
    let name: String
    let category: String
    let quantity: Double
    let unit: String
    let isOptional: Bool
    let prepNote: String?
    let cost: Double?
}

struct StepJSON: Codable {
    let order: Int
    let instruction: String
    let duration: Int?
}

struct SimilarityJSON: Codable {
    let mealAId: String
    let mealBId: String
    let sharedCount: Int
    let overlapRatio: Double
    let sharedIngredients: [String]
}

enum DataSeeder {
    static func seedIfNeeded(context: ModelContext) {
        let count = (try? context.fetchCount(FetchDescriptor<Meal>())) ?? 0
        guard count == 0 else { return }

        guard let url = Bundle.main.url(forResource: "meals", withExtension: "json"),
              let data = try? Data(contentsOf: url),
              let export = try? JSONDecoder().decode(MealsExport.self, from: data)
        else {
            print("[DataSeeder] Failed to load meals.json")
            return
        }

        for mealJSON in export.meals {
            let meal = Meal(
                id: mealJSON.id,
                name: mealJSON.name,
                desc: mealJSON.description,
                cuisine: mealJSON.cuisine,
                mealType: mealJSON.mealType,
                difficulty: mealJSON.difficulty,
                prepTime: mealJSON.prepTime,
                cookTime: mealJSON.cookTime,
                totalTime: mealJSON.totalTime,
                servings: mealJSON.servings,
                costPerServing: mealJSON.costPerServing,
                totalCost: mealJSON.totalCost,
                sourceInspiration: mealJSON.sourceInspiration,
                imageName: mealJSON.imageName,
                dietaryTags: mealJSON.dietaryTags,
                seasons: mealJSON.seasons,
                equipment: mealJSON.equipment,
                tips: mealJSON.tips,
                variations: mealJSON.variations
            )
            context.insert(meal)

            for ing in mealJSON.ingredients {
                let ingredient = MealIngredient(
                    name: ing.name, category: ing.category,
                    quantity: ing.quantity, unit: ing.unit,
                    isOptional: ing.isOptional, prepNote: ing.prepNote,
                    cost: ing.cost
                )
                ingredient.meal = meal
                context.insert(ingredient)
            }

            for step in mealJSON.steps {
                let recipeStep = RecipeStep(
                    order: step.order, instruction: step.instruction,
                    duration: step.duration
                )
                recipeStep.meal = meal
                context.insert(recipeStep)
            }
        }

        for sim in export.similarities {
            let similarity = MealSimilarity(
                mealAId: sim.mealAId, mealBId: sim.mealBId,
                sharedCount: sim.sharedCount, overlapRatio: sim.overlapRatio,
                sharedIngredients: sim.sharedIngredients
            )
            context.insert(similarity)
        }

        try? context.save()
        print("[DataSeeder] Seeded \(export.meals.count) meals, \(export.similarities.count) similarities")
    }
}
