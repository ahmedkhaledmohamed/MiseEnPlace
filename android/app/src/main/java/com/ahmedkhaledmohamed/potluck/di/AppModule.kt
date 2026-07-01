package com.ahmedkhaledmohamed.potluck.di

import android.content.Context
import androidx.room.Room
import com.ahmedkhaledmohamed.potluck.data.db.*
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object AppModule {
    @Provides
    @Singleton
    fun provideDatabase(@ApplicationContext context: Context): AppDatabase =
        Room.databaseBuilder(context, AppDatabase::class.java, "potluck.db")
            .fallbackToDestructiveMigration()
            .build()

    @Provides fun provideMealDao(db: AppDatabase): MealDao = db.mealDao()
    @Provides fun provideSimilarityDao(db: AppDatabase): SimilarityDao = db.similarityDao()
    @Provides fun provideFavoriteDao(db: AppDatabase): FavoriteDao = db.favoriteDao()
    @Provides fun providePlanDao(db: AppDatabase): PlanDao = db.planDao()
    @Provides fun providePantryDao(db: AppDatabase): PantryDao = db.pantryDao()
}
