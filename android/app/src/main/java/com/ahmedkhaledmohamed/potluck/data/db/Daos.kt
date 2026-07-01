package com.ahmedkhaledmohamed.potluck.data.db

import androidx.room.*
import kotlinx.coroutines.flow.Flow

@Dao
interface MealDao {
    @Query("SELECT * FROM meals ORDER BY name")
    fun allMeals(): Flow<List<MealEntity>>

    @Query("SELECT * FROM meals WHERE id = :id")
    suspend fun getMeal(id: String): MealEntity?

    @Query("SELECT COUNT(*) FROM meals")
    suspend fun count(): Int

    @Query("SELECT * FROM meal_ingredients WHERE mealId = :mealId")
    fun ingredientsForMeal(mealId: String): Flow<List<MealIngredientEntity>>

    @Query("SELECT * FROM recipe_steps WHERE mealId = :mealId ORDER BY step_order")
    fun stepsForMeal(mealId: String): Flow<List<RecipeStepEntity>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertMeals(meals: List<MealEntity>)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertIngredients(ingredients: List<MealIngredientEntity>)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertSteps(steps: List<RecipeStepEntity>)
}

@Dao
interface SimilarityDao {
    @Query("SELECT * FROM meal_similarities WHERE mealAId = :id OR mealBId = :id ORDER BY overlapRatio DESC LIMIT 8")
    fun similarTo(id: String): Flow<List<MealSimilarityEntity>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(similarities: List<MealSimilarityEntity>)
}

@Dao
interface FavoriteDao {
    @Query("SELECT * FROM favorite_meals ORDER BY createdAt DESC")
    fun allFavorites(): Flow<List<FavoriteMealEntity>>

    @Query("SELECT EXISTS(SELECT 1 FROM favorite_meals WHERE mealId = :mealId)")
    fun isFavorited(mealId: String): Flow<Boolean>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(fav: FavoriteMealEntity)

    @Query("DELETE FROM favorite_meals WHERE mealId = :mealId")
    suspend fun delete(mealId: String)
}

@Dao
interface PlanDao {
    @Query("SELECT * FROM plan_entries WHERE weekStart = :weekStart")
    fun entriesForWeek(weekStart: Long): Flow<List<PlanEntryEntity>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(entry: PlanEntryEntity)

    @Query("DELETE FROM plan_entries WHERE id = :id")
    suspend fun delete(id: String)

    @Query("DELETE FROM plan_entries WHERE weekStart = :weekStart")
    suspend fun clearWeek(weekStart: Long)
}

@Dao
interface PantryDao {
    @Query("SELECT * FROM pantry_items")
    fun allItems(): Flow<List<PantryItemEntity>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(item: PantryItemEntity)

    @Query("DELETE FROM pantry_items WHERE name = :name")
    suspend fun delete(name: String)
}
