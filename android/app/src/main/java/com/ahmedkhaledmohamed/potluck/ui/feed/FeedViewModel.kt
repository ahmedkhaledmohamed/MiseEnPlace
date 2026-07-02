package com.ahmedkhaledmohamed.potluck.ui.feed

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.ahmedkhaledmohamed.potluck.data.db.*
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import javax.inject.Inject
import kotlin.random.Random

@HiltViewModel
class FeedViewModel @Inject constructor(
    private val mealDao: MealDao,
    private val favoriteDao: FavoriteDao
) : ViewModel() {
    private val _rankedMeals = MutableStateFlow<List<MealEntity>>(emptyList())
    val rankedMeals: StateFlow<List<MealEntity>> = _rankedMeals

    private val _searchText = MutableStateFlow("")
    val searchText: StateFlow<String> = _searchText

    private val _selectedCuisine = MutableStateFlow<String?>(null)
    val selectedCuisine: StateFlow<String?> = _selectedCuisine

    private val _selectedType = MutableStateFlow<String?>(null)
    val selectedType: StateFlow<String?> = _selectedType

    private val _selectedDifficulty = MutableStateFlow<String?>(null)
    val selectedDifficulty: StateFlow<String?> = _selectedDifficulty

    private val _isRefreshing = MutableStateFlow(false)
    val isRefreshing: StateFlow<Boolean> = _isRefreshing

    init { buildFeed() }

    fun buildFeed() {
        viewModelScope.launch {
            _isRefreshing.value = true
            val meals = mealDao.allMealsList()
            val favs = favoriteDao.allFavoritesList()

            val cuisineCounts = favs.groupBy { fav -> meals.find { it.id == fav.mealId }?.cuisine ?: "" }
                .mapValues { it.value.size }
            val typeCounts = favs.groupBy { fav -> meals.find { it.id == fav.mealId }?.mealType ?: "" }
                .mapValues { it.value.size }

            val rng = Random(System.nanoTime())
            val scored = meals.map { meal ->
                val ca = (cuisineCounts[meal.cuisine] ?: 0).toDouble()
                val ta = (typeCounts[meal.mealType] ?: 0).toDouble()
                val jitter = rng.nextDouble() * 0.5
                val score = (ca * 3) + (ta * 2) + jitter
                meal to score
            }

            _rankedMeals.value = scored.sortedByDescending { it.second }.map { it.first }
            _isRefreshing.value = false
        }
    }

    fun setSearchText(text: String) { _searchText.value = text }
    fun setSelectedCuisine(c: String?) { _selectedCuisine.value = c }
    fun setSelectedType(t: String?) { _selectedType.value = t }
    fun setSelectedDifficulty(d: String?) { _selectedDifficulty.value = d }

    fun filteredMeals(meals: List<MealEntity>): List<MealEntity> {
        return meals.filter { meal ->
            val q = _searchText.value.lowercase()
            if (q.isNotEmpty() && !meal.name.lowercase().contains(q) && !meal.cuisine.lowercase().contains(q))
                return@filter false
            _selectedCuisine.value?.let { if (meal.cuisine != it) return@filter false }
            _selectedType.value?.let { if (meal.mealType != it) return@filter false }
            _selectedDifficulty.value?.let { if (meal.difficulty != it) return@filter false }
            true
        }
    }
}
