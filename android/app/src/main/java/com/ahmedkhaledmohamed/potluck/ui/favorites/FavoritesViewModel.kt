package com.ahmedkhaledmohamed.potluck.ui.favorites

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.ahmedkhaledmohamed.potluck.data.db.*
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class FavoritesViewModel @Inject constructor(
    private val mealDao: MealDao,
    private val favoriteDao: FavoriteDao
) : ViewModel() {
    val allMeals: Flow<List<MealEntity>> = mealDao.allMeals()
    val favorites: Flow<List<FavoriteMealEntity>> = favoriteDao.allFavorites()

    fun favoriteMeals(meals: List<MealEntity>, favs: List<FavoriteMealEntity>): List<MealEntity> {
        val favIds = favs.map { it.mealId }.toSet()
        return meals.filter { it.id in favIds }
    }
}
