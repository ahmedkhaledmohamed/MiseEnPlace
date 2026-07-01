package com.ahmedkhaledmohamed.potluck.data.db

import androidx.room.Database
import androidx.room.RoomDatabase
import androidx.room.TypeConverters

@Database(
    entities = [
        MealEntity::class,
        MealIngredientEntity::class,
        RecipeStepEntity::class,
        MealSimilarityEntity::class,
        PlanEntryEntity::class,
        FavoriteMealEntity::class,
        PantryItemEntity::class,
    ],
    version = 1,
    exportSchema = false
)
@TypeConverters(Converters::class)
abstract class AppDatabase : RoomDatabase() {
    abstract fun mealDao(): MealDao
    abstract fun similarityDao(): SimilarityDao
    abstract fun favoriteDao(): FavoriteDao
    abstract fun planDao(): PlanDao
    abstract fun pantryDao(): PantryDao
}
