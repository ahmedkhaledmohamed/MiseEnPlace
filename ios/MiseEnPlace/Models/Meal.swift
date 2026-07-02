import Foundation
import SwiftData

@Model
final class Meal {
    @Attribute(.unique) var id: String
    var name: String
    var desc: String
    var cuisine: String
    var mealType: String
    var difficulty: String
    var prepTime: Int
    var cookTime: Int
    var totalTime: Int
    var servings: Int
    var costPerServing: Double
    var totalCost: Double
    var sourceInspiration: String
    var imageUrl: String?
    var dietaryTags: [String]
    var seasons: [String]
    var equipment: [String]
    var tips: [String]
    var variations: [String]

    @Relationship(deleteRule: .cascade, inverse: \MealIngredient.meal)
    var ingredients: [MealIngredient]

    @Relationship(deleteRule: .cascade, inverse: \RecipeStep.meal)
    var steps: [RecipeStep]

    init(
        id: String, name: String, desc: String, cuisine: String,
        mealType: String, difficulty: String, prepTime: Int, cookTime: Int,
        totalTime: Int, servings: Int, costPerServing: Double, totalCost: Double,
        sourceInspiration: String, imageUrl: String?,
        dietaryTags: [String], seasons: [String], equipment: [String],
        tips: [String], variations: [String]
    ) {
        self.id = id
        self.name = name
        self.desc = desc
        self.cuisine = cuisine
        self.mealType = mealType
        self.difficulty = difficulty
        self.prepTime = prepTime
        self.cookTime = cookTime
        self.totalTime = totalTime
        self.servings = servings
        self.costPerServing = costPerServing
        self.totalCost = totalCost
        self.sourceInspiration = sourceInspiration
        self.imageUrl = imageUrl
        self.dietaryTags = dietaryTags
        self.seasons = seasons
        self.equipment = equipment
        self.tips = tips
        self.variations = variations
        self.ingredients = []
        self.steps = []
    }
}

@Model
final class MealIngredient {
    var name: String
    var category: String
    var quantity: Double
    var unit: String
    var isOptional: Bool
    var prepNote: String?
    var cost: Double?
    var meal: Meal?

    init(name: String, category: String, quantity: Double, unit: String,
         isOptional: Bool, prepNote: String?, cost: Double?) {
        self.name = name
        self.category = category
        self.quantity = quantity
        self.unit = unit
        self.isOptional = isOptional
        self.prepNote = prepNote
        self.cost = cost
    }
}

@Model
final class RecipeStep {
    var order: Int
    var instruction: String
    var duration: Int?
    var meal: Meal?

    init(order: Int, instruction: String, duration: Int?) {
        self.order = order
        self.instruction = instruction
        self.duration = duration
    }
}

@Model
final class MealSimilarity {
    var mealAId: String
    var mealBId: String
    var sharedCount: Int
    var overlapRatio: Double
    var sharedIngredients: [String]

    init(mealAId: String, mealBId: String, sharedCount: Int,
         overlapRatio: Double, sharedIngredients: [String]) {
        self.mealAId = mealAId
        self.mealBId = mealBId
        self.sharedCount = sharedCount
        self.overlapRatio = overlapRatio
        self.sharedIngredients = sharedIngredients
    }
}

@Model
final class PlanEntry {
    @Attribute(.unique) var id: UUID
    var mealId: String
    var dayIndex: Int
    var mealSlot: String
    var weekStart: Date

    init(mealId: String, dayIndex: Int, mealSlot: String, weekStart: Date) {
        self.id = UUID()
        self.mealId = mealId
        self.dayIndex = dayIndex
        self.mealSlot = mealSlot
        self.weekStart = weekStart
    }
}

@Model
final class SeenMeal {
    @Attribute(.unique) var mealId: String
    var seenAt: Date
    init(mealId: String) {
        self.mealId = mealId
        self.seenAt = .now
    }
}

@Model
final class FavoriteMeal {
    @Attribute(.unique) var mealId: String
    var createdAt: Date

    init(mealId: String) {
        self.mealId = mealId
        self.createdAt = .now
    }
}

@Model
final class PantryItem {
    @Attribute(.unique) var name: String
    var isStaple: Bool

    init(name: String, isStaple: Bool = true) {
        self.name = name
        self.isStaple = isStaple
    }
}
