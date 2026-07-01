package com.ahmedkhaledmohamed.potluck.ui.cook

import androidx.lifecycle.ViewModel
import com.ahmedkhaledmohamed.potluck.data.db.*
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.*
import javax.inject.Inject

data class IngredientInfo(val name: String, val category: String, val count: Int)
data class MealMatch(val meal: MealEntity, val matched: Int, val total: Int, val missing: List<String>)

@HiltViewModel
class PantryViewModel @Inject constructor(
    private val mealDao: MealDao
) : ViewModel() {
    val allMeals: Flow<List<MealEntity>> = mealDao.allMeals()

    private val _selected = MutableStateFlow<Set<String>>(emptySet())
    val selected: StateFlow<Set<String>> = _selected

    private val _search = MutableStateFlow("")
    val search: StateFlow<String> = _search

    fun setSearch(text: String) { _search.value = text }
    fun toggle(ingredient: String) {
        _selected.value = if (ingredient in _selected.value)
            _selected.value - ingredient else _selected.value + ingredient
    }
    fun clear() { _selected.value = emptySet() }
}
