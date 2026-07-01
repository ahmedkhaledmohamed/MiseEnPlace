package com.ahmedkhaledmohamed.potluck.data.db

import androidx.room.*

@Entity(tableName = "meals")
data class MealEntity(
    @PrimaryKey val id: String,
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
    val variations: List<String>
)

@Entity(
    tableName = "meal_ingredients",
    foreignKeys = [ForeignKey(
        entity = MealEntity::class,
        parentColumns = ["id"],
        childColumns = ["mealId"],
        onDelete = ForeignKey.CASCADE
    )],
    indices = [Index("mealId")]
)
data class MealIngredientEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val mealId: String,
    val name: String,
    val category: String,
    val quantity: Double,
    val unit: String,
    val isOptional: Boolean,
    val prepNote: String?,
    val cost: Double?
)

@Entity(
    tableName = "recipe_steps",
    foreignKeys = [ForeignKey(
        entity = MealEntity::class,
        parentColumns = ["id"],
        childColumns = ["mealId"],
        onDelete = ForeignKey.CASCADE
    )],
    indices = [Index("mealId")]
)
data class RecipeStepEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val mealId: String,
    @ColumnInfo(name = "step_order") val order: Int,
    val instruction: String,
    val duration: Int?
)

@Entity(tableName = "meal_similarities")
data class MealSimilarityEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val mealAId: String,
    val mealBId: String,
    val sharedCount: Int,
    val overlapRatio: Double,
    val sharedIngredients: List<String>
)

@Entity(tableName = "plan_entries")
data class PlanEntryEntity(
    @PrimaryKey val id: String = java.util.UUID.randomUUID().toString(),
    val mealId: String,
    val dayIndex: Int,
    val mealSlot: String,
    val weekStart: Long
)

@Entity(tableName = "favorite_meals")
data class FavoriteMealEntity(
    @PrimaryKey val mealId: String,
    val createdAt: Long = System.currentTimeMillis()
)

@Entity(tableName = "pantry_items")
data class PantryItemEntity(
    @PrimaryKey val name: String,
    val isStaple: Boolean = true
)
