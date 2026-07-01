package com.ahmedkhaledmohamed.potluck.data

import android.content.Context
import com.ahmedkhaledmohamed.potluck.data.db.*
import com.google.gson.Gson
import dagger.hilt.android.qualifiers.ApplicationContext
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class DataSeeder @Inject constructor(
    @ApplicationContext private val context: Context,
    private val db: AppDatabase
) {
    suspend fun seedIfNeeded() {
        val prefs = context.getSharedPreferences("potluck", Context.MODE_PRIVATE)
        val version = prefs.getInt("dataVersion", 0)
        if (version >= 2 && db.mealDao().count() > 0) return

        val json = context.assets.open("meals.json").bufferedReader().readText()
        val export = Gson().fromJson(json, MealsExport::class.java)

        db.clearAllTables()

        val meals = export.meals.map { m ->
            MealEntity(
                id = m.id, name = m.name, description = m.description,
                cuisine = m.cuisine, mealType = m.mealType, difficulty = m.difficulty,
                prepTime = m.prepTime, cookTime = m.cookTime, totalTime = m.totalTime,
                servings = m.servings, costPerServing = m.costPerServing, totalCost = m.totalCost,
                sourceInspiration = m.sourceInspiration, imageUrl = m.imageUrl,
                dietaryTags = m.dietaryTags, seasons = m.seasons, equipment = m.equipment,
                tips = m.tips, variations = m.variations
            )
        }
        db.mealDao().insertMeals(meals)

        val ingredients = export.meals.flatMap { m ->
            m.ingredients.map { ing ->
                MealIngredientEntity(
                    mealId = m.id, name = ing.name, category = ing.category,
                    quantity = ing.quantity, unit = ing.unit, isOptional = ing.isOptional,
                    prepNote = ing.prepNote, cost = ing.cost
                )
            }
        }
        db.mealDao().insertIngredients(ingredients)

        val steps = export.meals.flatMap { m ->
            m.steps.map { s ->
                RecipeStepEntity(mealId = m.id, order = s.order, instruction = s.instruction, duration = s.duration)
            }
        }
        db.mealDao().insertSteps(steps)

        val similarities = export.similarities.map { s ->
            MealSimilarityEntity(
                mealAId = s.mealAId, mealBId = s.mealBId,
                sharedCount = s.sharedCount, overlapRatio = s.overlapRatio,
                sharedIngredients = s.sharedIngredients
            )
        }
        db.similarityDao().insertAll(similarities)

        prefs.edit().putInt("dataVersion", 2).apply()
    }
}
