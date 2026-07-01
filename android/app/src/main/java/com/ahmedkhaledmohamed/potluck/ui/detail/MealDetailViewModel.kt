package com.ahmedkhaledmohamed.potluck.ui.detail

import androidx.lifecycle.SavedStateHandle
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.ahmedkhaledmohamed.potluck.data.db.*
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class MealDetailViewModel @Inject constructor(
    savedStateHandle: SavedStateHandle,
    private val mealDao: MealDao,
    private val similarityDao: SimilarityDao,
    private val favoriteDao: FavoriteDao
) : ViewModel() {
    private val mealId: String = savedStateHandle["mealId"] ?: ""

    val meal: Flow<MealEntity?> = flow { emit(mealDao.getMeal(mealId)) }
    val ingredients: Flow<List<MealIngredientEntity>> = mealDao.ingredientsForMeal(mealId)
    val steps: Flow<List<RecipeStepEntity>> = mealDao.stepsForMeal(mealId)
    val similarities: Flow<List<MealSimilarityEntity>> = similarityDao.similarTo(mealId)
    val isFavorited: Flow<Boolean> = favoriteDao.isFavorited(mealId)

    fun toggleFavorite() {
        viewModelScope.launch {
            val faved = isFavorited.first()
            if (faved) favoriteDao.delete(mealId) else favoriteDao.insert(FavoriteMealEntity(mealId))
        }
    }
}
