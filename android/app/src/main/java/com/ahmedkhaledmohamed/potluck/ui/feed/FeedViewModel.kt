package com.ahmedkhaledmohamed.potluck.ui.feed

import androidx.lifecycle.ViewModel
import com.ahmedkhaledmohamed.potluck.data.db.MealDao
import com.ahmedkhaledmohamed.potluck.data.db.MealEntity
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.*
import javax.inject.Inject

@HiltViewModel
class FeedViewModel @Inject constructor(
    private val mealDao: MealDao
) : ViewModel() {
    val allMeals: Flow<List<MealEntity>> = mealDao.allMeals()

    private val _searchText = MutableStateFlow("")
    val searchText: StateFlow<String> = _searchText

    private val _selectedCuisine = MutableStateFlow<String?>(null)
    val selectedCuisine: StateFlow<String?> = _selectedCuisine

    private val _selectedType = MutableStateFlow<String?>(null)
    val selectedType: StateFlow<String?> = _selectedType

    private val _selectedDifficulty = MutableStateFlow<String?>(null)
    val selectedDifficulty: StateFlow<String?> = _selectedDifficulty

    fun setSearchText(text: String) { _searchText.value = text }
    fun setSelectedCuisine(c: String?) { _selectedCuisine.value = c }
    fun setSelectedType(t: String?) { _selectedType.value = t }
    fun setSelectedDifficulty(d: String?) { _selectedDifficulty.value = d }

    fun filteredMeals(meals: List<MealEntity>): List<MealEntity> {
        return meals.filter { meal ->
            val q = _searchText.value.lowercase()
            if (q.isNotEmpty()) {
                if (!meal.name.lowercase().contains(q) && !meal.cuisine.lowercase().contains(q)) return@filter false
            }
            _selectedCuisine.value?.let { if (meal.cuisine != it) return@filter false }
            _selectedType.value?.let { if (meal.mealType != it) return@filter false }
            _selectedDifficulty.value?.let { if (meal.difficulty != it) return@filter false }
            true
        }
    }
}
