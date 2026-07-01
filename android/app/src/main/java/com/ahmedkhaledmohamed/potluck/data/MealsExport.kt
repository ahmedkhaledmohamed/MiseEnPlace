package com.ahmedkhaledmohamed.potluck.data

data class MealsExport(
    val meals: List<MealJson>,
    val similarities: List<SimilarityJson>
)

data class MealJson(
    val id: String,
    val name: String,
    val description: String,
    val cuisine: String,
    val mealType: String,
    val difficulty: String,
    val prepTime: Int,
    val cookTime: Int,
    val totalTime: Int,
    val servings: Int,
    val costPerServing: Double,
    val totalCost: Double,
    val sourceInspiration: String,
    val imageUrl: String?,
    val dietaryTags: List<String>,
    val seasons: List<String>,
    val equipment: List<String>,
    val tips: List<String>,
    val variations: List<String>,
    val ingredients: List<IngredientJson>,
    val steps: List<StepJson>
)

data class IngredientJson(
    val name: String,
    val category: String,
    val quantity: Double,
    val unit: String,
    val isOptional: Boolean,
    val prepNote: String?,
    val cost: Double?
)

data class StepJson(
    val order: Int,
    val instruction: String,
    val duration: Int?
)

data class SimilarityJson(
    val mealAId: String,
    val mealBId: String,
    val sharedCount: Int,
    val overlapRatio: Double,
    val sharedIngredients: List<String>
)
